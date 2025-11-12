suppressPackageStartupMessages({
  library(rpart)
})

set.seed(123) # Reproducibilidad

# ============================================================
# a) Folds estratificados por la clase
# ============================================================
create_stratified_folds <- function(y, k = 10) {
  if (!is.factor(y)) stop("Para estratificar, 'y' debe ser factor.")
  n <- length(y)
  folds <- vector("list", k)
  for (lvl in levels(y)) {
    idx <- which(y == lvl)
    idx <- sample(idx, length(idx), replace = FALSE)
    parts <- split(idx, cut(seq_along(idx), breaks = k, labels = FALSE))
    for (i in seq_len(k)) {
      folds[[i]] <- c(folds[[i]], parts[[i]])
    }
  }
  folds <- lapply(folds, function(ix) sort(unique(ix)))
  folds
}

# ============================================================
# b) Validación cruzada con optimizaciones
# ============================================================
cross_validation <- function(dataframe, k = 10, 
                             target_col = "inclinacion_peligrosa",
                             formula_vars = c("altura", "circ_tronco_cm", 
                                              "lat", "long", "seccion", "especie")) {
  
  # --- Validaciones y normalización de nombres ---
  if (!is.data.frame(dataframe)) stop("El primer argumento debe ser un dataframe")
  names(dataframe) <- tolower(names(dataframe))
  target_col <- tolower(target_col)
  formula_vars <- tolower(formula_vars)
  if (!target_col %in% names(dataframe)) stop(paste("La columna", target_col, "no existe."))
  missing_vars <- formula_vars[!formula_vars %in% names(dataframe)]
  if (length(missing_vars) > 0) stop(paste("Variables no encontradas:", paste(missing_vars, collapse = ", ")))
  cols_to_check <- c(target_col, formula_vars)
  
  # --- Limpieza ligera de strings ---
  for (v in cols_to_check) {
    if (is.character(dataframe[[v]]) || is.factor(dataframe[[v]])) {
      x <- as.character(dataframe[[v]])
      x <- trimws(x)
      x <- gsub("\\s+", " ", x)
      dataframe[[v]] <- x
    }
  }
  
  # --- Remover filas con NA en columnas relevantes ---
  complete_rows <- complete.cases(dataframe[, cols_to_check])
  dataframe_clean <- dataframe[complete_rows, ]
  
  cat("Filas originales:", nrow(dataframe), "\n")
  cat("Filas con datos completos:", nrow(dataframe_clean), "\n")
  cat("Filas removidas por NA:", nrow(dataframe) - nrow(dataframe_clean), "\n\n")
  
  # --- Forzar target a factor binario coherente ---
  y_raw <- dataframe_clean[[target_col]]
  if (is.numeric(y_raw)) {
    uniq <- sort(unique(y_raw))
    if (all(uniq %in% c(0, 1))) {
      dataframe_clean[[target_col]] <- factor(ifelse(y_raw == 1, "1", "0"), levels = c("0","1"))
    } else {
      stop("El target numérico no es binario 0/1. Ajusta la conversión.")
    }
  } else {
    y_chr <- as.character(y_raw)
    uniq <- sort(unique(y_chr))
    if (all(uniq %in% c("0","1"))) {
      dataframe_clean[[target_col]] <- factor(y_chr, levels = c("0","1"))
    } else {
      lvls <- sort(unique(y_chr))
      cat("Aviso: target con niveles distintos de '0/1':", paste(lvls, collapse=", "), "\n")
      dataframe_clean[[target_col]] <- factor(y_chr, levels = lvls)
    }
  }
  
  # --- Factorizar categóricas y fijar niveles globales (incluye target) ---
  cat_cols <- cols_to_check[sapply(dataframe_clean[, cols_to_check, drop = FALSE],
                                   function(x) is.character(x) || is.factor(x))]
  for (v in cat_cols) dataframe_clean[[v]] <- factor(dataframe_clean[[v]])
  global_levels <- lapply(dataframe_clean[, cat_cols, drop = FALSE], levels)
  
  # --- Crear folds estratificados por target ---
  cat("Creando", k, "folds estratificados por", target_col, "...\n")
  folds <- create_stratified_folds(dataframe_clean[[target_col]], k)
  
  # --- Fórmula para el árbol ---
  formula_str <- paste(target_col, "~", paste(formula_vars, collapse = " + "))
  train_formula <- as.formula(formula_str)
  cat("Fórmula:", formula_str, "\n\n")
  
  # --- DataFrame de resultados ---
  results <- data.frame(
    Fold = integer(),
    N_train = integer(),
    N_test = integer(),
    TP = integer(),
    TN = integer(),
    FP = integer(),
    FN = integer(),
    Accuracy = numeric(),
    Precision = numeric(),
    Sensitivity = numeric(),
    Specificity = numeric(),
    stringsAsFactors = FALSE
  )
  
  # --- Aux: valor seguro desde tabla ---
  get_cm_val <- function(cm, r, p) {
    if (!is.null(dim(cm)) && r %in% rownames(cm) && p %in% colnames(cm))
      as.integer(cm[r, p]) else 0L
  }
  
  # --- Iteración por folds ---
  for (i in seq_len(k)) {
    cat("=== Fold", i, "de", k, "===\n")
    
    test_indices  <- folds[[i]]
    train_indices <- setdiff(seq_len(nrow(dataframe_clean)), test_indices)
    
    data_train <- dataframe_clean[train_indices, , drop = FALSE]
    data_test  <- dataframe_clean[test_indices,  , drop = FALSE]
    
    # Reimponer niveles de factores iguales en train y test
    for (v in cat_cols) {
      lv <- global_levels[[v]]
      data_train[[v]] <- factor(data_train[[v]], levels = lv)
      data_test[[v]]  <- factor(data_test[[v]],  levels = lv)
    }
    
    cat("  Train:", nrow(data_train), "muestras | Test:", nrow(data_test), "muestras\n")
    
    # Definir clase positiva/negativa según niveles del train
    tr_levels <- levels(data_train[[target_col]])
    if (all(c("0","1") %in% tr_levels)) {
      neg <- "0"; pos <- "1"
    } else {
      if (length(tr_levels) != 2) stop("El target no es binario.")
      neg <- tr_levels[1]; pos <- tr_levels[2]
      cat("Aviso: usando '", pos, "' como clase positiva.\n", sep = "")
    }
    
    # --- ENTRENAR: rpart con costos/prior y control ---
    ctrl <- rpart.control(minsplit = 20, minbucket = 7, cp = 0.0005, maxdepth = 30)
    tree_model <- rpart(
      train_formula, data = data_train, method = "class",
      control = ctrl,
      parms = list(
        prior = c(0.4, 0.6),                  # ajustable
        loss  = matrix(c(0, 1, 5, 0), 2, 2, byrow = TRUE) # penaliza FN>FP
      )
    )
    
    # --- UMBRAL: elegir por F1 en train ---
    p_train <- predict(tree_model, data_train, type = "prob")[, pos]
    y_train <- data_train[[target_col]]
    ths <- seq(0.05, 0.95, by = 0.01)
    best_th <- 0.5; best_f1 <- -Inf
    for (th in ths) {
      pred_tr <- factor(ifelse(p_train >= th, pos, neg), levels = c(neg, pos))
      cm_tr <- table(Real = y_train, Pred = pred_tr)
      TP_tr <- get_cm_val(cm_tr, pos, pos)
      FP_tr <- get_cm_val(cm_tr, neg, pos)
      FN_tr <- get_cm_val(cm_tr, pos, neg)
      prec <- ifelse(TP_tr + FP_tr > 0, TP_tr / (TP_tr + FP_tr), 0)
      rec  <- ifelse(TP_tr + FN_tr > 0, TP_tr / (TP_tr + FN_tr), 0)
      f1   <- ifelse(prec + rec > 0, 2 * prec * rec / (prec + rec), 0)
      if (f1 > best_f1) { best_f1 <- f1; best_th <- th }
    }
    
    # --- PREDICCIÓN en test con umbral elegido ---
    p_test <- predict(tree_model, data_test, type = "prob")[, pos]
    pred_class <- factor(ifelse(p_test >= best_th, pos, neg), levels = c(neg, pos))
    y_test <- factor(data_test[[target_col]], levels = c(neg, pos))
    
    # --- Métricas ---
    cm <- table(Real = y_test, Pred = pred_class)
    TP <- get_cm_val(cm, pos, pos)
    TN <- get_cm_val(cm, neg, neg)
    FP <- get_cm_val(cm, neg, pos)
    FN <- get_cm_val(cm, pos, neg)
    
    total <- TP + TN + FP + FN
    accuracy    <- ifelse(total > 0, (TP + TN) / total, NA_real_)
    precision   <- ifelse((TP + FP) > 0, TP / (TP + FP), NA_real_)
    sensitivity <- ifelse((TP + FN) > 0, TP / (TP + FN), NA_real_)
    specificity <- ifelse((TN + FP) > 0, TN / (TN + FP), NA_real_)
    
    cat("  Umbral elegido (train, F1):", round(best_th, 3), " | F1_train:", round(best_f1, 3), "\n")
    cat("  TP:", TP, "| TN:", TN, "| FP:", FP, "| FN:", FN, "\n")
    cat("  Accuracy:", round(accuracy, 4), 
        "| Precision:", ifelse(is.na(precision), "NA", round(precision, 4)),
        "| Sensitivity:", ifelse(is.na(sensitivity), "NA", round(sensitivity, 4)),
        "| Specificity:", ifelse(is.na(specificity), "NA", round(specificity, 4)), "\n\n")
    
    results <- rbind(results, data.frame(
      Fold = i, N_train = nrow(data_train), N_test = nrow(data_test),
      TP = TP, TN = TN, FP = FP, FN = FN,
      Accuracy = accuracy,
      Precision = precision,
      Sensitivity = sensitivity,
      Specificity = specificity,
      stringsAsFactors = FALSE
    ))
  }
  
  # --- Resumen final ---
  cat("=================================================\n")
  cat("RESULTADOS FINALES (", k, "-Fold Cross Validation)\n", sep = "")
  cat("=================================================\n\n")
  
  metrics <- c("Accuracy", "Precision", "Sensitivity", "Specificity")
  summary_stats <- data.frame(
    Metric = metrics,
    Mean = numeric(length(metrics)),
    SD   = numeric(length(metrics)),
    stringsAsFactors = FALSE
  )
  
  for (i in seq_along(metrics)) {
    m <- metrics[i]
    vals <- results[[m]]
    summary_stats$Mean[i] <- mean(vals, na.rm = TRUE)
    summary_stats$SD[i]   <- sd(vals,  na.rm = TRUE)
    cat(sprintf("%-12s: Media = %.4f | SD = %.4f\n", m, summary_stats$Mean[i], summary_stats$SD[i]))
  }
  cat("\n")
  
  list(fold_results = results, summary = summary_stats, folds = folds)
}

# ============================================================
# EJECUCIÓN CON DATOS REALES
# ============================================================
df <- read.csv("arbolado-mendoza-dataset-train.csv")
cv_results <- cross_validation(df, k = 10)

write.csv(cv_results$fold_results, "cv_fold_results.csv", row.names = FALSE)
write.csv(cv_results$summary,     "cv_summary.csv",     row.names = FALSE)

# ============================================================
# GRÁFICOS (con fixes de NA/SD=0)
# ============================================================
fold_res <- cv_results$fold_results
avg_TP <- mean(fold_res$TP)
avg_TN <- mean(fold_res$TN)
avg_FP <- mean(fold_res$FP)
avg_FN <- mean(fold_res$FN)

png("cv_results_plot.png", width = 1400, height = 700, res = 100)
par(mfrow = c(1, 2), mar = c(5, 5, 4, 2))

metrics_data <- cv_results$summary
colores <- c("#3498db", "#e74c3c", "#2ecc71", "#f39c12")

# Limpiar NaN/NA para ploteo
metrics_data$Mean[!is.finite(metrics_data$Mean)] <- NA
metrics_data$SD[!is.finite(metrics_data$SD)] <- NA
metrics_data$Mean[is.na(metrics_data$Mean)] <- 0
metrics_data$SD[is.na(metrics_data$SD)]   <- 0

bp <- barplot(metrics_data$Mean, 
              names.arg = metrics_data$Metric,
              ylim = c(0, 1.15),
              col = colores,
              main = "Métricas Promedio (10-Fold Cross Validation)",
              ylab = "Valor",
              las = 2,
              cex.names = 1.1,
              cex.axis = 1.1,
              cex.lab = 1.2,
              cex.main = 1.3,
              border = "black",
              lwd = 2)

idx <- which(metrics_data$SD > 0)
if (length(idx) > 0) {
  arrows(x0 = bp[idx],
         y0 = metrics_data$Mean[idx] - metrics_data$SD[idx],
         x1 = bp[idx],
         y1 = metrics_data$Mean[idx] + metrics_data$SD[idx],
         angle = 90, code = 3, length = 0.1, lwd = 2)
}

text(x = bp,
     y = metrics_data$Mean + metrics_data$SD + 0.08,
     labels = sprintf("%.3f\n±%.3f", metrics_data$Mean, metrics_data$SD),
     pos = 3, cex = 1, font = 2)

abline(h = 0.5, col = "red", lty = 2, lwd = 2)
text(0.5, 0.52, "Baseline (0.5)", pos = 4, col = "red", cex = 0.9)

# ===== MATRIZ DE CONFUSIÓN PROMEDIO =====
plot(1, type = "n", xlim = c(0, 3), ylim = c(0, 3.5), 
     xlab = "", ylab = "", main = "Matriz de Confusión Promedio",
     axes = FALSE, cex.main = 1.3)

rect(0.5, 1.5, 1.5, 2.5, col = "#d5f4e6", border = "black", lwd = 3)
rect(1.5, 1.5, 2.5, 2.5, col = "#ffeaa7", border = "black", lwd = 3)
rect(0.5, 0.5, 1.5, 1.5, col = "#ffeaa7", border = "black", lwd = 3)
rect(1.5, 0.5, 2.5, 1.5, col = "#d5f4e6", border = "black", lwd = 3)

text(1, 2, sprintf("TN\n%.1f", avg_TN), cex = 1.8, font = 2)
text(2, 2, sprintf("FP\n%.1f", avg_FP), cex = 1.8, font = 2)
text(1, 1, sprintf("FN\n%.1f", avg_FN), cex = 1.8, font = 2)
text(2, 1, sprintf("TP\n%.1f", avg_TP), cex = 1.8, font = 2)

text(0.2, 2, "0", cex = 1.4, font = 2)
text(0.2, 1, "1", cex = 1.4, font = 2)
text(0.2, 1.5, "Predicción", cex = 1.2, srt = 90, font = 3, pos = 2)

text(1, 2.8, "0", cex = 1.4, font = 2)
text(2, 2.8, "1", cex = 1.4, font = 2)
text(1.5, 3.2, "Real", cex = 1.2, font = 3)

total_samples <- avg_TP + avg_TN + avg_FP + avg_FN
text(1.5, 0.1, sprintf("Total muestras promedio: %.0f por fold", total_samples), cex = 1, font = 3)

dev.off()

cat("\n✅ Resultados guardados en:\n")
cat("   - cv_fold_results.csv (resultados por fold)\n")
cat("   - cv_summary.csv (media y desviación estándar)\n")
cat("   - cv_results_plot.png (gráfico con matriz y métricas)\n")

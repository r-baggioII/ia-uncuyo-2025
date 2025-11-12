suppressPackageStartupMessages({
  library(ggplot2)
})

# -------- helpers ----------
leer_csv_robusto <- function(path) {
  if (!file.exists(path)) stop("No se encuentra '", path, "' en: ", getwd())
  df <- tryCatch(
    read.csv(path, stringsAsFactors = FALSE, check.names = FALSE, fileEncoding = "UTF-8"),
    error = function(e) NULL
  )
  if (!is.null(df) && ncol(df) > 1) return(df)
  df <- tryCatch(
    read.csv(path, stringsAsFactors = FALSE, check.names = FALSE,
             sep = ";", dec = ",", fileEncoding = "UTF-8"),
    error = function(e) NULL
  )
  if (is.null(df)) stop("No se pudo leer el CSV (revisa separador/encoding).")
  df
}

map_01_strict <- function(x, colname="(desconocida)") {
  if (is.logical(x)) return(as.integer(x))
  if (is.numeric(x)) return(ifelse(is.na(x), NA_integer_, ifelse(x >= 1, 1L, 0L)))
  if (is.character(x)) {
    xl <- tolower(trimws(x))
    out <- rep(NA_integer_, length(xl))
    out[xl %in% c("1","true","t","yes","si","sí")] <- 1L
    out[xl %in% c("0","false","f","no")] <- 0L
    if (any(is.na(out) & !is.na(xl))) {
      bad <- unique(xl[is.na(out) & !is.na(xl)])
      stop(sprintf("Valores no reconocidos en '%s': %s", colname, paste(bad, collapse=", ")))
    }
    return(out)
  }
  stop(sprintf("Tipo no manejado en '%s'", colname))
}

confusion_counts <- function(y_true, y_pred) {
  ok <- !is.na(y_true) & !is.na(y_pred)
  yt <- as.integer(y_true[ok])
  yp <- as.integer(y_pred[ok])
  TP <- sum(yt == 1 & yp == 1)
  TN <- sum(yt == 0 & yp == 0)
  FP <- sum(yt == 0 & yp == 1)
  FN <- sum(yt == 1 & yp == 0)
  list(TP=TP, TN=TN, FP=FP, FN=FN, N=length(yt))
}

accuracy    <- function(TP, TN, FP, FN) (TP + TN) / (TP + TN + FP + FN)
precision   <- function(TP, TN, FP, FN) ifelse((TP + FP) > 0, TP / (TP + FP), NA_real_)
sensitivity <- function(TP, TN, FP, FN) ifelse((TP + FN) > 0, TP / (TP + FN), NA_real_)
specificity <- function(TP, TN, FP, FN) ifelse((TN + FP) > 0, TN / (TN + FP), NA_real_)

compute_metrics_from_csv <- function(path, truth_col="inclinacion_peligrosa",
                                     pred_col="prediction_class", model_name) {
  df <- leer_csv_robusto(path)
  stopifnot(truth_col %in% names(df), pred_col %in% names(df))
  y_true <- map_01_strict(df[[truth_col]], truth_col)
  y_pred <- map_01_strict(df[[pred_col]],  pred_col)
  cc <- confusion_counts(y_true, y_pred)
  acc <- accuracy(cc$TP, cc$TN, cc$FP, cc$FN)
  pre <- precision(cc$TP, cc$TN, cc$FP, cc$FN)
  sen <- sensitivity(cc$TP, cc$TN, cc$FP, cc$FN)
  spe <- specificity(cc$TP, cc$TN, cc$FP, cc$FN)
  
  # PRINT — estos son los "valores de referencia"
  cat("\n=== ", model_name, " ===\n", sep = "")
  cat(sprintf("N=%d | TP=%d TN=%d FP=%d FN=%d\n", cc$N, cc$TP, cc$TN, cc$FP, cc$FN))
  cat(sprintf("Accuracy=%.4f  Precision=%s  Sensitivity=%.4f  Specificity=%.4f\n",
              acc,
              ifelse(is.na(pre), "NA", sprintf("%.4f", pre)),
              sen, spe))
  
  # Devolvemos exactamente lo impreso
  data.frame(
    model = model_name, N = cc$N,
    TP = cc$TP, TN = cc$TN, FP = cc$FP, FN = cc$FN,
    Accuracy = acc, Precision = pre, Sensitivity = sen, Specificity = spe,
    stringsAsFactors = FALSE
  )
}

# -------- rutas de CSV --------
path_random   <- "arbolado-mendoza-dataset-validation-with-preds.csv"
path_majority <- "arbolado-mendoza-dataset-validation-with-majority.csv"

# -------- cálculo EXACTO --------
res_random   <- compute_metrics_from_csv(path_random,   model_name = "Random (0.5)")
res_majority <- compute_metrics_from_csv(path_majority, model_name = "Mayoritaria")
summary_df   <- rbind(res_random, res_majority)

# Guardamos también como auditoría
write.csv(summary_df, "metrics_summary.csv", row.names = FALSE)

# -------- plot construido DESDE summary_df (CORREGIDO) --------
metric_names <- c("Accuracy","Precision","Sensitivity","Specificity")

# CORRECCIÓN: Construir plot_df fila por fila para cada modelo
plot_df <- rbind(
  data.frame(
    model = "Random (0.5)",
    metric = metric_names,
    value = c(res_random$Accuracy, res_random$Precision, 
              res_random$Sensitivity, res_random$Specificity),
    stringsAsFactors = FALSE
  ),
  data.frame(
    model = "Mayoritaria",
    metric = metric_names,
    value = c(res_majority$Accuracy, res_majority$Precision, 
              res_majority$Sensitivity, res_majority$Specificity),
    stringsAsFactors = FALSE
  )
)

# Convertimos NAs a 0 para la altura, pero la etiqueta muestra "NA"
plot_df$value_plot <- ifelse(is.na(plot_df$value), 0, plot_df$value)
plot_df$label_plot <- ifelse(is.na(plot_df$value), "NA", sprintf("%.4f", plot_df$value))

# Orden fijo de métricas y modelos para evitar reordenamientos "raros"
plot_df$metric <- factor(plot_df$metric, levels = metric_names)
plot_df$model  <- factor(plot_df$model,  levels = c("Random (0.5)", "Mayoritaria"))

p <- ggplot(plot_df, aes(x = metric, y = value_plot, fill = model)) +
  geom_col(position = position_dodge(width = 0.7), width = 0.6) +
  geom_text(aes(label = label_plot),
            position = position_dodge(width = 0.7),
            vjust = -0.35, size = 3.8) +
  coord_cartesian(ylim = c(0, 1)) +  # evita recortes por labels
  scale_y_continuous(expand = expansion(mult = c(0.02, 0.08))) +
  labs(
    title = "Métricas por modelo (desde los CSV)",
    subtitle = "Valores del gráfico = valores impresos.",
    x = "Métrica", y = "Valor (0-1)", fill = "Modelo",
    caption = "Precision puede ser NA si el modelo no predice positivos (TP+FP=0)."
  ) +
  theme_minimal(base_size = 12) +
  theme(
    plot.title = element_text(face = "bold"),
    panel.grid.minor = element_blank()
  )

print(p)

# Nombre con timestamp para evitar ver una imagen vieja en caché
ts <- format(Sys.time(), "%Y%m%d-%H%M%S")
outfile <- sprintf("metrics_by_model_exact_%s.png", ts)
ggsave(outfile, p, width = 9, height = 5.5, dpi = 150)

# Además guardamos el dataset que alimenta el gráfico
write.csv(plot_df, "plot_df_exact.csv", row.names = FALSE)

cat("\n✅ Gráfico guardado como '", outfile, "'\n", sep = "")
cat("🧾 Tablas guardadas: metrics_summary.csv, plot_df_exact.csv\n")
cat("\n📊 Verificación de datos del gráfico:\n")
print(plot_df[, c("model", "metric", "value")])
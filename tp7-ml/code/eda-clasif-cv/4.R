suppressPackageStartupMessages({
  library(dplyr)
  library(ggplot2)
})

set.seed(123)

# --- Helper: lectura robusta (coma o ';') ---
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

# --- (a) Agrega probabilidad aleatoria U(0,1) ---
add_prediction_prob <- function(df) {
  df$prediction_prob <- runif(nrow(df))
  df
}

# --- (b) Clasificador aleatorio por umbral 0.5 ---
random_classifier <- function(df) {
  if (!"prediction_prob" %in% names(df)) {
    stop("Falta 'prediction_prob'. Ejecuta add_prediction_prob(df) primero.")
  }
  df$prediction_class <- ifelse(df$prediction_prob > 0.5, 1L, 0L)
  df
}

# --- Helper: convertir verdad a 0/1 de forma robusta ---
to_binary01 <- function(x) {
  if (is.logical(x)) return(as.integer(x))
  if (is.numeric(x)) return(as.integer(x > 0))
  if (is.character(x)) {
    xl <- tolower(trimws(x))
    return(as.integer(xl %in% c("1","true","t","yes","si","sí")))
  }
  stop("Tipo no manejado para la columna de verdad.")
}

# =========================
# (c) Cargar validación y aplicar clasificador
# =========================
val_path <- "arbolado-mendoza-dataset-validation.csv"
df_val <- leer_csv_robusto(val_path)

if (!"inclinacion_peligrosa" %in% names(df_val)) {
  stop("No se encontró la columna 'inclinacion_peligrosa' en el dataset de validación.")
}

df_val <- df_val %>% add_prediction_prob() %>% random_classifier()

# Guardar CSV clasificado
write.csv(df_val, "arbolado-mendoza-dataset-validation-with-preds.csv", row.names = FALSE)

# =========================
# (d) TP, TN, FP, FN y matriz de confusión
# =========================
y_true_all <- to_binary01(df_val$inclinacion_peligrosa)
y_pred_all <- as.integer(df_val$prediction_class)

ok <- !is.na(y_true_all) & !is.na(y_pred_all)
y_true <- y_true_all[ok]
y_pred <- y_pred_all[ok]

TP <- sum(y_true == 1 & y_pred == 1)
TN <- sum(y_true == 0 & y_pred == 0)
FP <- sum(y_true == 0 & y_pred == 1)
FN <- sum(y_true == 1 & y_pred == 0)

accuracy  <- (TP + TN) / (TP + TN + FP + FN)
precision <- ifelse((TP + FP) > 0, TP / (TP + FP), NA_real_)
recall    <- ifelse((TP + FN) > 0, TP / (TP + FN), NA_real_)

# Data para heatmap 2x2
cm_df <- data.frame(
  Actual   = factor(c("1 (Peligroso)", "1 (Peligroso)", "0 (No peligroso)", "0 (No peligroso)"),
                    levels = c("1 (Peligroso)", "0 (No peligroso)")),
  Predicho = factor(c("Pred=1", "Pred=0", "Pred=1", "Pred=0"),
                    levels = c("Pred=1", "Pred=0")),
  Conteo   = c(TP, FN, FP, TN)
)

# Texto de métricas para título/subtítulo/caption
fmt <- function(x) ifelse(is.na(x), "NA", sprintf("%.4f", x))
subtext <- paste(
  sprintf("TP=%d  TN=%d  FP=%d  FN=%d", TP, TN, FP, FN),
  sprintf(" | Accuracy=%s  Precision=%s  Recall=%s",
          fmt(accuracy), fmt(precision), fmt(recall)),
  sep = ""
)

# Gráfico: matriz de confusión con métricas en subtítulo
p_cm <- ggplot(cm_df, aes(Predicho, Actual, fill = Conteo)) +
  geom_tile(color = "white", linewidth = 0.8) +
  geom_text(aes(label = Conteo), size = 6) +
  scale_fill_gradient(low = "#e6f3ff", high = "#08519c") +
  labs(
    title = "Matriz de confusión - Clasificador aleatorio (umbral 0.5)",
    subtitle = subtext,
    x = "Predicción del modelo",
    y = "Clase real",
    fill = "Conteo",
    caption = "Notas: TP = reales 1 predichos 1; TN = reales 0 predichos 0; FP = reales 0 predichos 1; FN = reales 1 predichos 0."
  ) +
  theme_minimal(base_size = 13) +
  theme(
    plot.title = element_text(face = "bold"),
    panel.grid = element_blank()
  )

# Mostrar en pantalla y GUARDAR a archivo
print(p_cm)
ggsave("random_classifier_confusion_matrix.png", p_cm, width = 8, height = 6, dpi = 150)

cat("\nListo ✅\n")
cat("- CSV con predicciones: arbolado-mendoza-dataset-validation-with-preds.csv\n")
cat("- Imagen de la matriz:  random_classifier_confusion_matrix.png\n")
cat(sprintf("- Métricas -> Accuracy: %s | Precision: %s | Recall: %s\n",
            fmt(accuracy), fmt(precision), fmt(recall)))

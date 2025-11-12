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

# --- Helper: convertir verdad a 0/1 de forma robusta ---
to_binary01 <- function(x) {
  if (is.logical(x)) return(as.integer(x))          # TRUE->1, FALSE->0
  if (is.numeric(x)) return(as.integer(x > 0))      # >0 -> 1, else 0
  if (is.character(x)) {
    xl <- tolower(trimws(x))
    return(as.integer(xl %in% c("1","true","t","yes","si","sí")))
  }
  stop("Tipo no manejado para la columna de verdad.")
}

# --- (a) Clasificador por clase mayoritaria ---
# Usa la columna de verdad (por defecto 'inclinacion_peligrosa') para
# determinar la clase mayoritaria (0 o 1) y la asigna a todas las filas.
# En caso de empate, asigna 0 por defecto (puedes cambiarlo con tie_wins=0/1).
biggerclass_classifier <- function(df, truth_col = "inclinacion_peligrosa", tie_wins = 0L) {
  if (!truth_col %in% names(df)) {
    stop(sprintf("No se encontró la columna de verdad '%s' en el dataframe.", truth_col))
  }
  y_true <- to_binary01(df[[truth_col]])
  n1 <- sum(y_true == 1, na.rm = TRUE)
  n0 <- sum(y_true == 0, na.rm = TRUE)
  majority <- if (n1 > n0) 1L else if (n0 > n1) 0L else as.integer(tie_wins)
  df$prediction_class <- majority
  attr(df, "majority_class") <- majority
  df
}

# =========================
# (b) Repetir 4c y 4d con biggerclass_classifier
# =========================
val_path <- "arbolado-mendoza-dataset-validation.csv"
df_val <- leer_csv_robusto(val_path)

if (!"inclinacion_peligrosa" %in% names(df_val)) {
  stop("No se encontró la columna 'inclinacion_peligrosa' en el dataset de validación.")
}

# Aplicar clasificador por clase mayoritaria
df_val <- biggerclass_classifier(df_val, truth_col = "inclinacion_peligrosa", tie_wins = 0L)
majority <- attr(df_val, "majority_class")
message(sprintf("Clase mayoritaria asignada por el modelo: %d", majority))

# Guardar CSV clasificado
write.csv(df_val, "arbolado-mendoza-dataset-validation-with-majority.csv", row.names = FALSE)

# --- Métricas (TP, TN, FP, FN) ---
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

# --- Matriz de confusión para el plot ---
cm_df <- data.frame(
  Actual   = factor(c("1 (Peligroso)", "1 (Peligroso)", "0 (No peligroso)", "0 (No peligroso)"),
                    levels = c("1 (Peligroso)", "0 (No peligroso)")),
  Predicho = factor(c("Pred=1", "Pred=0", "Pred=1", "Pred=0"),
                    levels = c("Pred=1", "Pred=0")),
  Conteo   = c(TP, FN, FP, TN)
)

fmt <- function(x) ifelse(is.na(x), "NA", sprintf("%.4f", x))
subtext <- paste(
  sprintf("TP=%d  TN=%d  FP=%d  FN=%d", TP, TN, FP, FN),
  sprintf(" | Accuracy=%s  Precision=%s  Recall=%s",
          fmt(accuracy), fmt(precision), fmt(recall)),
  sep = ""
)

p_cm <- ggplot(cm_df, aes(Predicho, Actual, fill = Conteo)) +
  geom_tile(color = "white", linewidth = 0.8) +
  geom_text(aes(label = Conteo), size = 6) +
  scale_fill_gradient(low = "#e6f3ff", high = "#08519c") +
  labs(
    title = "Matriz de confusión - Clasificador clase mayoritaria",
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

print(p_cm)
ggsave("biggerclass_confusion_matrix.png", p_cm, width = 8, height = 6, dpi = 150)

cat("\nListo ✅\n")
cat("- CSV con predicciones (clase mayoritaria): arbolado-mendoza-dataset-validation-with-majority.csv\n")
cat("- Imagen de la matriz:                     biggerclass_confusion_matrix.png\n")
cat(sprintf("- Clase mayoritaria asignada: %d\n", majority))
cat(sprintf("- Métricas -> Accuracy: %s | Precision: %s | Recall: %s\n",
            fmt(accuracy), fmt(precision), fmt(recall)))

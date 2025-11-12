# ================================================
# Análisis de arbolado - versión sin readr/tidyverse
# Lee/escribe con base R para evitar dependencias de SO
# Mantiene dplyr/ggplot2/forcats/scales para análisis
# ================================================

suppressPackageStartupMessages({
  library(dplyr)
  library(ggplot2)
  library(forcats)
  library(scales)
})

set.seed(123)

# ---------- Helper de lectura robusta ----------
# Intenta leer con coma, si detecta 1 sola columna reintenta con ';' y dec=','
leer_csv_robusto <- function(path) {
  if (!file.exists(path)) {
    stop("No se encuentra '", path, "' en el directorio: ", getwd())
  }
  # Intento 1: separador coma, punto decimal
  df <- tryCatch(
    read.csv(path, stringsAsFactors = FALSE, check.names = FALSE,
             fileEncoding = "UTF-8"),
    error = function(e) NULL
  )
  if (!is.null(df) && ncol(df) > 1) return(df)
  
  # Intento 2: separador ';', coma decimal
  df <- tryCatch(
    read.csv(path, stringsAsFactors = FALSE, check.names = FALSE,
             sep = ";", dec = ",", fileEncoding = "UTF-8"),
    error = function(e) NULL
  )
  if (is.null(df)) {
    stop("No se pudo leer el CSV. Revisa el separador/encoding.")
  }
  df
}

# ---------- PROGRAMA PRINCIPAL ----------
tryCatch({
  # 1) Cargar archivo
  ruta <- "arbolado-mza-dataset.csv"
  df_completo <- leer_csv_robusto(ruta)
  
  # 1a/1b) Split 80/20 (validación 20%)
  total_filas <- nrow(df_completo)
  tamaño_val <- floor(0.20 * total_filas)
  indices_val <- sample(seq_len(total_filas), size = tamaño_val)
  df_val   <- df_completo[indices_val, , drop = FALSE]
  df_train <- df_completo[-indices_val, , drop = FALSE]
  
  # Guardar splits con base R
  write.csv(df_val,   "arbolado-mendoza-dataset-validation.csv", row.names = FALSE)
  write.csv(df_train, "arbolado-mendoza-dataset-train.csv",      row.names = FALSE)
  
  message("Archivos 'arbolado-mendoza-dataset-validation.csv' y ",
          "'arbolado-mendoza-dataset-train.csv' creados con éxito.")
  message(paste("Filas entrenamiento:", nrow(df_train)))
  message(paste("Filas validación:",   nrow(df_val)))
  
  # ---------- Tarea 2 ----------
  # 2a) Distribución de inclinacion_peligrosa
  message("Generando gráfico 2a: Distribución de 'inclinacion_peligrosa'")
  g_2a <- ggplot(df_train, aes(x = factor(inclinacion_peligrosa))) +
    geom_bar(aes(fill = factor(inclinacion_peligrosa)), show.legend = FALSE) +
    geom_text(stat = 'count', aes(label = ..count..), vjust = -0.5) +
    labs(title = "Distribución de la clase 'inclinacion_peligrosa'",
         x = "Inclinación Peligrosa", y = "Conteo Total") +
    theme_minimal()
  print(g_2a)
  # ggsave("grafico_2a_distribucion.png", g_2a, width = 7, height = 5, dpi = 120)
  
  # 2b) Peligrosidad por sección (proporciones)
  message("Generando gráfico 2b: Peligrosidad por Sección")
  g_2b <- df_train %>%
    filter(!is.na(seccion)) %>%
    ggplot(aes(x = factor(seccion), fill = factor(inclinacion_peligrosa))) +
    geom_bar(position = "fill") +
    scale_y_continuous(labels = scales::percent) +
    labs(title = "Proporción de Peligrosidad por Sección",
         x = "Sección", y = "Proporción de Árboles",
         fill = "Inclinación Peligrosa") +
    theme_minimal()
  print(g_2b)
  # ggsave("grafico_2b_seccion.png", g_2b, width = 9, height = 5, dpi = 120)
  
  # 2c) Peligrosidad por especie (Top 15 más comunes)
  message("Generando gráfico 2c: Peligrosidad por Especie (Top 15)")
  top_especies <- df_train %>%
    count(especie, sort = TRUE) %>%
    dplyr::slice_max(n, n = 15, with_ties = FALSE) %>%
    pull(especie)
  
  g_2c <- df_train %>%
    filter(especie %in% top_especies) %>%
    ggplot(aes(x = forcats::fct_reorder(especie, inclinacion_peligrosa, .fun = mean),
               fill = factor(inclinacion_peligrosa))) +
    geom_bar(position = "fill") +
    coord_flip() +
    scale_y_continuous(labels = scales::percent) +
    labs(title = "Proporción de Peligrosidad (Top 15 Especies más Comunes)",
         x = "Especie", y = "Proporción de Árboles",
         fill = "Inclinación Peligrosa") +
    theme_minimal()
  print(g_2c)
  # ggsave("grafico_2c_especie.png", g_2c, width = 9, height = 6, dpi = 120)
  
  # ---------- Tarea 3: circ_tronco_cm ----------
  # 3a) Histogramas
  message("Generando gráfico 3a: Histograma de 'circ_tronco_cm'")
  g_3a_bins30 <- ggplot(df_train, aes(x = circ_tronco_cm)) +
    geom_histogram(bins = 30, fill = "steelblue", color = "white") +
    labs(title = "Histograma de Circunferencia de Tronco (30 bins)",
         x = "Circunferencia (cm)", y = "Frecuencia") +
    theme_minimal()
  print(g_3a_bins30)
  
  g_3a_bins100 <- ggplot(df_train, aes(x = circ_tronco_cm)) +
    geom_histogram(bins = 100, fill = "darkgreen", color = "white") +
    labs(title = "Histograma de Circunferencia de Tronco (100 bins)",
         x = "Circunferencia (cm)", y = "Frecuencia") +
    theme_minimal()
  print(g_3a_bins100)
  
  # 3b) Hist por peligrosidad
  message("Generando gráfico 3b: Histograma por Peligrosidad")
  g_3b <- ggplot(df_train, aes(x = circ_tronco_cm, fill = factor(inclinacion_peligrosa))) +
    geom_histogram(bins = 60, color = "white", show.legend = FALSE) +
    facet_wrap(~ inclinacion_peligrosa, ncol = 1, scales = "free_y") +
    labs(title = "Histograma de Circunferencia por Peligrosidad",
         x = "Circunferencia (cm)", y = "Frecuencia") +
    theme_minimal()
  print(g_3b)
  
  g_3b_densidad <- ggplot(df_train, aes(x = circ_tronco_cm, fill = factor(inclinacion_peligrosa))) +
    geom_density(alpha = 0.6) +
    labs(title = "Densidad de Circunferencia por Peligrosidad",
         x = "Circunferencia (cm)", y = "Densidad",
         fill = "Inclinación Peligrosa") +
    theme_minimal()
  print(g_3b_densidad)
  
  # 3c) Variable categórica por cuartiles
  cortes <- quantile(df_train$circ_tronco_cm,
                     probs = c(0, .25, .5, .75, 1),
                     na.rm = TRUE)
  message("Puntos de corte (cuartiles) para 'circ_tronco_cm':")
  print(cortes)
  
  etiquetas <- c("bajo", "medio", "alto", "muy alto")
  df_train_nuevo <- df_train %>%
    mutate(circ_tronco_cm_cat = cut(circ_tronco_cm,
                                    breaks = cortes,
                                    labels = etiquetas,
                                    include.lowest = TRUE))
  message("Verificación de la nueva variable 'circ_tronco_cm_cat':")
  print(table(df_train_nuevo$circ_tronco_cm_cat, useNA = "ifany"))
  
  # 3d) Guardar dataframe nuevo (base R)
  write.csv(df_train_nuevo, "arbolado-mendoza-dataset-circ_tronco_cm-train.csv",
            row.names = FALSE)
  message("DataFrame con la nueva variable categórica guardado con éxito.")
  
}, error = function(e) {
  message("Error al procesar el archivo: ", e$message)
  message("Verifica que el archivo 'arbolado-mendoza-dataset.csv' esté en tu WD.")
  message("Usa getwd() para ver el directorio y list.files() para listar archivos.")
})

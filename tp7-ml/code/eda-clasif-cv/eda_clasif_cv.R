# Utility functions for TP7B: EDA, baselines, and CV
# Requirements implemented:
# - prediction_prob column generation (random)
# - random_classifier (threshold 0.5)
# - biggerclass_classifier (majority class)
# - TP/TN/FP/FN and metrics (Accuracy, Precision, Sensitivity, Specificity)
# - create_folds and cross_validation using rpart

library(dplyr)
library(rpart)

# Create a reproducible column of random prediction probabilities
add_random_probs <- function(df, seed = 2025) {
  set.seed(seed)
  df %>% mutate(prediction_prob = runif(n()))
}

# Random classifier using prediction_prob and threshold 0.5 (or custom)
random_classifier <- function(df, prob_col = "prediction_prob", threshold = 0.5) {
  df %>% mutate(prediction_class = ifelse(.data[[prob_col]] >= threshold, 1L, 0L))
}

# Majority-class classifier: always predict the most frequent class in target_col
biggerclass_classifier <- function(df, target_col = "inclinacion_peligrosa") {
  freq <- df %>% count(.data[[target_col]]) %>% arrange(desc(n))
  maj_class <- as.integer(freq[[target_col]][1])
  df %>% mutate(prediction_class = rep(maj_class, n()))
}

# Confusion counts: returns TP, TN, FP, FN as a named list
confusion_counts <- function(df, truth_col = "inclinacion_peligrosa", pred_col = "prediction_class") {
  tbl <- table(factor(df[[truth_col]], levels = c(1,0)), factor(df[[pred_col]], levels = c(1,0)))
  # rows = truth (1,0), cols = pred (1,0)
  TP <- as.integer(tbl["1","1"])
  TN <- as.integer(tbl["0","0"])
  FP <- as.integer(tbl["0","1"])
  FN <- as.integer(tbl["1","0"])
  list(TP = TP, TN = TN, FP = FP, FN = FN)
}

# Metrics: Accuracy, Precision, Sensitivity (Recall), Specificity
compute_metrics <- function(counts) {
  TP <- counts$TP; TN <- counts$TN; FP <- counts$FP; FN <- counts$FN
  Accuracy <- (TP + TN) / (TP + TN + FP + FN)
  Precision <- if ((TP + FP) == 0) NA else TP / (TP + FP)
  Sensitivity <- if ((TP + FN) == 0) NA else TP / (TP + FN)
  Specificity <- if ((TN + FP) == 0) NA else TN / (TN + FP)
  tibble::tibble(Accuracy = Accuracy, Precision = Precision, Sensitivity = Sensitivity, Specificity = Specificity,
                 TP = TP, TN = TN, FP = FP, FN = FN)
}

# Create k folds: returns a list of indices for each fold
create_folds <- function(df, k = 5, seed = 2025, stratify_by = NULL) {
  set.seed(seed)
  n <- nrow(df)
  if (!is.null(stratify_by)) {
    # stratified sampling
    df$___fold_id <- NA_integer_
    unique_vals <- unique(df[[stratify_by]])
    for (val in unique_vals) {
      idx <- which(df[[stratify_by]] == val)
      shuffled <- sample(idx)
      folds <- split(shuffled, rep(1:k, length.out = length(shuffled)))
      for (i in seq_along(folds)) df$___fold_id[folds[[i]]] <- i
    }
    folds_list <- lapply(1:k, function(i) which(df$___fold_id == i))
    df$___fold_id <- NULL
    return(folds_list)
  } else {
    idx <- sample(1:n)
    folds <- split(idx, rep(1:k, length.out = n))
    return(folds)
  }
}

# Cross-validation using rpart decision tree on formula and returning metrics per fold
cross_validation <- function(df, formula, k = 5, seed = 2025, control = rpart.control(cp = 0.01, minsplit = 20), stratify = TRUE) {
  if (stratify && ("inclinacion_peligrosa" %in% names(df))) {
    folds <- create_folds(df, k = k, seed = seed, stratify_by = "inclinacion_peligrosa")
  } else {
    folds <- create_folds(df, k = k, seed = seed, stratify_by = NULL)
  }

  results <- lapply(seq_along(folds), function(i) {
    test_idx <- folds[[i]]
    train_idx <- setdiff(seq_len(nrow(df)), test_idx)
    train_df <- df[train_idx, , drop = FALSE]
    test_df <- df[test_idx, , drop = FALSE]

    model <- rpart::rpart(formula = formula, data = train_df, control = control)
    preds_prob <- predict(model, test_df)[, "1"]
    # if predict returns vector (binary numeric), handle both
    if (is.null(dim(predict(model, test_df)))) {
      # single vector
      preds_prob <- predict(model, test_df)
      # try to transform to probability of class 1 when factor levels present
      if (is.factor(train_df$inclinacion_peligrosa)) {
        # rpart returns probabilities when type="prob"
        preds_prob <- predict(model, test_df, type = "prob")[, "1"]
      }
    } else {
      preds_prob <- predict(model, test_df, type = "prob")[, "1"]
    }

    test_df$prediction_class <- ifelse(preds_prob >= 0.5, 1L, 0L)
    counts <- confusion_counts(test_df, truth_col = "inclinacion_peligrosa", pred_col = "prediction_class")
    metrics <- compute_metrics(counts)
    metrics$fold <- i
    metrics
  })

  results_df <- dplyr::bind_rows(results)
  summary <- results_df %>%
    summarise(across(c(Accuracy, Precision, Sensitivity, Specificity), list(Mean = mean, SD = sd), .names = "{.col}_{.fn}"))
  list(per_fold = results_df, summary = summary)
}

# End of file

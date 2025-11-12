import pandas as pd
import numpy as np
from catboost import CatBoostClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                             f1_score, confusion_matrix)
import warnings
warnings.filterwarnings('ignore')

np.random.seed(123)

print("\n" + "="*70)
print("OPTIMIZED CATBOOST - SIMPLE FEATURES, BETTER TUNING")
print("="*70 + "\n")

def preprocess_simple(df, is_train=True):
    """Simple preprocessing - NO feature engineering, just core features"""
    df = df.copy()
    df.columns = df.columns.str.lower()
    
    # Core features only - the ones that actually matter
    feature_cols = ['circ_tronco_cm', 'lat', 'long', 'altura', 'especie', 'diametro_tronco']
    cat_features = ['altura', 'especie', 'diametro_tronco']
    
    if is_train:
        cols_needed = feature_cols + ['inclinacion_peligrosa', 'id']
    else:
        cols_needed = feature_cols + ['id']
    
    df = df[cols_needed]
    
    # Clean strings
    for col in cat_features:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    
    # Ensure numerics
    for col in ['circ_tronco_cm', 'lat', 'long']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df, cat_features, feature_cols

def optimize_threshold_stable(y_true, y_proba, metric='f1'):
    """Find best threshold using validation data"""
    thresholds = np.arange(0.1, 0.9, 0.005)  # Finer grid
    best_score = 0
    best_thresh = 0.5
    
    for thresh in thresholds:
        y_pred = (y_proba >= thresh).astype(int)
        
        if metric == 'f1':
            score = f1_score(y_true, y_pred, zero_division=0)
        elif metric == 'balanced':
            # Balance precision and recall
            prec = precision_score(y_true, y_pred, zero_division=0)
            rec = recall_score(y_true, y_pred, zero_division=0)
            score = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0
        
        if score > best_score:
            best_score = score
            best_thresh = thresh
    
    return best_thresh, best_score

def catboost_optimized_cv(df, n_folds=10, use_scale_pos_weight=True):
    """Optimized CV with hyperparameter tuning"""
    
    print("Preprocessing...")
    df_processed, cat_features, feature_cols = preprocess_simple(df, is_train=True)
    df_clean = df_processed.dropna(subset=feature_cols + ['inclinacion_peligrosa'])
    
    print(f"Samples: {len(df_clean)}")
    print(f"Features: {feature_cols}")
    print(f"Class distribution: {df_clean['inclinacion_peligrosa'].value_counts().to_dict()}\n")
    
    y = df_clean['inclinacion_peligrosa'].astype(int)
    X = df_clean[feature_cols]
    
    # Cat feature indices
    cat_indices = [i for i, col in enumerate(feature_cols) if col in cat_features]
    
    # Calculate scale_pos_weight
    class_counts = y.value_counts()
    scale_pos_weight = class_counts[0] / class_counts[1]
    print(f"Scale_pos_weight: {scale_pos_weight:.2f}\n")
    
    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=123)
    results = []
    
    print(f"Starting {n_folds}-Fold CV...\n")
    
    # Try different hyperparameter combinations
    best_params = None
    best_avg_f1 = 0
    
    param_grid = [
        # Conservative: High regularization, lower complexity
        {'iterations': 1000, 'depth': 6, 'learning_rate': 0.05, 'l2_leaf_reg': 10, 'min_data_in_leaf': 10},
        # Balanced
        {'iterations': 1500, 'depth': 7, 'learning_rate': 0.03, 'l2_leaf_reg': 7, 'min_data_in_leaf': 7},
        # Aggressive: Lower regularization, more complexity
        {'iterations': 2000, 'depth': 8, 'learning_rate': 0.03, 'l2_leaf_reg': 5, 'min_data_in_leaf': 5},
    ]
    
    for param_set_idx, params in enumerate(param_grid):
        print(f"\n{'='*70}")
        print(f"Testing Parameter Set {param_set_idx + 1}/{len(param_grid)}")
        print(f"Params: {params}")
        print(f"{'='*70}\n")
        
        fold_results = []
        
        for fold, (train_idx, val_idx) in enumerate(skf.split(X, y), 1):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
            
            if use_scale_pos_weight:
                model = CatBoostClassifier(
                    **params,
                    loss_function='Logloss',
                    eval_metric='F1',
                    random_seed=123 + fold,
                    verbose=False,
                    scale_pos_weight=scale_pos_weight,
                    cat_features=cat_indices,
                    early_stopping_rounds=150
                )
            else:
                model = CatBoostClassifier(
                    **params,
                    loss_function='Logloss',
                    eval_metric='F1',
                    random_seed=123 + fold,
                    verbose=False,
                    auto_class_weights='Balanced',
                    cat_features=cat_indices,
                    early_stopping_rounds=150
                )
            
            # Train
            model.fit(X_train, y_train, eval_set=(X_val, y_val), verbose=False)
            
            # Predict
            y_val_proba = model.predict_proba(X_val)[:, 1]
            
            # Optimize threshold on validation set (not train!)
            best_thresh, _ = optimize_threshold_stable(y_val, y_val_proba, metric='f1')
            y_pred = (y_val_proba >= best_thresh).astype(int)
            
            # Metrics
            cm = confusion_matrix(y_val, y_pred)
            tn, fp, fn, tp = cm.ravel()
            
            f1 = f1_score(y_val, y_pred, zero_division=0)
            precision = precision_score(y_val, y_pred, zero_division=0)
            recall = recall_score(y_val, y_pred, zero_division=0)
            
            fold_results.append({
                'Fold': fold,
                'TP': tp, 'TN': tn, 'FP': fp, 'FN': fn,
                'F1': f1, 'Precision': precision, 'Recall': recall,
                'Threshold': best_thresh
            })
            
            if fold <= 2:  # Print first 2 folds for monitoring
                print(f"  Fold {fold}: F1={f1:.4f}, Prec={precision:.4f}, Rec={recall:.4f}, Thresh={best_thresh:.3f}")
        
        avg_f1 = np.mean([r['F1'] for r in fold_results])
        avg_prec = np.mean([r['Precision'] for r in fold_results])
        avg_rec = np.mean([r['Recall'] for r in fold_results])
        
        print(f"\n  Average F1: {avg_f1:.4f} | Precision: {avg_prec:.4f} | Recall: {avg_rec:.4f}")
        
        if avg_f1 > best_avg_f1:
            best_avg_f1 = avg_f1
            best_params = params
            results = fold_results
    
    print(f"\n{'='*70}")
    print(f"BEST PARAMETER SET:")
    print(f"{best_params}")
    print(f"Best Average F1-Score: {best_avg_f1:.4f}")
    print(f"{'='*70}\n")
    
    # Final summary with best params
    results_df = pd.DataFrame(results)
    
    metrics = ['F1', 'Precision', 'Recall']
    summary = pd.DataFrame({
        'Metric': metrics,
        'Mean': [results_df[m].mean() for m in metrics],
        'Std': [results_df[m].std() for m in metrics]
    })
    
    print("FINAL CROSS-VALIDATION RESULTS:")
    print(summary.to_string(index=False))
    
    baseline_f1 = 0.3691
    improvement = best_avg_f1 - baseline_f1
    print(f"\n🔍 vs Baseline (0.3691): {improvement:+.4f} ({improvement/baseline_f1*100:+.1f}%)\n")
    
    return results_df, summary, best_params

def train_final_optimized(train_path, test_path, best_params, output_path='catboost_submission_final.csv'):
    """Train final model with best params"""
    
    print("\n" + "="*70)
    print("TRAINING FINAL MODEL WITH OPTIMIZED PARAMETERS")
    print("="*70 + "\n")
    
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    
    train_processed, cat_features, feature_cols = preprocess_simple(train_df, is_train=True)
    test_processed, _, _ = preprocess_simple(test_df, is_train=False)
    
    train_clean = train_processed.dropna(subset=feature_cols + ['inclinacion_peligrosa'])
    
    X_train = train_clean[feature_cols]
    y_train = train_clean['inclinacion_peligrosa'].astype(int)
    X_test = test_processed[feature_cols]
    test_ids = test_processed['id']
    
    cat_indices = [i for i, col in enumerate(feature_cols) if col in cat_features]
    
    # Calculate scale_pos_weight
    class_counts = y_train.value_counts()
    scale_pos_weight = class_counts[0] / class_counts[1]
    
    print(f"Training samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")
    print(f"Using params: {best_params}\n")
    
    # Train with slightly more iterations for final model
    final_params = best_params.copy()
    final_params['iterations'] = min(final_params['iterations'] * 15 // 10, 3000)  # +50% iterations
    
    model = CatBoostClassifier(
        **final_params,
        loss_function='Logloss',
        eval_metric='F1',
        random_seed=42,
        verbose=200,
        scale_pos_weight=scale_pos_weight,
        cat_features=cat_indices
    )
    
    print("Training...")
    model.fit(X_train, y_train)
    
    # Predict with threshold=0.5 (conservative for Kaggle)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    y_pred = (y_pred_proba >= 0.5).astype(int)
    
    submission = pd.DataFrame({'id': test_ids, 'inclinacion_peligrosa': y_pred})
    submission.to_csv(output_path, index=False)
    
    print(f"\n✅ Saved: {output_path}")
    print(f"Prediction distribution:\n{submission['inclinacion_peligrosa'].value_counts()}\n")
    
    # Feature importance
    importance = pd.DataFrame({
        'Feature': feature_cols,
        'Importance': model.get_feature_importance()
    }).sort_values('Importance', ascending=False)
    
    print("Feature Importance:")
    print(importance.to_string(index=False))
    
    return model, submission

if __name__ == "__main__":
    
    print(">>> HYPERPARAMETER OPTIMIZATION WITH CV <<<\n")
    train_data = pd.read_csv('../data/arbolado-mendoza-dataset-train.csv')
    
    cv_results, cv_summary, best_params = catboost_optimized_cv(
        train_data,
        n_folds=10,
        use_scale_pos_weight=True
    )
    
    cv_results.to_csv('catboost_final_cv_results.csv', index=False)
    cv_summary.to_csv('catboost_final_cv_summary.csv', index=False)
    
    print("\n>>> TRAINING FINAL MODEL <<<")
    final_model, submission = train_final_optimized(
        '../data/arbolado-mendoza-dataset-train.csv',
        'arbolado-mza-dataset-test.csv',
        best_params,
        'catboost_submission_final.csv'
    )
    
    print("\n" + "="*70)
    print("✅ OPTIMIZATION COMPLETE!")
    print("="*70)
    f1_mean = cv_summary[cv_summary['Metric'] == 'F1']['Mean'].values[0]
    print(f"\n🎯 Final CV F1-Score: {f1_mean:.4f}")
    print("📁 Files: catboost_final_cv_results.csv, catboost_submission_final.csv\n")

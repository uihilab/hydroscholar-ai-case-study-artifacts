import os
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib

def main():
    # Paths
    data_path = os.path.join('data', 'ml_ready_features.csv')
    model_dir = 'outputs'
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, 'rf_model.pkl')
    preds_path = os.path.join(model_dir, 'test_predictions.csv')

    # Load ML-ready features with proper date index
    df = pd.read_csv(
        data_path,
        parse_dates=['Unnamed: 0'],
        index_col='Unnamed: 0'
    )
    df.index.rename('date', inplace=True)

    # Define features and target
    feature_cols = ['Flow_Upstream', 'Upstream_Lag1', 'Upstream_Lag2', 'Upstream_Lag3']
    target_col = 'Flow_Downstream'
    X = df[feature_cols]
    y = df[target_col]

    # Chronological train-test split (first 80% train, last 20% test)
    split_index = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
    y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]

    # Initialize and train Random Forest model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Save the trained model
    joblib.dump(model, model_path)

    # Predict on test set
    test_preds = model.predict(X_test)
    results = pd.DataFrame({
        'actual': y_test.values,
        'predicted': test_preds
    }, index=X_test.index)
    results.to_csv(preds_path)

    print(f"Model trained and saved to {model_path}")
    print(f"Test predictions saved to {preds_path}")

if __name__ == '__main__':
    main()
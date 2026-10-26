import os
import numpy as np
import pandas as pd
from tensorflow.keras.models import model_from_json

def create_sequences(df, seq_len=7):
    X, y, dates = [], [], []
    precip = df['precipitation_mm'].values
    logq = df['log_discharge'].values
    date_vals = df['date'].values
    for i in range(seq_len, len(df)):
        X.append(precip[i-seq_len:i])
        y.append(logq[i])
        dates.append(date_vals[i])
    X = np.array(X).reshape(-1, seq_len, 1)
    y = np.array(y)
    dates = np.array(dates)
    return X, y, dates

if __name__ == '__main__':
    # Load cleaned data
    df = pd.read_csv('data/clean/cleaned_data.csv', parse_dates=['date'])
    df = df.sort_values('date').reset_index(drop=True)

    # Compute log discharge
    df['log_discharge'] = np.log(df['discharge_cfs'] + 0.1)

    # We need extra 7 days of history before each split start
    full_start = pd.to_datetime('2014-12-25')
    full_end = pd.to_datetime('2020-12-31')
    df_full = df[(df['date'] >= full_start) & (df['date'] <= full_end)].reset_index(drop=True)

    # Prepare training data (targets from 2015-01-01 to 2018-12-31)
    train_seq_start = pd.to_datetime('2014-12-25')
    train_seq_end   = pd.to_datetime('2018-12-31')
    df_train_seq = df_full[(df_full['date'] >= train_seq_start) & (df_full['date'] <= train_seq_end)].reset_index(drop=True)
    X_train, y_train, _ = create_sequences(df_train_seq, seq_len=7)

    # Prepare validation data (targets from 2019-01-01 to 2019-12-31)
    val_seq_start = pd.to_datetime('2018-12-25')
    val_seq_end   = pd.to_datetime('2019-12-31')
    df_val_seq = df_full[(df_full['date'] >= val_seq_start) & (df_full['date'] <= val_seq_end)].reset_index(drop=True)
    X_val, y_val, _ = create_sequences(df_val_seq, seq_len=7)

    # Prepare test data (targets from 2020-01-01 to 2020-12-31)
    test_seq_start = pd.to_datetime('2019-12-25')
    test_seq_end   = pd.to_datetime('2020-12-31')
    df_test_seq = df_full[(df_full['date'] >= test_seq_start) & (df_full['date'] <= test_seq_end)].reset_index(drop=True)
    X_test, y_test, dates_test = create_sequences(df_test_seq, seq_len=7)

    # Load model architecture
    with open('models/lstm_log_model_arch.json', 'r') as f:
        model = model_from_json(f.read())

    # Compile model
    model.compile(optimizer='adam', loss='mse')

    # Train
    model.fit(
        X_train, y_train,
        epochs=50,
        batch_size=32,
        validation_data=(X_val, y_val),
        verbose=1
    )

    # Save weights
    os.makedirs('models', exist_ok=True)
    model.save_weights('models/lstm_log_model_weights.weights.h5')

    # Predict on test set
    y_pred = model.predict(X_test).flatten()

    # Save predictions
    df_out = pd.DataFrame({
        'date': dates_test,
        'true_log_discharge': y_test,
        'predicted_log_discharge': y_pred
    })
    os.makedirs('outputs', exist_ok=True)
    df_out.to_csv('outputs/test_predictions_log.csv', index=False)
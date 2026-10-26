import os
import pandas as pd
import numpy as np
from tensorflow.keras.models import model_from_json
from tensorflow.keras.metrics import RootMeanSquaredError

# Ensure output directories exist
os.makedirs('outputs', exist_ok=True)
os.makedirs('models', exist_ok=True)

print("1. Loading and preparing data")
df = pd.read_csv('data/clean/cleaned_data.csv', parse_dates=['date'])
df = df.sort_values('date').reset_index(drop=True)
print(f"  Data shape after load: {df.shape}")

print("2. Building sequences (7-day precipitation window)")
X, y, dates = [], [], []
for i in range(7, len(df)):
    window = df.iloc[i-7:i]
    if window['precipitation_mm'].isnull().any():
        continue
    feats = window[['precipitation_mm']].values  # shape (7, 1)
    X.append(feats)
    y.append(df.loc[i, 'discharge_cfs'])
    dates.append(df.loc[i, 'date'])
X = np.array(X)
y = np.array(y)
dates = np.array(dates, dtype='datetime64[ns]')
print(f"  Sequence data shapes: X={X.shape}, y={y.shape}, dates={dates.shape}")

print("3. Splitting into train/val/test by date")
train_mask = (dates >= np.datetime64('2015-01-01')) & (dates <= np.datetime64('2018-12-31'))
val_mask   = (dates >= np.datetime64('2019-01-01')) & (dates <= np.datetime64('2019-12-31'))
test_mask  = (dates >= np.datetime64('2020-01-01')) & (dates <= np.datetime64('2020-12-31'))

X_train, y_train = X[train_mask], y[train_mask]
X_val,   y_val   = X[val_mask],   y[val_mask]
X_test,  y_test, dates_test = X[test_mask], y[test_mask], dates[test_mask]
print(f"  Train shape: X={X_train.shape}, y={y_train.shape}")
print(f"  Val   shape: X={X_val.shape}, y={y_val.shape}")
print(f"  Test  shape: X={X_test.shape}, y={y_test.shape}")

print("4. Loading LSTM model architecture")
with open('models/lstm_model_arch.json', 'r') as f:
    model_json = f.read()
model = model_from_json(model_json)

print("5. Compiling model")
model.compile(
    optimizer='adam',
    loss='mean_squared_error',
    metrics=[RootMeanSquaredError(name='rmse')]
)

print("6. Training model for 50 epochs")
history = model.fit(
    X_train,
    y_train,
    validation_data=(X_val, y_val),
    epochs=50,
    batch_size=32,
    verbose=2
)

print("7. Saving model weights")
weights_path = 'models/lstm_model_weights.weights.h5'
model.save_weights(weights_path)
print(f"  Weights saved to {weights_path}")

print("8. Predicting on test set and saving results")
y_pred = model.predict(X_test).flatten()
pred_df = pd.DataFrame({
    'date': dates_test,
    'true_discharge_cfs': y_test,
    'predicted_discharge_cfs': y_pred
})
pred_df.to_csv('outputs/test_predictions.csv', index=False)
print("Done. Test predictions saved to outputs/test_predictions.csv")
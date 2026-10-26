import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import os

# Define a Sequential LSTM model for log-transformed discharge
model = Sequential()
# same configuration as 04_define_lstm_model.py
model.add(LSTM(units=32, input_shape=(12, 1)))
model.add(Dense(1))

# Compile with MSE loss and Adam optimizer
model.compile(optimizer='adam', loss='mean_squared_error')

# Serialize model architecture to JSON
model_json = model.to_json()
os.makedirs('models', exist_ok=True)
with open(os.path.join('models', 'lstm_log_model_arch.json'), 'w') as json_file:
    json_file.write(model_json)
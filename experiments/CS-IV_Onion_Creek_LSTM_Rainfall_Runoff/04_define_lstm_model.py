import os
import tensorflow as tf

# Define the LSTM model
model = tf.keras.Sequential([
    tf.keras.layers.LSTM(32, input_shape=(7, 1)),
    tf.keras.layers.Dense(1)
])

# Compile the model
model.compile(optimizer='adam', loss='mean_squared_error')

# Ensure the output directory exists
os.makedirs('models', exist_ok=True)

# Serialize model architecture to JSON
model_json = model.to_json()
with open('models/lstm_model_arch.json', 'w') as json_file:
    json_file.write(model_json)
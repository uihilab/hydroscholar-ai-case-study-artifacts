import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
from hydrostats import nse, rmse

def main():
    # Load predictions
    df = pd.read_csv('outputs/test_predictions_log.csv')

    # De-log the discharge values (exp(value) - 0.1)
    df['true_discharge'] = np.exp(df['true_log_discharge']) - 0.1
    df['predicted_discharge'] = np.exp(df['predicted_log_discharge']) - 0.1

    # Compute metrics
    nse_value = nse(df['true_discharge'], df['predicted_discharge'])
    rmse_value = rmse(df['true_discharge'], df['predicted_discharge'])

    # Save metrics to JSON
    metrics = {
        'NSE': float(nse_value),
        'RMSE': float(rmse_value)
    }
    with open('outputs/log_metrics.json', 'w') as f:
        json.dump(metrics, f, indent=4)

    # Plot true vs predicted discharge
    plt.figure(figsize=(10, 6))
    plt.plot(df['true_discharge'], label='True Discharge')
    plt.plot(df['predicted_discharge'], label='Predicted Discharge')
    plt.xlabel('Time')
    plt.ylabel('Discharge')
    plt.title('True vs. Predicted Discharge')
    plt.legend()
    plt.tight_layout()
    plt.savefig('outputs/plot_log.png', dpi=300)
    plt.close()

if __name__ == '__main__':
    main()
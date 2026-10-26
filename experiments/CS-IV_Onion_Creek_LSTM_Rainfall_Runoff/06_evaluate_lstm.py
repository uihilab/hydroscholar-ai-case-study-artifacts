import pandas as pd
from hydrostats.metrics import nse, rmse
import json
import matplotlib.pyplot as plt

def main():
    # Load test predictions
    df = pd.read_csv('outputs/test_predictions.csv', parse_dates=['date'], index_col='date')

    # Extract observed and simulated discharge
    observed = df['true_discharge_cfs']
    simulated = df['predicted_discharge_cfs']

    # Compute metrics
    nse_value = nse(observed, simulated)
    rmse_value = rmse(observed, simulated)

    # Save metrics to JSON
    metrics = {
        "NSE": nse_value,
        "RMSE": rmse_value
    }
    with open('outputs/metrics.json', 'w') as f:
        json.dump(metrics, f, indent=4)

    # Plot observed vs simulated discharge
    plt.figure(figsize=(10, 6))
    plt.plot(df.index, observed, label='True Discharge')
    plt.plot(df.index, simulated, label='Predicted Discharge')
    plt.xlabel('Date')
    plt.ylabel('Discharge (cfs)')
    plt.title('True vs Predicted Discharge')
    plt.legend()
    plt.tight_layout()
    plt.savefig('outputs/plot_initial.png')
    plt.close()

if __name__ == '__main__':
    main()
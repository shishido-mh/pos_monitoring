import pandas as pd
from pivoter import Pivot
from sklearn.ensemble import IsolationForest
from joblib import dump

# Get train data
url = 'https://raw.githubusercontent.com/thais-menezes/monitoring/main/transactions_1.csv'
X = pd.read_csv(url)

# Pivot the df
X_train = Pivot.pivot_df(X)

# Select relevant columns to the model
cols = ['approved', 'backend_reversed', 'denied', 'failed', 'processing',
        'reversed', 'total', 'success_rate', 'reversal_rate', 'denial_rate', 
        'failure_rate', 'hour', 'minute'
        ]

# Create model
model = IsolationForest(random_state=42)

# Fit model with training data
model.fit(X_train[cols])

# Save the model to a file
dump(model, 'isolation_forest_model.joblib')

print('Model saved successfully')

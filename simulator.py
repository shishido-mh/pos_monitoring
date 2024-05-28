import pandas as pd
import requests
from pivoter import Pivot  # Assuming Pivoter is a custom library/module you have
import time

# Read POS data
X = pd.read_csv('https://raw.githubusercontent.com/thais-menezes/monitoring/main/transactions_2.csv')
X = X.rename(columns={'count': 'f0_'})  # Renaming 'count' column to 'f0_' for clarity

# API URL
url = 'http://127.0.0.1:5000/receive_transaction'
# Pivot dataframe
X_pivoted = Pivot.pivot_df(X)

# Send each data to the API
for index, row in X_pivoted.iterrows():
    # Convert the row to a dictionary
    row_data = row.to_dict()
    response = requests.post(url, json=row_data)
    
    # Check if the request was successful
    if response.status_code == 200:
        print("API call successful!")
        print("Response JSON:")
        print(response.json())
    else:
        print("API call failed with status code:", response.status_code)
        print("Response text:")
        print(response.text)
    time.sleep(10)
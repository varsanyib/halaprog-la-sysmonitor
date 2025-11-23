from sklearn.ensemble import IsolationForest
import numpy as np
import pandas as pd

class AnomalyDetector:
    def __init__(self, contamination=0.01, random_state=42, min_samples=60):
        self.model = IsolationForest(random_state=random_state, contamination=contamination)
        self.is_trained = False
        self.min_samples = min_samples

    def train(self, data_list):
        if len(data_list) < self.min_samples:
            return False

        # Use CPU % and Memory % data
        df = pd.DataFrame([entry['data'] for entry in data_list])
        features = df[['cpu_usage_percent', 'memory_percent']].values
        
        # Learning the model
        self.model.fit(features)
        self.is_trained = True
        return True

    def predict_anomaly_score(self, current_data):
        if not self.is_trained:
            return 0.0 # Model not trained yet
        
        current_features = np.array([[
            current_data['cpu_usage_percent'], 
            current_data['memory_percent']
        ]])
        
        # The decision_function returns the anomaly score. Lower scores indicate more abnormal instances.
        score = self.model.decision_function(current_features)[0]
        return score
from flask import Flask, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)

# Load the saved hybrid setup
saved_data = joblib.load("full_model.pkl")
xgb = saved_data["xgb_model"]
iso = saved_data["iso_model"]
threshold = saved_data["threshold"]

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        # Expecting [temperature, humidity]
        features = np.array([[data['temp'], data['hum']]])
        
        # XGBoost Prob
        prob = xgb.predict_proba(features)[:, 1][0]
        xgb_vote = 1 if prob > threshold else 0
        
        # Isolation Forest
        iso_vote = 1 if iso.predict(features)[0] == -1 else 0
        
        #  Hybrid Strategy (AND logic)
        is_anomaly = bool(xgb_vote and iso_vote)
        
        return jsonify({"anomaly": bool(is_anomaly), "probability": float(prob)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
from flask import Flask, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)

# load the saved hybrid setup
saved_data = joblib.load("full_model.pkl")
xgb = saved_data["xgb_model"]
iso = saved_data["iso_model"]
threshold = saved_data["threshold"]

# convert strings to numbers
def encode_state(state_str):
    mapping = {"AUTO": 0, "TRIP": 1, "RESET": 2, "CLOSED": 0, "OPEN": 1}
    return mapping.get(state_str, 0)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json

        # extract data
        temp = data.get('motorTemperatureC')
        cmd = encode_state(data.get('relayCommand'))
        fdbk = encode_state(data.get('relayFeedback'))
        ot = int(data.get('overTemperature', 0))
        
        # create feature arr
        features = np.array([[temp, cmd, fdbk, ot]])

        # XGBoost Prob
        prob = xgb.predict_proba(features)[:, 1][0]
        xgb_vote = 1 if prob > threshold else 0
        
        # isolation Forest
        iso_vote = 1 if iso.predict(features)[0] == -1 else 0
        
        # hybrid Strategy (OR logic)
        is_anomaly = bool(xgb_vote or iso_vote)
        
        return jsonify({
            "is_trip_risk": bool(xgb_vote),
            "is_anomaly": bool(iso_vote),
            "hybrid_alert": is_anomaly,
            "probability": round(float(prob), 4)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
from sklearn.metrics import classification_report, confusion_matrix
import joblib
from xgboost import XGBClassifier
from data_preprocessing import data_preprocessing
from sklearn.ensemble import IsolationForest
import numpy as np
from sklearn.metrics import f1_score

# model
model = XGBClassifier(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric="logloss"
)

# data preprocessing
X_train_balanced, y_train_balanced, X_test, y_test = data_preprocessing()

# XGBoost train
model.fit(X_train_balanced, y_train_balanced)

# train Isolation Forest (ONLY on normal data)
iso_model = IsolationForest(
    n_estimators=200,
    contamination=0.1,
    random_state=42
)

# train only on normal data
X_train_normal = X_train_balanced[y_train_balanced == 0]

iso_model.fit(X_train_normal)


# XGBoost probability
y_proba = model.predict_proba(X_test)[:, 1]

# Isolation Forest predictions
iso_pred = iso_model.predict(X_test)

# convert Isolation Forest output:
# -1 = anomaly, 1 = normal
iso_pred = (iso_pred == -1).astype(int)

"""
# threshold tuning
for threshold in [0.1, 0.2, 0.3, 0.4, 0.5]:
    y_pred = (y_proba > threshold).astype(int)
    print(threshold)
    # evaluate model
    print(confusion_matrix(y_test, y_pred))
    print(classification_report(y_test, y_pred))


# best threshold value
threshold = 0.4
print(threshold)
# evaluate model
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))

"""

thresholds = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

for threshold in thresholds:

    # XGBoost prediction
    xgb_pred = (y_proba > threshold).astype(int)

    # hybrid rule
    final_pred = []
    final_pred2 = []

    print("Below one is using or operation")

    for x, i in zip(xgb_pred, iso_pred):
        if x == 1 or i == 1:
            final_pred.append(1)
        else:
            final_pred.append(0)

    final_pred = np.array(final_pred)

    print("\nThreshold:", threshold)
    print(confusion_matrix(y_test, final_pred))
    print(classification_report(y_test, final_pred))

    print("Below one is using and operation")

    for x, i in zip(xgb_pred, iso_pred):
        if x == 1 and i == 1:
            final_pred2.append(1)
        else:
            final_pred2.append(0)

    final_pred2 = np.array(final_pred2)

    print("\nThreshold:", threshold)
    print(confusion_matrix(y_test, final_pred2))
    print(classification_report(y_test, final_pred2))


# best  model
print("\n \n Best model:\n")
threshold=0.8

# XGBoost prediction
xgb_pred = (y_proba > threshold).astype(int)

# hybrid rule
final_pred = []

for x, i in zip(xgb_pred, iso_pred):
    if x == 1 and i == 1:
        final_pred.append(1)
    else:
        final_pred.append(0)

final_pred = np.array(final_pred)

print("\nThreshold:", threshold)
print(confusion_matrix(y_test, final_pred))
print(classification_report(y_test, final_pred))




# save 

import os

# current dir
script_dir = os.path.dirname(os.path.abspath(__file__))
# full path for .pkl
save_path = os.path.join(script_dir, "full_model.pkl")

# save 
joblib.dump({
    "xgb_model": model,
    "iso_model": iso_model,
    "threshold": 0.8,
    "strategy": "and"
}, save_path)

print(f"Model saved successfully at: {save_path}")
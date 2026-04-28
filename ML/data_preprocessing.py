import pandas as pd
import os
import json
import seaborn as sns
import matplotlib.pyplot as plt
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from publisher.simulation import simulate_data_for_ML_training


def data_preprocessing():
    # read data
    data = [json.loads(simulate_data_for_ML_training()) for _ in range(5000)]
    data = pd.DataFrame(data)


    # corelation matrix
    corr_matrix = data.corr()

    # heat mapp
    sns.heatmap(corr_matrix, cmap="coolwarm")
    plt.title("Correlation Matrix")
    #plt.show()

    # print counts
    print(data['label'].value_counts())

    # visualize data
    """sns.countplot(data=data, x='label')
    plt.title("Target Variable Distribution")
    plt.show()"""

    # slit data and label
    X = data.drop('label', axis=1)
    y = data['label']

    # split data into train and test data  >> 80% for testing >> kept imbalance ratio correct
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2 , random_state=42, stratify=y)

    # dataset balace using smote
    smote = SMOTE(random_state=42)

    X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)

    # check new distribution
    print(f"Balanced dataset counts: \n {y_train_balanced.value_counts()}")


    return X_train_balanced, y_train_balanced, X_test, y_test
import pandas as pd
import os
import xgboost as xgb

# Load train/test datasets
output_path = r"C:\Users\lenovo\Desktop\churn-pipeline-project\output"
X_test = pd.read_csv(os.path.join(output_path, "X_test.csv"))
y_test = pd.read_csv(os.path.join(output_path, "y_test.csv"))

# Load pre-trained model
model = xgb.XGBClassifier()
model.load_model(r"C:\Users\lenovo\Desktop\churn-pipeline-project\models\xgb_students_churn.model")

# Make predictions
y_pred_proba = model.predict_proba(X_test)[:,1]
y_pred_class = model.predict(X_test)

results = X_test.copy()
results['y_true'] = y_test
results['y_pred_proba'] = y_pred_proba
results['y_pred_class'] = y_pred_class

results.to_csv(os.path.join(output_path, "churn_predictions.csv"), index=False)
print("✅ Churn predictions saved.")

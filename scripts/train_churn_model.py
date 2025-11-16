# =========================================
# train_churn_model.py
# =========================================

import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report

# ================= LOAD SPLIT DATA =================
BASE_DIR = r"C:\Users\lenovo\Desktop\churn-pipeline-project\data"

X_train = pd.read_csv(f"{BASE_DIR}\\X_train.csv")
X_test = pd.read_csv(f"{BASE_DIR}\\X_test.csv")
y_train = pd.read_csv(f"{BASE_DIR}\\y_train.csv").values.ravel()
y_test = pd.read_csv(f"{BASE_DIR}\\y_test.csv").values.ravel()

# ================= SCALE FEATURES =================
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ================= TRAIN MODELS ===================
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=200, random_state=42),
    "XGBoost": XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
}

results = {}

for name, model in models.items():
    print(f"\n🚀 Training {name}...")
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    results[name] = acc
    print(f"✅ {name} Accuracy: {acc:.4f}")

# ================= PICK BEST MODEL ================
best_model_name = max(results, key=results.get)
best_model = models[best_model_name]
best_acc = results[best_model_name]

print(f"\n🏆 Best Model: {best_model_name} (Accuracy: {best_acc:.4f})")

# ================= SAVE BEST MODEL ================
joblib.dump(best_model, f"{BASE_DIR}\\best_model.pkl")
joblib.dump(scaler, f"{BASE_DIR}\\scaler.pkl")

print("💾 Best model and scaler saved successfully!")

# ================= REPORT ========================
print("\n📋 Classification Report:")
y_pred_best = best_model.predict(X_test_scaled)
print(classification_report(y_test, y_pred_best))

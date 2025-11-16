# =========================================
# train_test_split.py
# =========================================

import pandas as pd
from sklearn.model_selection import train_test_split
import os

# ================= CONFIG =================
DATA_PATH = r"C:\Users\lenovo\Desktop\churn-pipeline-project\data\engineered_students.csv"
OUTPUT_DIR = r"C:\Users\lenovo\Desktop\churn-pipeline-project\data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ================= LOAD ====================
df = pd.read_csv(DATA_PATH)
print(f"✅ Loaded dataset with shape: {df.shape}")

# ================= SPLIT ===================
# Target is already encoded (Dropout = 1, Graduate = 0)
X = df.drop("Target_num", axis=1)
y = df["Target_num"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ================= SAVE ====================
X_train.to_csv(os.path.join(OUTPUT_DIR, "X_train.csv"), index=False)
X_test.to_csv(os.path.join(OUTPUT_DIR, "X_test.csv"), index=False)
y_train.to_csv(os.path.join(OUTPUT_DIR, "y_train.csv"), index=False)
y_test.to_csv(os.path.join(OUTPUT_DIR, "y_test.csv"), index=False)

print("💾 Train/test data saved successfully!")

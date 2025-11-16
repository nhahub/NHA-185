import pandas as pd
from sqlalchemy import create_engine
from sklearn.preprocessing import StandardScaler
import os

# -----------------------------
# Step 1: Load data from MySQL
# -----------------------------
engine = create_engine('mysql+pymysql://root:Root@1234@localhost/students_churn_db')
query = open(r"C:\Users\lenovo\Desktop\churn-pipeline-project\sql\02_feature_extraction.sql").read()
df = pd.read_sql(query, engine)

# -----------------------------
# Step 2: Handle missing values
# -----------------------------
df.fillna(df.mean(), inplace=True)

# -----------------------------
# Step 3: Feature scaling
# -----------------------------
numeric_cols = ['total_units_approved', 'total_units_enrolled', 'Tuition_fees_up_to_date', 'Age_at_enrollment']
scaler = StandardScaler()
df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

# -----------------------------
# Step 4: Save preprocessed dataset
# -----------------------------
output_path = r"C:\Users\lenovo\Desktop\churn-pipeline-project\output"
os.makedirs(output_path, exist_ok=True)
df.to_csv(os.path.join(output_path, "preprocessed_data.csv"), index=False)
print("✅ Preprocessing complete. Data saved.")

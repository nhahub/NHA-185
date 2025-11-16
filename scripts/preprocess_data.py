import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote
from sklearn.preprocessing import StandardScaler

# ========================
# CONFIGURATION
# ========================
MYSQL_USER = "root"
MYSQL_PASSWORD = "Root@1234"
MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
DB_NAME = "students_churn_db"

# ========================
# CONNECT TO MYSQL
# ========================
engine = create_engine(
    f"mysql+mysqlconnector://{MYSQL_USER}:{quote(MYSQL_PASSWORD)}@{MYSQL_HOST}:{MYSQL_PORT}/{DB_NAME}"
)

# ========================
# LOAD DATA FROM SQL
# ========================
# Make sure this table/view comes from your feature extraction SQL script
query = "SELECT * FROM student_features"
df = pd.read_sql(query, con=engine)
print(f"✅ Loaded dataset from SQL: {df.shape}")

# ========================
# ENCODE TARGET
# ========================
# Dropout -> 0, Graduate/Enrolled -> 1
df['Target'] = df['Target'].apply(lambda x: 0 if x=='Dropout' else 1)

# ========================
# HANDLE MISSING VALUES (NUMERIC ONLY)
# ========================
numeric_cols = df.select_dtypes(include='number').columns
df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())

# ========================
# SCALE FEATURES (NUMERIC ONLY)
# ========================
features = df.drop(columns=['Target'])
scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)
scaled_df = pd.DataFrame(scaled_features, columns=features.columns)
scaled_df['Target'] = df['Target']

# ========================
# SAVE CLEANED DATA
# ========================
output_path = r"C:\Users\lenovo\Desktop\churn-pipeline-project\data\processed_students.csv"
scaled_df.to_csv(output_path, index=False)
print(f"✅ Preprocessed data saved to {output_path}")

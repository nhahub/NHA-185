import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote

# ========================
# CONFIGURATION
# ========================
CSV_PATH = r"C:\Users\lenovo\Desktop\churn-pipeline-project\data\students_churn_formatted.csv"
MYSQL_USER = "root"
MYSQL_PASSWORD = "Root@1234"
MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
DB_NAME = "students_churn_db"
TABLE_NAME = "students_churn"

# ========================
# LOAD DATA
# ========================
df = pd.read_csv(CSV_PATH)
print(f"✅ Loaded CSV successfully. Shape: {df.shape}")

# 🧹 Clean column names for MySQL
df.columns = (
    df.columns
    .str.strip()
    .str.replace('/', '_', regex=False)
    .str.replace(' ', '_', regex=False)
    .str.replace('(', '', regex=False)
    .str.replace(')', '', regex=False)
)

# ========================
# CONNECT TO MYSQL
# ========================
engine = create_engine(
    f"mysql+mysqlconnector://{MYSQL_USER}:{quote(MYSQL_PASSWORD)}@{MYSQL_HOST}:{MYSQL_PORT}/{DB_NAME}"
)

# ========================
# SAVE TO MYSQL
# ========================
df.to_sql(TABLE_NAME, con=engine, if_exists='replace', index=False)
print("✅ Data uploaded successfully to MySQL!")
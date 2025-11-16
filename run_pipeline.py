import os
import subprocess
import mysql.connector

# =========================
# CONFIGURATION
# =========================
MYSQL_USER = "root"
MYSQL_PASSWORD = "Root@1234"
MYSQL_HOST = "127.0.0.1"

SQL_DIR = r"C:\Users\lenovo\Desktop\churn-pipeline-project\sql"
SCRIPTS_DIR = r"C:\Users\lenovo\Desktop\churn-pipeline-project\scripts"

# =========================
# Helper Function
# =========================
def run_sql_script(filename):
    sql_path = os.path.join(SQL_DIR, filename)
    print(f"⚙️  Running SQL script: {filename}")
    connection = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD
    )
    cursor = connection.cursor()
    with open(sql_path, "r", encoding="utf-8") as f:
        sql_commands = f.read().split(";")
        for command in sql_commands:
            command = command.strip()
            if command:
                cursor.execute(command)
    connection.commit()
    connection.close()
    print(f"✅ Finished running {filename}\n")


def run_python_script(filename):
    print(f"🐍 Running Python script: {filename}")
    subprocess.run(["python", os.path.join(SCRIPTS_DIR, filename)], check=True)
    print(f"✅ Finished {filename}\n")

# =========================
# PIPELINE EXECUTION
# =========================
if __name__ == "__main__":
    print("🚀 Starting Students Churn Data Pipeline\n")

    # 1️⃣ Create the database
    run_sql_script("00_create_dataset.sql")

    # 2️⃣ Clean raw CSV
    run_python_script("clean_format.py")

    # 3️⃣ Load cleaned CSV to MySQL
    run_python_script("load_csv_to_mysql.py")

    # 4️⃣ Run exploratory SQL queries
    run_sql_script("01_explore_data.sql")

    # 5️⃣ Extract features via SQL
    run_sql_script("02_feature_extraction.sql")

    # 6️⃣ Preprocess data
    run_python_script("preprocess_data.py")

    # 7️⃣ Feature engineering
    run_python_script("feature_engineering.py")

    # 8️⃣ Visualize features
    run_python_script("visualize_features.py")

    # 9️⃣ Train/test split
    run_python_script("train_test_split.py")

    # 🔟 Train and predict churn
    run_python_script("predict_churn.py")

    print("🎯 Pipeline completed successfully!")

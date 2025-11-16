import pandas as pd

# ✅ Load raw CSV
df = pd.read_csv(r"C:\Users\lenovo\Desktop\churn-pipeline-project\data\students_churn.csv", sep=';')

# ✅ Clean Target column
df['Target'] = df['Target'].str.replace('"', '')

# ✅ Save cleaned file
df.to_csv(r"C:\Users\lenovo\Desktop\churn-pipeline-project\data\students_churn_formatted.csv", index=False)
print("✅ students_churn_formatted.csv created successfully!")

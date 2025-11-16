import pandas as pd

df = pd.read_csv(r"C:\Users\lenovo\Desktop\churn-pipeline-project\data\processed_students.csv")

# ✅ Create new useful features
df['Avg_Grades'] = (df['Curricular_units_1st_sem_grade'] + df['Curricular_units_2nd_sem_grade']) / 2
df['Approval_Rate'] = (
    (df['Curricular_units_1st_sem_approved'] + df['Curricular_units_2nd_sem_approved']) /
    (df['Curricular_units_1st_sem_enrolled'] + df['Curricular_units_2nd_sem_enrolled']).replace(0, 1)
)

# ✅ Save new engineered dataset
df.to_csv(r"C:\Users\lenovo\Desktop\churn-pipeline-project\data\engineered_students.csv", index=False)
print("✅ Feature engineering completed and saved!")

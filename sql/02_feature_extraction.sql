USE students_churn_db;

DROP VIEW IF EXISTS student_features;

CREATE VIEW student_features AS
SELECT
    Marital_status,
    Application_mode,
    Application_order,
    Course,
    Daytime_evening_attendance,
    Previous_qualification,
    Previous_qualification_grade,
    Nacionality,
    Mothers_qualification,
    Fathers_qualification,
    Mothers_occupation,
    Fathers_occupation,
    Admission_grade,
    Displaced,
    Educational_special_needs,
    Debtor,
    Tuition_fees_up_to_date,
    Gender,
    Scholarship_holder,
    Age_at_enrollment,
    International,
    Curricular_units_1st_sem_credited,
    Curricular_units_1st_sem_enrolled,
    Curricular_units_1st_sem_evaluations,
    Curricular_units_1st_sem_approved,
    Curricular_units_1st_sem_grade,
    Curricular_units_1st_sem_without_evaluations,
    Curricular_units_2nd_sem_credited,
    Curricular_units_2nd_sem_enrolled,
    Curricular_units_2nd_sem_evaluations,
    Curricular_units_2nd_sem_approved,
    Curricular_units_2nd_sem_grade,
    Curricular_units_2nd_sem_without_evaluations,
    Unemployment_rate,
    Inflation_rate,
    GDP,
    Target,

    -- FEATURE EXTRACTION
    (Curricular_units_1st_sem_approved / NULLIF(Curricular_units_1st_sem_enrolled,0)) AS First_sem_pass_rate,
    (Curricular_units_2nd_sem_approved / NULLIF(Curricular_units_2nd_sem_enrolled,0)) AS Second_sem_pass_rate,
    (Curricular_units_1st_sem_grade + Curricular_units_2nd_sem_grade) / 2 AS Average_grade,
    (Curricular_units_1st_sem_enrolled + Curricular_units_2nd_sem_enrolled) AS Total_curricular_units_enrolled,
    (Curricular_units_1st_sem_approved + Curricular_units_2nd_sem_approved) AS Total_curricular_units_approved,
    ((Curricular_units_1st_sem_approved + Curricular_units_2nd_sem_approved) / 
        NULLIF((Curricular_units_1st_sem_enrolled + Curricular_units_2nd_sem_enrolled),0)) AS Overall_pass_rate,
    GREATEST(Displaced, Educational_special_needs) AS Displaced_or_special_needs
FROM students_churn;

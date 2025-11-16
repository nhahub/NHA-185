require('dotenv').config({ path: '/root/my-node-app/.env' });

const ObsClient = require("esdk-obs-nodejs");
const csv = require("csv-parser");
const mysql = require("mysql2/promise");
const { Readable } = require("stream");
const fs = require("fs").promises;

// --- CONFIGURATION from .env ---
const DB_NAME = process.env.DB_NAME;
const TABLE_NAME = "students_churn"; // This remains consistent with your SQL file

const SQL_FILES_SETUP = ["/root/my-node-app/00_create_dataset.sql", "/root/my-node-app/01_explore_data.sql"];
const SQL_FILES_POST_IMPORT = ["/root/my-node-app/02_feature_extraction.sql"];

// 🚨 COLUMN MAPPING: Maps CSV headers (Keys) to SQL column names (Values) 🚨
// This map MUST match the structure of your CSV and your 00_create_dataset.sql table.
const HEADER_MAP = {
    "Marital status": "Marital_status",
    "Application mode": "Application_mode",
    "Application order": "Application_order",
    "Course": "Course",
    "Daytime/evening attendance\t": "Daytime_evening_attendance",
    "Previous qualification": "Previous_qualification",
    "Previous qualification (grade)": "Previous_qualification_grade",
    "Nacionality": "Nacionality",
    "Mother's qualification": "Mothers_qualification",
    "Father's qualification": "Fathers_qualification",
    "Mother's occupation": "Mothers_occupation",
    "Father's occupation": "Fathers_occupation",
    "Admission grade": "Admission_grade",
    "Displaced": "Displaced",
    "Educational special needs": "Educational_special_needs",
    "Debtor": "Debtor",
    "Tuition fees up to date": "Tuition_fees_up_to_date",
    "Gender": "Gender",
    "Scholarship holder": "Scholarship_holder",
    "Age at enrollment": "Age_at_enrollment",
    "International": "International",
    "Curricular units 1st sem (credited)": "Curricular_units_1st_sem_credited",
    "Curricular units 1st sem (enrolled)": "Curricular_units_1st_sem_enrolled",
    "Curricular units 1st sem (evaluations)": "Curricular_units_1st_sem_evaluations",
    "Curricular units 1st sem (approved)": "Curricular_units_1st_sem_approved",
    "Curricular units 1st sem (grade)": "Curricular_units_1st_sem_grade",
    "Curricular units 1st sem (without evaluations)": "Curricular_units_1st_sem_without_evaluations",
    "Curricular units 2nd sem (credited)": "Curricular_units_2nd_sem_credited",
    "Curricular units 2nd sem (enrolled)": "Curricular_units_2nd_sem_enrolled",
    "Curricular units 2nd sem (evaluations)": "Curricular_units_2nd_sem_evaluations",
    "Curricular units 2nd sem (approved)": "Curricular_units_2nd_sem_approved",
    "Curricular units 2nd sem (grade)": "Curricular_units_2nd_sem_grade",
    "Curricular units 2nd sem (without evaluations)": "Curricular_units_2nd_sem_without_evaluations",
    "Unemployment rate": "Unemployment_rate",
    "Inflation rate": "Inflation_rate",
    "GDP": "GDP",
    "Target": "Target",
};


// --- CLIENTS ---

// OBS client (uses environment variables)
const obsClient = new ObsClient({
    access_key_id: process.env.OBS_ACCESS_KEY_ID,
    secret_access_key: process.env.OBS_SECRET_ACCESS_KEY,
    server: process.env.OBS_SERVER
});

// MySQL connection (uses environment variables)
async function connectMySQL(dbName = DB_NAME) {
    const config = {
        host: process.env.MYSQL_HOST,
        user: process.env.MYSQL_USER,
        password: process.env.MYSQL_PASSWORD,
        multipleStatements: true,
    };
    if (dbName) {
        config.database = dbName;
    }
    return mysql.createConnection(config);
}


// --- SQL EXECUTION FUNCTION ---
async function executeSqlFiles(filesToRun, initialConnection = false) {
    let db;
    try {
        db = await connectMySQL(initialConnection ? null : DB_NAME);
        console.log(`MySQL connection established for SQL stage: ${filesToRun.join(', ')}`);

        for (const file of filesToRun) {
            console.log(`Executing SQL file: ${file}...`);
            const sql = await fs.readFile(file, "utf-8");

            await db.query(sql);
        }
        console.log(`SQL files executed successfully for stage: ${filesToRun.join(', ')}`);
    } catch (err) {
        console.error(`Error during SQL file execution of ${filesToRun.join(', ')}:`, err.message);
        throw err;
    } finally {
        if (db) db.end();
    }
}

// --- MAIN IMPORT FUNCTION ---
async function importCSV() {
    let db;
    try {
        // 0a. STAGE 1 (SETUP): Run SQL files for DB/Table creation
        await executeSqlFiles(SQL_FILES_SETUP, true);
        console.log("Database and table structure setup complete. Starting data import...");

        const params = {
            Bucket: process.env.OBS_BUCKET,
            Key: process.env.OBS_KEY
        };

        // 1. Download CSV from OBS
        const res = await obsClient.getObject(params);

        if (res.CommonMsg.Status >= 300) {
            console.error("OBS error:", res.CommonMsg);
            return;
        }

        console.log("Downloaded CSV file from OBS.");

        const stream = Readable.from(res.InterfaceResult.Content);

        // 2. STAGE 2 (IMPORT): Connect to MySQL for data insertion
        db = await connectMySQL(DB_NAME);
        console.log(`Connected to MySQL database '${DB_NAME}' for data import.`);

        // SQL column list derived from the mapping keys
        const SQL_COLUMNS = Object.values(HEADER_MAP).map(h => `\`${h}\``).join(",");
        console.log("SQL target columns:", SQL_COLUMNS);

        // Ordered list of CSV headers (keys of the map)
        const CSV_HEADER_ORDER = Object.keys(HEADER_MAP);
        let importCount = 0;

        stream
            .pipe(csv())
            .on("data", async row => {
                stream.pause();

                // Create ordered array of values using the CSV headers
                const values = CSV_HEADER_ORDER.map(csvHeader => {
                    return row[csvHeader];
                });

                const placeholders = values.map(() => "?").join(",");

                const sql = `INSERT INTO ${TABLE_NAME} (${SQL_COLUMNS}) VALUES (${placeholders})`;

                try {
                    await db.execute(sql, values);
                    importCount++;
                } catch (err) {
                    console.error("Insert error:", err.message);
                } finally {
                    stream.resume();
                }
            })
            .on("end", async () => {
                console.log(`CSV import completed. ${importCount} rows imported.`);
                db.end();

                // 3. STAGE 3 (POST-IMPORT): Run the final feature extraction SQL file
                console.log("Starting feature extraction view creation...");
                await executeSqlFiles(SQL_FILES_POST_IMPORT, false);
                console.log("Feature extraction view created successfully. Process finished.");
            })
            .on("error", (err) => {
                console.error("CSV Stream Error:", err);
                if (db) db.end();
            });

    } catch (err) {
        console.error("Fatal Error:", err);
        if (db) db.end();
    }
}

// Start the entire process
importCSV();
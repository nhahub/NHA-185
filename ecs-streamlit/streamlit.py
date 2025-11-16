
Conversation with Gemini
import streamlit as st

import pandas as pd

import numpy as np

import joblib

import requests

from io import BytesIO

from typing import Dict, Any

from sklearn.preprocessing import StandardScaler

from sklearn.metrics.pairwise import cosine_similarity

import json

import plotly.express as px

from google import genai



# -----------------------------

# Page Configuration

# -----------------------------

st.set_page_config(page_title="Student Churn Predictor", layout="wide")

st.title("Student Churn Predictor")

st.markdown(

    "Predict academic outcomes (Dropout, Enrolled, Graduate) and get AI-driven retention advice."

)



# -----------------------------

# URLs and Resources

# -----------------------------

MODEL_URL = "https://datasets-cffe.obs.ap-southeast-3.myhuaweicloud.com/meta_model_v1/model/best_model.pkl"

SCALER_URL = "https://datasets-cffe.obs.ap-southeast-3.myhuaweicloud.com/meta_model_v1/model/scaler.pkl"

CSV_URL = "https://datasets-cffe.obs.ap-southeast-3.myhuaweicloud.com/students_churn.csv"



FEATURE_DEFAULTS = {

    'Marital status': 1, 'Application mode': 17, 'Application order': 3, 'Course': 9070,

    'Daytime/evening attendance': 1, 'Previous qualification': 1, 'Previous qualification (grade)': 133.0,

    'Nacionality': 1, "Mother's qualification": 19, "Father's qualification": 19,

    "Mother's occupation": 5, "Father's occupation": 9, 'Admission grade': 130.0,

    'Displaced': 1, 'Educational special needs': 0, 'Debtor': 0, 'Tuition fees up to date': 1,

    'Gender': 1, 'Scholarship holder': 0, 'Age at enrollment': 21, 'International': 0,

    'Curricular units 1st sem (credited)': 0, 'Curricular units 1st sem (enrolled)': 6,

    'Curricular units 1st sem (evaluations)': 8, 'Curricular units 1st sem (approved)': 6,

    'Curricular units 1st sem (grade)': 12.0, 'Curricular units 1st sem (without evaluations)': 0,

    'Curricular units 2nd sem (credited)': 0, 'Curricular units 2nd sem (enrolled)': 6,

    'Curricular units 2nd sem (evaluations)': 8, 'Curricular units 2nd sem (approved)': 6,

    'Curricular units 2nd sem (grade)': 12.0, 'Curricular units 2nd sem (without evaluations)': 0,

    'Unemployment rate': 10.8, 'Inflation rate': 1.4, 'GDP': 1.74

}



DATASET_INTUITIONS = (

    "- Lower Admission Grades and 1st semester grades increase Dropout risk.\n"

    "- Debtors or unpaid Tuition Fees are at higher risk.\n"

    "- Older students (25+) face higher pressures.\n"

    "- 0 approved units in 1st semester indicates extremely high risk.\n"

    "- Financial/contextual factors often outweigh initial academic performance.\n"

)



# -----------------------------

# Load resources

# -----------------------------

@st.cache_resource

def load_resource(url: str, resource_name: str):

    try:

        with st.spinner(f"Loading {resource_name}..."):

            response = requests.get(url, timeout=120)

            response.raise_for_status()

            if resource_name == "CSV Data":

                df = pd.read_csv(BytesIO(response.content), delimiter=';')

                df.columns = df.columns.str.strip()

                return df

            return joblib.load(BytesIO(response.content))

    except Exception as e:

        st.error(f"Error loading {resource_name}: {e}")

        return None



model = load_resource(MODEL_URL, "Prediction Model")

scaler = load_resource(SCALER_URL, "Feature Scaler")

csv_data = load_resource(CSV_URL, "CSV Data")



if model is None or scaler is None or csv_data is None:

    st.error("Cannot proceed without model, scaler, and CSV data.")

    st.stop()



# -----------------------------

# API Keys / System Instruction

# -----------------------------

try:
    # Load secrets from Streamlit's st.secrets
    HUAWEI_TOKEN = st.secrets["HUAWEI_TOKEN"]
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError as e:
    st.error(f"Missing required API key in st.secrets: {e}. Please add 'HUAWEI_TOKEN' and 'GEMINI_API_KEY' to your Streamlit secrets file.")
    # Stop the app if keys are missing to prevent API call errors
    st.stop()

HUAWEI_API_URL = "https://api-ap-southeast-1.modelarts-maas.com/v1/chat/completions"

SYSTEM_INSTRUCTION = (

    "You are an AI Student Retention Counselor. Be helpful, encouraging, "

    "and provide clear, actionable advice related to student success and academic retention. "

    "Crucially, DO NOT output raw Python dictionaries, JSON objects, or complex data structures (like the input vector or similar student data) in your final response. "

    "Translate all technical data into readable, human-friendly text for the student or advisor."

)



# -----------------------------

# Helper Functions

# -----------------------------

def query_ai(messages: list, model_name: str) -> str:

    try:

        full_messages = [{"role": "system", "content": SYSTEM_INSTRUCTION}] + messages

        response = None

       

        if model_name.lower() in ["deepseek-v3.1", "qwen3-32b"]:

            headers = {"Content-Type": "application/json"}

            if model_name.lower() == "deepseek-v3.1":

                headers["Authorization"] = f"Bearer {HUAWEI_TOKEN}"

            else:

                headers["Authorization"] = f"Bearer {HUAWEI_TOKEN}"

            payload = {

                "model": model_name,

                "messages": full_messages,

                "temperature": 0.7, "max_tokens": 1024

            }

            response = requests.post(HUAWEI_API_URL, headers=headers, json=payload, timeout=60)

        elif model_name.lower() == "gemini":

            # Gemini-specific API call using the recommended structure

            # Note: Using text-bison-001 as in the original code, but often gemini-pro is preferred for chat. Sticking to the original provided model name here.

           

            # Reconstruct the prompt for text-bison (non-chat model)

            prompt_text = f"SYSTEM: {SYSTEM_INSTRUCTION}\n\n" + "\n".join([f"**{msg['role'].title()}**: {msg['content']}" for msg in messages])

                   

            client = genai.Client(api_key=GEMINI_API_KEY)



            response = client.models.generate_content(

                model="gemini-2.5-flash", contents=prompt_text

            )

        else:

            return f"Unknown model: {model_name}"



       

       

        if model_name.lower() in ["deepseek-v3.1", "qwen3-32b"]:

            response.raise_for_status()

            result = response.json()

            if "choices" in result and result["choices"]:

                return result["choices"][0]["message"]["content"]

            return f"Unexpected response from {model_name}: {json.dumps(result, indent=2)}"

        elif model_name.lower() == "gemini":

            try:

                return response.text

            except (e):

                return f"Unexpected Gemini response: {e}"

           

                # Accessing 'output' for text-bison response

    except Exception as e:

        return f"Error querying {model_name}: {e}"



def retrieve_similar_rows_numeric(input_vector: Dict[str, Any], csv_df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:

    feature_cols = [

        'Age at enrollment','Admission grade','Marital status','Course',

        'Daytime/evening attendance','Debtor','Tuition fees up to date',

        'Scholarship holder','Curricular units 1st sem (approved)',

        'Curricular units 1st sem (grade)'

    ]

    csv_features = csv_df[feature_cols].fillna(0)

    input_row = pd.DataFrame([{k: input_vector[k] for k in feature_cols}])

    combined = pd.concat([csv_features, input_row], ignore_index=True)

    scaler_local = StandardScaler()

    combined_scaled = scaler_local.fit_transform(combined)

    input_vec_scaled = combined_scaled[-1].reshape(1, -1)

    csv_scaled = combined_scaled[:-1]

    similarity = cosine_similarity(input_vec_scaled, csv_scaled).flatten()

    top_indices = similarity.argsort()[-top_n:][::-1]

    return csv_df.iloc[top_indices]



def create_dashboard(df: pd.DataFrame):

    st.header("Interactive Data Dashboard")

    fig1 = px.histogram(df, x='Target',

                         title='Distribution of Academic Outcomes',

                         color='Target',

                         color_discrete_map={'Dropout': 'red', 'Enrolled': 'orange', 'Graduate': 'green'})

    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("---")

    col_dashboard_1, col_dashboard_2 = st.columns(2)

    with col_dashboard_1:

        fig2 = px.box(df, x='Target', y='Admission grade',

                      title='Admission Grade by Outcome',

                      color='Target',

                      color_discrete_map={'Dropout': 'red', 'Enrolled': 'orange', 'Graduate': 'green'})

        st.plotly_chart(fig2, use_container_width=True)

    with col_dashboard_2:

        fig3 = px.histogram(df, x='Age at enrollment',

                            color='Target',

                            barmode='overlay',

                            title='Age Distribution at Enrollment by Outcome',

                            color_discrete_map={'Dropout': 'red', 'Enrolled': 'orange', 'Graduate': 'green'},

                            opacity=0.6)

        st.plotly_chart(fig3, use_container_width=True)

    df_fees = df.copy()

    df_fees['Tuition fees status'] = df_fees['Tuition fees up to date'].apply(lambda x: 'Paid' if x==1 else 'Unpaid')

    fig4 = px.bar(df_fees, x='Target', color='Tuition fees status',

                  title='Outcome by Tuition Fees Status',

                  barmode='group',

                  color_discrete_map={'Paid': 'green', 'Unpaid': 'red'})

    st.plotly_chart(fig4, use_container_width=True)



# -----------------------------

# Session State

# -----------------------------

if "chat_history" not in st.session_state:

    st.session_state["chat_history"] = []

if "last_predicted_outcome" not in st.session_state:

    st.session_state["last_predicted_outcome"] = None

if "last_selected_model" not in st.session_state:

    st.session_state["last_selected_model"] = None

if "chat_input" not in st.session_state:

    st.session_state["chat_input"] = ""



# -----------------------------

# Tabs Layout

# -----------------------------

prediction_tab, dashboard_tab = st.tabs(["Student Prediction & AI Advice", "Interactive Data Dashboard"])



# -----------------------------

# Prediction Tab

# -----------------------------

with prediction_tab:

    # --- Input Form ---

    with st.form("student_data_form", clear_on_submit=False):

        st.header("Student Profile")

        col1, col2 = st.columns(2)

        with col1:

            age_at_enrollment = st.number_input("Age at Enrollment",18,80,25)

            admission_grade = st.number_input("Admission Grade",0.0,200.0,130.0)

            marital_status = st.selectbox("Marital Status", [("Single",1),("Married",2),("Divorced",4),("Other",6)], format_func=lambda x:x[0])

            course_type = st.selectbox("Course Type", [("Informatics",9070),("Design",171),("Education",9254),("Other",9999)], format_func=lambda x:x[0])

            attendance = st.radio("Day/Evening", [("Daytime",1),("Evening",0)], format_func=lambda x:x[0])

        with col2:

            debtor = st.checkbox("Debtor", False)

            fees_up_to_date = st.checkbox("Tuition Fees Up to Date", True)

            scholarship_holder = st.checkbox("Scholarship Holder", False)

            approved_units_1st = st.number_input("1st Sem Units Approved",0,30,6)

            grade_1st_sem = st.number_input("1st Sem Grade",0.0,20.0,12.0)

            unemployment_rate = st.number_input("Unemployment Rate (%)",0.0,20.0,10.8)

           

        st.markdown("---")

        selected_model = st.selectbox("Choose AI Model", ["deepseek-v3.1","qwen3-32b","gemini"])

        submitted = st.form_submit_button("Predict & Analyze")



    if submitted:

        # Clear chat history and set up initial state

        st.session_state['chat_history'] = []

        st.session_state['last_predicted_outcome'] = None

        st.session_state['last_selected_model'] = selected_model

        st.success("Generating prediction & AI analysis...")

       

        try:

            # --- Prepare Input Vector ---

            input_vector = FEATURE_DEFAULTS.copy()

            input_vector.update({

                'Age at enrollment': age_at_enrollment,

                'Admission grade': admission_grade,

                'Marital status': marital_status[1],

                'Course': course_type[1],

                'Daytime/evening attendance': attendance[1],

                'Debtor': int(debtor),

                'Tuition fees up to date': int(fees_up_to_date),

                'Scholarship holder': int(scholarship_holder),

                'Curricular units 1st sem (approved)': approved_units_1st,

                'Curricular units 1st sem (grade)': grade_1st_sem,

                'Unemployment rate': unemployment_rate

            })



            df_pred = pd.Series(input_vector).to_frame().T

            df_pred['Avg_Grades'] = (df_pred['Curricular units 1st sem (grade)'] + df_pred['Curricular units 2nd sem (grade)']) / 2

            denominator = df_pred['Curricular units 1st sem (enrolled)'] + df_pred['Curricular units 2nd sem (enrolled)']

            df_pred['Approval_Rate'] = (df_pred['Curricular units 1st sem (approved)'] + df_pred['Curricular units 2nd sem (approved)']) / denominator.replace(0,1)

            scaled_data = scaler.transform(df_pred)

            prediction_index = model.predict(scaled_data)[0]

            label_map = {0:"Dropout",1:"Graduate",2:"Enrolled"}

            predicted_outcome = label_map.get(prediction_index,"Unknown Outcome")



            st.subheader("Prediction Result")

            if predicted_outcome=="Dropout": st.error(predicted_outcome)

            elif predicted_outcome=="Enrolled": st.warning(predicted_outcome)

            else: st.success(predicted_outcome)



            # --- Retrieve Similar Students ---

            similar_students = retrieve_similar_rows_numeric(input_vector, csv_data)

            rag_context_data = similar_students.to_dict(orient='records')



            st.session_state['last_predicted_outcome'] = predicted_outcome

           

            # --- Initial AI Analysis ---

            # The full context for RAG is sent, but the user only sees the result.

            initial_prompt_content = (

                f"Predicted outcome: {predicted_outcome}\n"

                f"Student profile:\n{json.dumps(input_vector, indent=2)}\n\n"

                f"Dataset intuitions:\n{DATASET_INTUITIONS}\n\n"

                f"Top similar historical students:\n{json.dumps(rag_context_data, indent=2)}\n\n"

                "Provide detailed initial analysis and 3 actionable, personalized retention strategies."

            )

           

            # Add the full RAG context as the first user message (not displayed to user)

            st.session_state['chat_history'].append({"role": "user", "content": initial_prompt_content})

           

            messages = [{"role": "user", "content": initial_prompt_content}]

            with st.spinner(f"Generating initial {selected_model} analysis..."):

                ai_analysis = query_ai(messages, model_name=selected_model)

               

            # Add the AI's first response

            st.session_state['chat_history'].append({"role": "assistant", "content": ai_analysis})



        except Exception as e:

            st.error(f"Error during prediction or initial analysis: {e}")



    # -----------------------------

    # Chat Interface (Styled with st.chat_message)

    # -----------------------------

   

    # Only show chat if a prediction has been made

    if st.session_state['last_predicted_outcome']:



        def submit_chat():

            user_input = st.session_state["chat_input_key"]

            if user_input.strip():

                selected_model = st.session_state['last_selected_model']

               

                # Append new user message (only the text, not the RAG context)

                st.session_state['chat_history'].append({"role": "user", "content": user_input.strip()})

               

                # Prepare messages to send (include RAG context from index 0)

                messages_to_send = [

                    {"role": "user", "content": st.session_state['chat_history'][0]['content']}

                ] + st.session_state['chat_history'][1:] # Subsequent turns

               

                with st.spinner("AI is thinking..."):

                    # Use the RAG context in the conversation history

                    chat_response = query_ai(messages_to_send, model_name=selected_model)

                st.session_state['chat_history'].append({"role": "assistant", "content": chat_response})

                st.session_state["chat_input_key"] = ""

                # Rerun to update chat display

                st.rerun()



        st.markdown("---")

        st.subheader("AI Counselor Chat")



        # Display chat history in reverse order for better UX (newest at bottom)

        chat_display_container = st.container(height=300, border=True)

        with chat_display_container:

            for i, msg in enumerate(st.session_state['chat_history']):

                role = msg["role"]

                content = msg["content"]



                if i == 0 and role == "user":

                    # This is the initial RAG prompt. We skip showing the raw data

                    # and just acknowledge the action.

                    with st.chat_message("user"):

                         st.caption("Initial student data submitted for analysis.")

                    continue



                if role == "user":

                    with st.chat_message("user"):

                        st.markdown(content)

                else:

                    with st.chat_message("assistant"):

                        st.markdown(content)

       

        # Chat input at the bottom

        st.text_input("Ask for more advice or clarification...", key="chat_input_key", on_change=submit_chat)





# -----------------------------

# Dashboard Tab

# -----------------------------

with dashboard_tab:

    if csv_data is not None:

        create_dashboard(csv_data)

    else:

        st.warning("Dashboard data could not be loaded.")
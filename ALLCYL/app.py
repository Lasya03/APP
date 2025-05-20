import streamlit as st
import pickle
import os
import numpy as np
st.set_page_config(
    page_title="Cylinder Cost Prediction",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Feature configuration per model
model_features = {
    'HD': ['Bore','Stroke','RPC','Rod','R bearing','B bearing','Block','Val A'],
    'HDE': ['Bore','Stroke','RPC','Rod','R bearing','B bearing','Block','Val A'],
    'HDI': ['Bore','Stroke','RPC','Rod','R bearing','B bearing','Block','Val A'],
    'LD': ['Bore','Stroke','RPC','Rod','R bearing','B bearing','Block','Val A'],
    'LDH': ['Bore','Stroke','RPC','Rod','Block','Val A'],
    'MD': ['Bore','Stroke','RPC','Rod','R bearing','B bearing','Block','Val A'],
    'NR': ['Bore','Stroke','RPC','Rod','R bearing'],
    'H': ['Bore','Stroke','RPC','Rod','R bearing','B bearing','Block','Val A'],
    'L': ['Bore','Stroke','RPC','Rod','Block'],
    'M': ['Bore','Stroke','RPC','Rod','R bearing','B bearing','Block','Val A'],
    'N': ['Bore','Stroke','RPC','Rod','R bearing','B bearing','Block','Val A'],
}

numerical_features = ['Bore','Stroke','RPC','Rod']
yesno_features = ['R bearing','B bearing','Block','Val A','Val B']

def load_model(model_key):
    filename = os.path.join(os.path.dirname(__file__), f"{model_key}_model.pkl")
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)
    else:
        st.error(f"Model file {filename} not found!")
        return None

st.sidebar.title("Model Selection")
model_key = st.sidebar.selectbox("Select Model Type", list(model_features.keys()))

model = load_model(model_key)
if model is None:
    st.stop()
    
st.title("Cylinder Cost Prediction - Columbus")

def synced_input(label, min_val, max_val, default):
    col_slider, col_input = st.columns([2, 1])
    with col_slider:
        slider_val = st.slider(label, min_value=min_val, max_value=max_val, value=default, key=label+"slider")
    with col_input:
        input_val = st.number_input(f"{label} value", min_value=min_val, max_value=max_val, value=slider_val, key=label+"input")
    return input_val if input_val != slider_val else slider_val

col1, col2 = st.columns(2)
inputs = {}

with col1:
    bore = synced_input("Bore", 0, 300, 100)
    stroke = synced_input("Stroke", 0, 300, 50)
    rpc = synced_input("RPC", 0, 100, 20)
    rod = synced_input("Rod", 0, bore, min(30, bore))
with col2:
    r_bearing = st.radio("R bearing", ["No", "Yes"])
    b_bearing = st.radio("B bearing", ["No", "Yes"])
    block = st.radio("Block", ["No", "Yes"])
    val_a = st.radio("Val A", ["No", "Yes"])
    

# Add inputs to dictionary
inputs['Bore'] = bore
inputs['Stroke'] = stroke
inputs['RPC'] = rpc
inputs['Rod'] = rod
inputs['R bearing'] = 1 if r_bearing == 'Yes' else 0
inputs['B bearing'] = 1 if b_bearing == 'Yes' else 0
inputs['Val A'] = 1 if val_a == 'Yes' else 0
inputs['Block'] = 1 if block == 'Yes' else 0

# Custom feature engineering
if model_key in ['HD', 'HDE', 'HDI']:
    inputs['Bore2'] = inputs['Bore'] ** 2
    inputs['Bore_Rod'] = inputs['Bore'] * inputs['Rod']
    inputs['RPC_Bore'] = inputs['RPC'] * inputs['Bore']
    if model_key == 'HDI':
        inputs['Bore_stroke'] = inputs['Bore'] * inputs['Stroke']

elif model_key == 'LDH':
    inputs['Bore_stroke'] = inputs['Bore'] * inputs['Stroke']
    inputs['Bore_Rod'] = inputs['Bore'] * inputs['Rod']
    inputs['RPC_Bore'] = inputs['RPC'] * inputs['Bore']
    inputs['Stroke_Rod'] = inputs['Stroke'] * inputs['Rod']

elif model_key == 'MD':
    inputs['Bore2'] = inputs['Bore'] ** 2
    inputs['Bore_RPC'] = inputs['Bore'] * inputs['RPC']
    inputs['Bore_Stroke'] = inputs['RPC'] * inputs['Stroke']
    inputs['Bore_Rod'] = inputs['Bore'] * inputs['Rod']

elif model_key == 'NR':
    inputs['RPC2'] = inputs['RPC'] ** 2
    inputs['Bore_RPC'] = inputs['Bore'] * inputs['RPC']
    inputs['RPC_Stroke'] = inputs['RPC'] * inputs['Stroke']
    inputs['Stroke2'] = inputs['Stroke'] ** 2
    inputs['RPC_Rod'] = inputs['RPC'] * inputs['Rod']

elif model_key == 'H':
    inputs['RPC2'] = inputs['RPC'] ** 2
    inputs['Bore_Rod'] = inputs['Bore'] * inputs['Rod']
    inputs['RPC_Bore'] = inputs['RPC'] * inputs['Bore']
    inputs['Bore2'] = inputs['Bore'] ** 2
    inputs['RPC_Rod'] = inputs['RPC'] * inputs['Rod']

elif model_key == 'L':
    inputs['Bore_RPC'] = inputs['Bore'] * inputs['RPC']
    inputs['Bore_Stroke'] = inputs['Bore'] * inputs['Stroke']
    inputs['Bore2'] = inputs['Bore'] ** 2
    inputs['Stroke_Rod'] = inputs['Stroke'] * inputs['Rod']

elif model_key == 'M':
    inputs['Bore_Stroke'] = inputs['Bore'] * inputs['Stroke']
    inputs['Bore_Rod'] = inputs['Bore'] * inputs['Rod']
    inputs['RPC_Bore'] = inputs['RPC'] * inputs['Bore']
    inputs['Bore2'] = inputs['Bore'] ** 2
    inputs['RPC_Rod'] = inputs['RPC'] * inputs['Rod']

# Remap yes/no feature names to match training column names
input_name_mapping = {
    'R bearing': 'R bearing_Y',
    'B bearing': 'B bearing_Y',
    'Block': 'Block_Y',
    'Val A': 'Val A_Y',
    'Val B': 'Val B_Y'
}

remapped_inputs = {}
for k, v in inputs.items():
    remapped_inputs[input_name_mapping.get(k, k)] = v

# Ensure all features expected by model are present
model_input = [remapped_inputs.get(f, 0) for f in model.feature_names_]
# Predict and show result
predicted_cost = np.expm1(model.predict([model_input])[0])
st.markdown(f"### Predicted Cost: **$ {predicted_cost:.2f}**")

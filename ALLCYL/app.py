import streamlit as st
import pickle
import os
import numpy as np

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
required_features = model_features.get(model_key, [])
optional_features = [f for f in yesno_features if f not in required_features]

st.sidebar.markdown(f"**Model Selected:** {model_key}")
if optional_features:
    st.sidebar.markdown("**Note:** Optional features for this model:")
    for feat in optional_features:
        st.sidebar.markdown(f"- {feat}")
else:
    st.sidebar.markdown("*All yes/no features are required for this model.*")

model = load_model(model_key)
if model is None:
    st.stop()

st.title("Cylinder Cost Prediction - Columbus")
col1, col2 = st.columns(2)
inputs = {}

feature_ranges = {
    'Bore': (0.0, 20.0),
    'Stroke': (0.0, 500.0),
    'RPC': (0.0, 500.0),
    'Rod': (0.0, 20.0)
}

with col1:
    for feat in numerical_features:
        col_slider, col_input, col_enable = st.columns([3, 2, 1])
        is_required = feat in required_features
        enable = st.session_state.get(f"enable_slider_{feat}", is_required)

        with col_enable:
            if not is_required:
                enable = st.checkbox("", key=f"enable_slider_{feat}", help="Enable input")

        min_val, max_val = feature_ranges.get(feat, (0.0, 1000.0))

        with col_slider:
            val_slider = st.slider(
                feat,
                min_value=min_val,
                max_value=max_val,
                value=(min_val + max_val) / 2,
                step=0.1,
                key=f"{feat}_slider",
                disabled=not enable
            )

        with col_input:
            val_text = st.text_input(
                f"{feat}",
                value="",
                key=f"{feat}_txt",
                disabled=not enable
            )

        try:
            inputs[feat] = float(val_text) if val_text else float(val_slider)
        except:
            inputs[feat] = float(val_slider)

with col2:
    for feat in yesno_features:
        col_dropdown, col_input, col_enable = st.columns([3, 2, 1])
        is_required = feat in required_features
        enable = st.session_state.get(f"enable_dropdown_{feat}", is_required)

        with col_enable:
            if not is_required:
                enable = st.checkbox("", key=f"enable_dropdown_{feat}", help="Enable input")

        with col_dropdown:
            option = st.selectbox(
                feat,
                ['No', 'Yes'],
                key=f"{feat}_dropdown",
                disabled=not enable
            )
            inputs[feat] = 1 if option == 'Yes' and enable else 0

        with col_input:
            extra_cost = st.text_input(
                f"{feat} Cost",
                value="",
                key=f"{feat}_extra",
                disabled=not enable
            )
            try:
                inputs[feat + '_extra_cost'] = float(extra_cost) if extra_cost else 0.0
            except:
                inputs[feat + '_extra_cost'] = 0.0

# Add custom features for specific models
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

input_name_mapping = {
    'R bearing': 'R bearing_Y',
    'B bearing': 'B bearing_Y',
    'Block': 'Block_Y',
    'Val A': 'Val A_Y',
    'Val B': 'Val B_Y'
}

remapped_inputs = {}
for k, v in inputs.items():
    mapped_key = input_name_mapping.get(k, k)
    remapped_inputs[mapped_key] = v

model_input = [remapped_inputs.get(f, 0) for f in model.feature_names_]
predicted_cost = np.expm1(model.predict([model_input])[0])
manual_addition = sum(inputs.get(f + "_extra_cost", 0) for f in yesno_features if f not in required_features)
total_cost = predicted_cost + manual_addition

st.markdown(f"### 🔍 Predicted Cost: **$ {total_cost:.2f}**")

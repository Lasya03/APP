import streamlit as st
import pickle
import os
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
# Let user select model type
model_key = st.sidebar.selectbox("Select Model Type", list(model_features.keys()))
# Define required_features based on model_key
required_features = model_features.get(model_key, [])
optional_features = [f for f in yesno_features if f not in required_features]

# Sidebar message
st.sidebar.markdown("### 📌 Model Guidance")
st.sidebar.markdown(f"**Model Selected:** `{model_key}`")

if optional_features:
    st.sidebar.markdown("**Note:** The following features are *not required* for this model:")
    for feat in optional_features:
        st.sidebar.markdown(f"- {feat}")
    st.sidebar.markdown(
        "*You can still add costs for them manually by enabling the checkbox and entering a value.*"
    )
else:
    st.sidebar.markdown("*All yes/no features are required for this model.*")

# Load the model
def load_model(model_key):
    filename = os.path.join(os.path.dirname(__file__), f"{model_key}_model.pkl")
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)
    else:
        st.error(f"Model file {filename} not found!")
        return None
model = load_model(model_key)
if model is None:
    st.error(f"Model file {model_key}_model.pkl not found!")
    st.stop()
# Layout
st.title(f"Cylinder Cost Prediction-Columbus")
col1, col2 = st.columns(2)
inputs = {}
# Column 1: Numerical features with slider and input box side by side
with col1:
    for feat in numerical_features:
        col_slider, col_input, col_enable = st.columns([3, 2, 1])  # Add third column for checkbox
        is_required = feat in required_features
        # Checkbox to enable/disable optional feature
        enable = st.session_state.get(f"enable_slider_{feat}", is_required)
        with col_enable:
            if not is_required:
                enable = st.checkbox("", key=f"enable_slider_{feat}", help="Enable input")
        with col_slider:
            val_slider = st.slider(
                feat,
                min_value=0.0,
                max_value=1000.0,
                value=100.0,
                step=1.0,
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
        # Prioritize text input if entered, otherwise use slider
        try:
            inputs[feat] = float(val_text) if val_text else float(val_slider)
        except:
            inputs[feat] = float(val_slider)
# Column 2: Yes/No features with dropdown and input box side by side
with col2:
    for feat in yesno_features:
        col_dropdown, col_input, col_enable = st.columns([3, 2, 1])  # Add third column for checkbox
        is_required = feat in required_features
        # Checkbox to enable/disable optional feature
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
# Create a mapping from user-friendly names to model's expected feature names
model_feature_names = model.feature_names_
# Create a mapping for user-friendly names to model feature names
input_name_mapping = {
    'R bearing': 'R bearing_Y',
    'B bearing': 'B bearing_Y',
    'Block': 'Block_Y',
    'Val A': 'Val A_Y',
    'Val B': 'Val B_Y'
}
# Remap inputs dictionary to match model's feature names
remapped_inputs = {}
for k, v in inputs.items():
    mapped_key = input_name_mapping.get(k, k)  # Use mapped key if it exists, else the original
    remapped_inputs[mapped_key] = v
# Ensure the remapped inputs include all the required features
model_input = [remapped_inputs.get(f, 0) for f in model_feature_names]
# Prediction
predicted_cost = model.predict([model_input])[0]
# Add manual costs if there are any
manual_addition = sum(inputs.get(f + "_extra_cost", 0) for f in yesno_features if f not in required_features)
total_cost = predicted_cost + manual_addition
st.markdown(f"### 🔍 Predicted Cost: **$ {total_cost:.2f}**")

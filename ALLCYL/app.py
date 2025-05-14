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
# Info message
if 'Val B' not in required_features:
    st.info(f"⚠️ For {model_key}, the ML model does not consider 'Val B'. You can manually add its cost by double-clicking its input box.")
# Layout
st.title(f"Cylinder Cost Prediction-Columbus")
col1, col2 = st.columns(2)
inputs = {}
# Column 1: Numerical features with slider and input box side by side
with col1:
    st.subheader("Numerical Inputs")
    for feat in numerical_features:
        col_slider, col_input = st.columns([3, 2])  # Adjust the column ratio as needed
        with col_slider:
            if feat in required_features:
                # Create slider for numerical features
                val = st.slider(feat, min_value=0.0, max_value=1000.0, value=100.0, step=1.0, key=feat)
                inputs[feat] = val
            else:
                # Disable slider for non-required features
                st.slider(feat, min_value=0.0, max_value=1000.0, value=100.0, step=1.0, key=feat, disabled=True)

        with col_input:
            if feat in required_features:
                # Create input box for numerical features
                val = st.text_input(f"{feat} (Optional)", value="", key=feat)
                inputs[feat] = float(val) if val else 0.0
            else:
                # Disable input box for non-required features
                val = st.text_input(f"(Disabled) {feat} (Optional)", value="", key=feat, disabled=True)
                inputs[feat] = float(val) if val else 0.0
# Column 2: Yes/No features with dropdown and input box side by side
with col2:
    st.subheader("Yes/No Inputs")
    for feat in yesno_features:
        col_dropdown, col_input = st.columns([3, 2])  # Adjust the column ratio as needed
        with col_dropdown:
            if feat in required_features:
                # Dropdown for Yes/No features
                option = st.selectbox(feat, ['No', 'Yes'], key=feat)
                inputs[feat] = 1 if option == 'Yes' else 0
            else:
                # Disable dropdown for non-required features
                option = st.selectbox(feat, ['No', 'Yes'], key=feat, disabled=True)
                inputs[feat] = 0
        with col_input:
            if feat in required_features:
                # Optional input box for additional cost
                extra_cost = st.text_input(f"(Optional) {feat} Cost", value="", key=feat+"_extra")
                try:
                    inputs[feat + '_extra_cost'] = float(extra_cost) if extra_cost else 0.0
                except:
                    inputs[feat + '_extra_cost'] = 0.0
            else:
                # Disable input box for extra cost for non-required features
                extra_cost = st.text_input(f"(Disabled) {feat} Cost", value="", key=feat+"_extra", disabled=True)
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

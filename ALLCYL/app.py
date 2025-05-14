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
    filename = f"{model_key}_model.pkl"
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
st.title("🔧 Cost Prediction App")
col1, col2 = st.columns(2)
inputs = {}

# Column 1: Numerical features
with col1:
    st.subheader("Numerical Inputs")
    for feat in numerical_features:
        if feat in required_features:
            val = st.slider(feat, min_value=0.0, max_value=1000.0, value=100.0, step=1.0, key=feat)
            inputs[feat] = val
        else:
            val = st.text_input(f"(Optional) {feat}", value="", key=feat)
            inputs[feat] = float(val) if val else 0.0

# Column 2: Yes/No features
with col2:
    st.subheader("Yes/No Inputs")
    for feat in yesno_features:
        if feat in required_features:
            option = st.selectbox(feat, ['No', 'Yes'], key=feat)
            inputs[feat] = 1 if option == 'Yes' else 0
        else:
            inputs[feat] = 0
            extra_cost = st.text_input(f"(Optional) {feat} Cost", value="", key=feat+"_extra")
            try:
                inputs[feat + '_extra_cost'] = float(extra_cost) if extra_cost else 0.0
            except:
                inputs[feat + '_extra_cost'] = 0.0

# Prediction
model_input = [inputs.get(f, 0) for f in required_features]
predicted_cost = model.predict([model_input])[0]

# Add extra cost manually if any
manual_addition = sum(inputs.get(f + "_extra_cost", 0) for f in yesno_features if f not in required_features)
total_cost = predicted_cost + manual_addition

st.markdown(f"### 🔍 Predicted Cost: **₹ {total_cost:.2f}**")

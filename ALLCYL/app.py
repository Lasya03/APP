import streamlit as st
import pickle
import os

# -------------------
# MODEL FEATURES MAP
# -------------------
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
    'N': ['Bore','Stroke','RPC','Rod','R bearing','B bearing','Block','Val A']
}

numerical_features = ['Bore','Stroke','RPC','Rod']
yesno_features = ['R bearing','B bearing','Block','Val A','Val B']

# -------------------
# LOAD MODEL
# -------------------
@st.cache_resource
def load_model(model_name):
    filename = f"{model_name}_model.pkl"
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            return pickle.load(f)
    else:
        st.error(f"Model file {filename} not found!")
        return None

# -------------------
# MAIN APP
# -------------------
st.sidebar.title("Model Selection")
model_type = st.sidebar.selectbox("Select Model Type", list(model_features.keys()))
model_key = model_type  # this matches keys like 'HD', 'HDE', etc.

model = load_model(model_key)

st.title(f"{selected_model} - Cost Estimator")

required_features = model_features[selected_model]

# -------------------
# DISCLAIMER
# -------------------
if 'Val B' not in required_features:
    st.warning("For this model, 'Val B' is not used by the ML model.\nIf you want to include its cost, double-click and manually enter it.")

# -------------------
# INPUT FIELDS
# -------------------
user_input = {}
st.subheader("Input Features")
col1, col2 = st.columns(2)

with col1:
    for feature in numerical_features:
        if feature in required_features:
            val = st.slider(f"{feature}", 0.0, 1000.0, 100.0, step=1.0, key=feature)
        else:
            val = st.number_input(f"(Optional) {feature}", key=feature)
        user_input[feature] = val

with col2:
    for feature in yesno_features:
        if feature in required_features:
            option = st.selectbox(f"{feature}", ['Yes', 'No'], key=feature)
        else:
            option = st.text_input(f"(Optional) {feature}", key=feature)
        user_input[feature] = 1 if option == 'Yes' else (0 if option == 'No' else option)

# -------------------
# PREDICT COST
# -------------------
if model:
    # Filter input for model-required features only
    input_for_model = []
    for feat in required_features:
        val = user_input[feat]
        if isinstance(val, str) and val.strip().isdigit():
            val = float(val)
        input_for_model.append(val)
    
    try:
        pred = model.predict([input_for_model])[0]
        # Add optional Val B if user added it
        extra_cost = 0
        if 'Val B' not in required_features:
            vb_input = user_input['Val B']
            if isinstance(vb_input, (int, float)):
                extra_cost = vb_input
        total = pred + extra_cost
        st.success(f"Estimated Cost: ₹ {total:.2f}")
    except Exception as e:
        st.error(f"Prediction failed: {e}")

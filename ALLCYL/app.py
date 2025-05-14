import streamlit as st
import pickle
import os

# Feature and model mapping
model_features = {
    'HD': ['Bore', 'Stroke', 'RPC', 'Rod', 'R bearing', 'B bearing', 'Block', 'Val A'],
    'HDE': ['Bore', 'Stroke', 'RPC', 'Rod', 'R bearing', 'B bearing', 'Block', 'Val A'],
    'HDI': ['Bore', 'Stroke', 'RPC', 'Rod', 'R bearing', 'B bearing', 'Block', 'Val A'],
    'LD': ['Bore', 'Stroke', 'RPC', 'Rod', 'R bearing', 'B bearing', 'Block', 'Val A'],
    'LDH': ['Bore', 'Stroke', 'RPC', 'Rod', 'Block', 'Val A'],
    'MD': ['Bore', 'Stroke', 'RPC', 'Rod', 'R bearing', 'B bearing', 'Block', 'Val A'],
    'NR': ['Bore', 'Stroke', 'RPC', 'Rod', 'R bearing'],
    'H': ['Bore', 'Stroke', 'RPC', 'Rod', 'R bearing', 'B bearing', 'Block', 'Val A'],
    'L': ['Bore', 'Stroke', 'RPC', 'Rod', 'Block'],
    'M': ['Bore', 'Stroke', 'RPC', 'Rod', 'R bearing', 'B bearing', 'Block', 'Val A'],
    'N': ['Bore', 'Stroke', 'RPC', 'Rod', 'R bearing', 'B bearing', 'Block', 'Val A'],
}

numerical_features = ['Bore', 'Stroke', 'RPC', 'Rod']
yes_no_features = ['R bearing', 'B bearing', 'Block', 'Val A', 'Val B']

# Initialize session state for optional inputs
for f in yes_no_features:
    if f + "_enabled" not in st.session_state:
        st.session_state[f + "_enabled"] = False

st.sidebar.title("Model Selector")
model_type = st.sidebar.selectbox("Choose model type", list(model_features.keys()))

# Load model
def load_model(model_type):
    model_path = f"{model_type}_model.pkl"
    if os.path.exists(model_path):
        with open(model_path, "rb") as f:
            model = pickle.load(f)
        return model
    else:
        st.error(f"Model file {model_path} not found!")
        return None

st.title("Cost Prediction App")
st.write(f"### Selected Model: {model_type}")

required_features = model_features[model_type]
optional_features = [f for f in yes_no_features if f not in required_features]

# Warning for excluded features
for opt in optional_features:
    st.warning(
        f"For {model_type}, the ML model has no importance for **{opt}**. "
        f"If you want to add its cost manually, double-click the input box."
    )

# Input UI layout
col1, col2 = st.columns(2)
inputs = {}

# === Numerical inputs ===
with col1:
    st.subheader("Numerical Inputs")
    for feature in numerical_features:
        if feature in required_features:
            slider_val = st.slider(f"{feature}", min_value=0.0, max_value=1000.0, value=100.0, step=1.0, key=f"{feature}_slider")
            num_val = st.number_input(f"{feature} (exact)", value=slider_val, step=1.0, key=f"{feature}_input")
            inputs[feature] = num_val

# === Yes/No inputs ===
with col2:
    st.subheader("Yes/No Features")
    for feature in yes_no_features:
        if feature in required_features or feature in optional_features:
            selected = st.selectbox(f"{feature}?", options=["No", "Yes"], key=f"{feature}_choice")
            cost_input = st.number_input(
                f"{feature} Cost",
                value=0.0,
                step=10.0,
                key=f"{feature}_cost",
                disabled=feature in optional_features and not st.session_state[feature + "_enabled"]
            )
            # HTML double-click handler for enabling input
            if feature in optional_features:
                st.components.v1.html(
                    f"""
                    <script>
                    const box = window.parent.document.querySelector('input[aria-label="{feature} Cost"]');
                    if (box) {{
                        box.ondblclick = function() {{
                            fetch(window.location.href, {{
                                method: 'POST',
                                headers: {{'Content-Type': 'application/json'}},
                                body: JSON.stringify({{ type: 'enable_{feature}' }})
                            }}).then(() => window.location.reload());
                        }}
                    }}
                    </script>
                    """,
                    height=0,
                )
            inputs[feature] = 1 if selected == "Yes" else 0
            if feature in optional_features and st.session_state[feature + "_enabled"]:
                inputs[feature + "_extra_cost"] = cost_input

# Enable toggles via JS signal (via hidden POST)
if st.session_state.get("_streamlit_messages"):
    for msg in st.session_state["_streamlit_messages"]:
        if msg.startswith("enable_"):
            f = msg.replace("enable_", "")
            st.session_state[f + "_enabled"] = True
    st.session_state["_streamlit_messages"] = []

# Prepare model input
model_input = [inputs.get(f, 0) for f in required_features]
predicted_cost = model.predict([model_input])[0]

# Add extra cost manually if any
manual_addition = sum(inputs.get(f + "_extra_cost", 0) for f in optional_features if st.session_state[f + "_enabled"])
total_cost = predicted_cost + manual_addition

st.markdown(f"### 🔍 Predicted Cost: **₹ {total_cost:.2f}**")

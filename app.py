import streamlit as st
import pandas as pd
import joblib

def safe_transform(encoder, value):
    value = str(value)
    if value in encoder.classes_:
        return encoder.transform([value])[0]
    else:
        return encoder.transform([encoder.classes_[0]])[0]

# ===============================
# Load model and encoders
# ===============================
FEATURE_ORDER = [
    'CHROM',
    'POS',
    'REF',
    'ALT',
    'AF_ESP',
    'AF_EXAC',
    'AF_TGP',
    'SYMBOL',
    'IMPACT',
    'Consequence',
    'SIFT',
    'PolyPhen',
    'CADD_PHRED',
    'CADD_RAW',
    'BLOSUM62'
]



model = joblib.load("model/genomic_model.pkl")
encoders = joblib.load("encoders/encoders.pkl")

st.set_page_config(page_title="Genomic Mutation Risk Predictor")

st.title("🧬 Genomic Mutation Risk Predictor")
st.write("Predict whether a genetic mutation is **Benign or Pathogenic**")

st.markdown("---")

# ===============================
# USER INPUT FORM
# ===============================

chrom = st.text_input("Chromosome (e.g., 17)")
pos = st.number_input("Position", min_value=1)

ref = st.text_input("Reference Base (A/C/G/T)")
alt = st.text_input("Alternate Base (A/C/G/T)")

symbol = st.text_input("Gene Symbol (e.g., BRCA1)")

impact = st.selectbox(
    "Impact",
    ["LOW", "MODERATE", "HIGH"]
)

consequence = st.text_input(
    "Consequence (e.g., missense_variant)"
)

af_exac = st.number_input("AF_EXAC", format="%.6f")
af_esp = st.number_input("AF_ESP", format="%.6f")
af_tgp = st.number_input("AF_TGP", format="%.6f")

sift = st.number_input("SIFT (0=tolerated, 1=deleterious)", min_value=0, max_value=1)
polyphen = st.number_input("PolyPhen (0=benign, 1=possibly, 2=probably damaging)", min_value=0, max_value=2)


cadd_phred = st.number_input("CADD_PHRED")
cadd_raw = st.number_input("CADD_RAW")
blosum62 = st.number_input("BLOSUM62")

# ===============================
# PREDICTION
# ===============================

if st.button("🔍 Predict Mutation Risk"):

    input_data = {
        "CHROM": chrom,
        "POS": pos,
        "REF": ref,
        "ALT": alt,
        "AF_ESP": af_esp,
        "AF_EXAC": af_exac,
        "AF_TGP": af_tgp,
        "SYMBOL": symbol,
        "IMPACT": impact,
        "Consequence": consequence,
        "SIFT": sift,
        "PolyPhen": polyphen,
        "CADD_PHRED": cadd_phred,
        "CADD_RAW": cadd_raw,
        "BLOSUM62": blosum62
    }

    df_input = pd.DataFrame([input_data])

# encode categorical columns
    categorical_cols = [
    'CHROM',
    'REF',
    'ALT',
    'SYMBOL',
    'IMPACT',
    'Consequence']


    for col in categorical_cols:
        if col in encoders:
            df_input[col] = df_input[col].apply(
                lambda x: safe_transform(encoders[col], x)
            )



    df_input = df_input[FEATURE_ORDER]

    prediction = model.predict(df_input.values)[0]
    probability = model.predict_proba(df_input.values)[0][1]

    st.markdown("---")

    if prediction == 1:
        st.error("🧪 Prediction: **Pathogenic Mutation**")
    else:
        st.success("🧪 Prediction: **Benign Mutation**")

    st.write("### Risk Score:", round(probability, 3))

    st.caption(
        "⚠️ This tool is for educational and research purposes only. "
        "It is not a medical diagnosis."
    )

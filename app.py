"""
Streamlit app: CPI vs division performance (linear regression).
Run locally: streamlit run app.py
Deploy to Streamlit Community Cloud, Railway, or Render.
"""

import os

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from cpi_regression import (
    get_cpi_data,
    load_division_performance,
    run_regression,
    _sample_cpi,
)


st.set_page_config(page_title="CPI vs Division", layout="centered")
st.title("CPI vs division performance")
st.caption("Compare Consumer Price Index to your division metric using linear regression.")

# Sidebar: CPI source
with st.sidebar:
    st.header("Data")
    _secret_key = getattr(st.secrets, "BLS_API_KEY", None) if hasattr(st, "secrets") else None
    _env_key = os.environ.get("BLS_API_KEY")
    bls_key_default = _secret_key or _env_key
    use_bls = st.checkbox("Use live CPI (BLS API)", value=bool(bls_key_default))
    bls_key = bls_key_default
    if use_bls:
        bls_key = st.text_input("BLS API key", value=bls_key or "", type="password", help="Free at bls.gov/developers") or bls_key
    st.divider()
    st.caption("Division data: upload a CSV below or use sample data.")

# Division data: upload or sample
uploaded = st.file_uploader("Division performance CSV", type=["csv"], help="Columns: date, value")
if uploaded:
    try:
        raw = pd.read_csv(uploaded)
        raw["date"] = pd.to_datetime(raw["date"])
        division = raw[["date", "value"]].rename(columns={"value": "division"})
        st.success(f"Loaded {len(division)} rows.")
    except Exception as e:
        st.error(f"Could not parse CSV: {e}")
        st.stop()
else:
    try:
        division = load_division_performance("division_performance.csv")
        st.info("Using sample division data from division_performance.csv. Upload a CSV to use your own.")
    except FileNotFoundError:
        cpi_sample = _sample_cpi()
        division = cpi_sample[["date"]].copy()
        division["division"] = (cpi_sample["cpi"].values * 1.2 + 50) + 0.5 * range(len(cpi_sample))
        st.info("Using synthetic division data. Add division_performance.csv or upload a file.")

# CPI
try:
    if use_bls and bls_key:
        cpi = get_cpi_data(api_key=bls_key)
        st.sidebar.success("Live CPI loaded.")
    else:
        cpi = get_cpi_data()
        st.sidebar.caption("Using sample CPI. Enable BLS and add key for live data.")
except Exception as e:
    st.error(f"CPI error: {e}")
    st.stop()

# Run regression
try:
    merged, model, r2, y_pred = run_regression(cpi, division)
except ValueError as e:
    st.error(str(e))
    st.stop()

# Metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Slope (per 1 pt CPI)", f"{model.coef_[0]:.4f}")
with col2:
    st.metric("Intercept", f"{model.intercept_:.4f}")
with col3:
    st.metric("R²", f"{r2:.4f}")

st.write("**Equation:** division ≈ {:.2f} + {:.2f} × CPI".format(model.intercept_, model.coef_[0]))

# Plot
fig, ax = plt.subplots(figsize=(8, 5))
ax.scatter(merged["cpi"], merged["division"], alpha=0.7, label="Actual")
ax.plot(merged["cpi"], y_pred, color="red", linewidth=2, label="Regression line")
ax.set_xlabel("CPI (Consumer Price Index)")
ax.set_ylabel("Division performance")
ax.set_title("Division performance vs CPI")
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
st.pyplot(fig)
plt.close()

# Optional: show merged table
with st.expander("View merged data"):
    st.dataframe(merged, use_container_width=True)

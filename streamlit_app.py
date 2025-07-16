import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# Define simple sample data manually
def load_simple_data():
    data = {
        'X': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'y': [2.1, 4.2, 6.1, 8.0, 10.1, 11.9, 14.2, 16.1, 18.0, 20.2]
    }
    return pd.DataFrame(data)

# App title
st.title("📘 Simple Linear Regression Dashboard")

# Load data
df = load_simple_data()

# Sidebar options
st.sidebar.header("Options")
if st.sidebar.checkbox("Show raw data", value=True):
    st.subheader("🔍 Simple Dataset")
    st.dataframe(df)

# Extract X and y
X = df[['X']]  # shape: (n_samples, 1)
y = df['y']    # shape: (n_samples,)

# Fit linear regression model
model = LinearRegression()
model.fit(X, y)
y_pred = model.predict(X)

# Show model info
st.subheader("📈 Linear Regression Model")
st.markdown(f"**Equation:** y = {model.coef_[0]:.2f}x + {model.intercept_:.2f}")
st.markdown(f"**R² score:** {r2_score(y, y_pred):.3f}")

# Plot
st.subheader("📉 Regression Plot")
fig, ax = plt.subplots()
ax.scatter(X, y, color='blue', label='Actual Data')
ax.plot(X, y_pred, color='red', linewidth=2, label='Regression Line')
ax.set_xlabel("X")
ax.set_ylabel("y")
ax.set_title("Simple Linear Regression Fit")
ax.legend()
st.pyplot(fig)

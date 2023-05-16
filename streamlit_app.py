# from collections import namedtuple
# import altair as alt
# import math
import calendar
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import seaborn as sns
import streamlit as st

"""
# Enstoa COE KPI Report

Edit `/streamlit_app.py` to customize this app to your heart's desire :heart:

If you have any questions, checkout our [documentation](https://docs.streamlit.io) and [community
forums](https://discuss.streamlit.io).

In the meantime, below is an example of what you can do with just a few lines of code:
"""


st.set_page_config(layout="wide")

st.subheader("Input CSV below")
uploaded_file = st.file_uploader(label_visibility="collapsed")

# if uploaded_file:
#     df = pd.read_csv(uploaded_file)
#     st.subheader("Dataframe")
#     st.write(df.head(3))
#     st.subheader("D")
#     st.write(df.describe())
# else:
#     st.info("☝️ Upload a CSV file")

if not uploaded_file:
    st.info("☝️ Upload a CSV file")

df = pd.read_csv(uploaded_file)
st.subheader("Dataframe")
st.write(df.head(3))
st.subheader("D")
st.write(df.describe())

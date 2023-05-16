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

st.set_page_config(layout="wide")

"""
# Enstoa COE KPI Report

Edit `/streamlit_app.py` to customize this app to your heart's desire :heart:

If you have any questions, checkout our [documentation](https://docs.streamlit.io) and [community
forums](https://discuss.streamlit.io).

In the meantime, below is an example of what you can do with just a few lines of code:
"""


st.subheader("Input CSV below")

uploaded_file = st.file_uploader(label="hidden label", label_visibility="collapsed")
# st.info("☝️ Upload a CSV file")

if not uploaded_file:
    st.warning("Please upload a .csv file")
    st.stop()

st.success(
    f'{uploaded_file.name} has been successfully uploaded! Select "Browse files" again to upload a different file if desired.',
    icon="✅",
)

# if uploaded_file:
#     df = pd.read_csv(uploaded_file)
#     st.subheader("Dataframe")
#     st.write(df.head(3))
#     st.subheader("D")
#     st.write(df.describe())
# else:
#     st.info("☝️ Upload a CSV file")


df = pd.read_csv(uploaded_file)
st.subheader("Dataframe")
st.write(df.head(3))
st.subheader("basic df info")
st.write(df.describe())

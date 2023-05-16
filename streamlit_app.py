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
# st.subheader("Dataframe")
# st.write(df.head(3))
# st.subheader("basic df info")
# st.write(df.describe())


# Pre-processing

df = df.drop(columns=["Latest Update", "Tickets", "Assignee name", "Requester name"])
init_col_names = list(df.dtypes.reset_index()["index"])

new_col_names = {
    init_col_names[0]: "ticket_id",
    init_col_names[1]: "client_name",
    init_col_names[2]: "ticket_status",
    init_col_names[3]: "ticket_type",
    init_col_names[4]: "ticket_subject",
    init_col_names[5]: "ticket_priority",
    init_col_names[7]: "environment",
    init_col_names[8]: "product_type",
    init_col_names[6]: "requested_date",
    init_col_names[9]: "ticket_updated_date",
}

df = df.rename(columns=new_col_names)[new_col_names.values()]

df = df.astype(
    {
        # df.columns[0]: 'object',
        # df.columns[1]: 'object',
        # df.columns[2]: '',
        # df.columns[3]: '',
        # df.columns[4]: '',
        # df.columns[5]: '',
        # df.columns[6]: '',
        # df.columns[7]: '',
        df.columns[8]: "datetime64[ns]",
        df.columns[9]: "datetime64[ns]",
    }
)

# Feature engineering
df["days_active"] = df.ticket_updated_date - df.requested_date
df["month_opened"] = df.requested_date.dt.month
df["year_opened"] = df.requested_date.dt.year

df["day_opened"] = df.requested_date.dt.day_of_year
df["week_opened"] = df.requested_date.dt.isocalendar().week

# df_weekly_grouped = (
#     df.groupby(by=["year_opened", "month_opened", "week_opened"])
#     .week_opened.count()
#     .reset_index(name="ticket_count")
#     .astype({"week_opened": "int32"})
# )

df_monthly_grouped = (
    df.groupby(by=["year_opened", "month_opened"])
    .month_opened.count()
    .reset_index(name="ticket_count")
    .astype({"month_opened": "int32"})
)
st.write(df_monthly_grouped.head(20))

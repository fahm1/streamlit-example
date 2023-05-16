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


@st.cache_data()
def load_data(file):
    return pd.read_csv(file)


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


df = load_data(uploaded_file)

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

custom_palette = sns.color_palette(
    ["#264653", "#2A9D8F", "#E9C46A", "#F4A261", "#E76F51", "#E97C61"]
)

# with st.expander('title')

# Fig 1: Tickets per month
fig, ax = plt.subplots(figsize=(13.6, 8))

bplot = sns.barplot(
    data=df_monthly_grouped.query("year_opened >= 2019"),
    x="month_opened",
    y="ticket_count",
    hue="year_opened",
    palette=custom_palette,
    ax=ax,
    errorbar=None,
    alpha=0.2,
)

ax.set_xlim(-0.5, 11.5)
ax.set_ylim(0, ax.get_ylim()[1])

ax.legend_.remove()

ax.set_xticklabels([calendar.month_name[i] for i in range(1, 13)])
# ax.set_xlabel("Month of Year", fontsize=14, labelpad=12)
ax.set_xlabel("")
ax.set_ylabel("Tickets Opened", fontsize=12, labelpad=15)
ax.tick_params(axis="both", length=0)
ax.tick_params(axis="y", pad=10)

ax2 = fig.add_axes([0.119, 0.11, 0.76, 0.77])  # left, bottom, width, height
ax2.patch.set_alpha(0)

lplot = sns.lineplot(
    data=df_monthly_grouped.query(
        "(year_opened >= 2019 & year_opened < 2023) | (year_opened == 2023 & month_opened < 5)"
    ),
    x="month_opened",
    y="ticket_count",
    hue="year_opened",
    palette=custom_palette[:5],
    ax=ax2,
    errorbar=None,
    alpha=1,
    legend=True,
)

ax2.set_xlim(0.125, 12)
ax2.set_ylim(0, ax.get_ylim()[1])

handles, labels = ax2.get_legend_handles_labels()
handles = handles[::-1]
labels = labels[::-1]
ax2.legend(
    handles,
    labels,
    # loc="best",
    facecolor="white",
    framealpha=1,
    bbox_to_anchor=(0.9, 0.728),
)
# legend.set_title("Year")
legend.get_title().set_fontsize(12)
legend.get_frame().set_linewidth(0.25)

ax2.set_xticklabels([])
ax2.set_yticklabels([])
ax2.set_xlabel("")
ax2.set_ylabel("")
ax2.tick_params(axis="both", length=0)

ax2.axvline(x=4.25, linestyle="--", color="red", ymin=0, ymax=0.95)

ax2.text(
    4.37,
    plt.ylim()[1] * 0.82,
    "End of full month data for 2023",
    color="r",
    ha="left",
    rotation=0,
)
ax2.grid(color="k", linestyle="-", axis="y", alpha=0.1)


plt.suptitle(
    "The number of tickets opened per month has increased significantly YoY for 2022 and the start of 2023",
    fontsize=14,
    ha="left",
    va="top",
    x=0.12,
    y=0.93,
)

sns.despine(bottom=True, left=True)

# plt.savefig('tickets_per_month.png', dpi=300, bbox_inches='tight')
st.pyplot()

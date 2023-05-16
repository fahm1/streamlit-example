import time
import calendar
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# import matplotlib.cm as cm

# st.set_page_config(layout="wide")
st.set_page_config(
    page_title="Enstoa COE KPI Report",
    page_icon="🏫",
    layout="wide",
    menu_items={
        "Get help": "mailto:fislam@enstoa.com",
        "About": "A page to display key metrics regarding COE and tickets pulled from Zendesk",
    },
)

"""
# Enstoa COE KPI Report

Questions / comments / concerns / requests: [fislam@enstoa.com](mailto:fislam@enstoa.com)
"""


@st.cache_data()
def load_data(file):
    return pd.read_csv(file)


# import requests

# url = st.text_input(
#     label="url box", placeholder="Input a TikTok URL here: ", max_chars=200
# )

# if not url:
#     st.warning("Please enter a valid TikTok link")
#     st.stop()

# st.success("Loading...")

# headers = {
#     "authority": "tikwm.com",
#     "accept": "application/json, text/javascript, */*; q=0.01",
#     "accept-language": "en-US,en;q=0.9",
#     "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
#     "origin": "https://tikwm.com",
#     "referer": "https://tikwm.com/",
#     "sec-ch-ua": '"Chromium";v="112", "Microsoft Edge";v="112", "Not:A-Brand";v="99"',
#     "sec-ch-ua-mobile": "?0",
#     "sec-ch-ua-platform": '"Windows"',
#     "sec-fetch-dest": "empty",
#     "sec-fetch-mode": "cors",
#     "sec-fetch-site": "same-origin",
#     "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.58",
#     "x-requested-with": "XMLHttpRequest",
# }

# data = {
#     "url": url,
#     "count": "12",
#     "cursor": "0",
#     "web": "1",
#     "hd": "1",
# }

# response = requests.post("https://tikwm.com/api/", headers=headers, data=data)

# # print(response.status_code)
# response_data = response.json()
# # print(response_data)

# vid = requests.get(f'https://tikwm.com{response_data["data"]["hdplay"]}').content

# st.video(vid, format="video/mp4")


st.subheader("Input CSV below")

uploaded_file = st.file_uploader(label="hidden label", label_visibility="collapsed")
# st.info("☝️ Upload a CSV file")

if not uploaded_file:
    st.warning("Please upload a .csv file")
    st.stop()

upload_success = st.success(
    f"{uploaded_file.name} has been successfully uploaded!",
    icon="✅",
)

progress_text = "Loading..."
progress_bar = st.progress(0, progress_text)

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "Tickets per Month",
        "Average Days to Close Tickets",
        "Average Ticket Count by Product",
        "Average Ticket Count by Client",
        "Average Days to Close Tickets by Product",
    ]
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

# with st.expander("Tickets Per Month"):
with tab1:
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
    legend = ax2.legend(
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
    st.pyplot(fig=fig)

progress_bar.progress(20, text=progress_text)

df3 = (
    df.query("ticket_status == 'Closed' and year_opened >= 2019")
    .groupby(by=["year_opened", "month_opened"])
    .days_active.agg(np.mean)
    .reset_index(name="average_days_active")
)

df3["rounded_days_active"] = np.ceil(
    df3["average_days_active"].dt.total_seconds() / (24 * 3600)
).astype(int)

# with st.expander("Average days to close tickets"):
with tab2:
    # Fig 2: Average tickets per month
    fig, ax = plt.subplots(figsize=(13.6, 8))

    bplot = sns.barplot(
        data=df3,
        x="month_opened",
        y="rounded_days_active",
        hue="year_opened",
        palette=custom_palette,
        ax=ax,
        errorbar=None,
        alpha=0.15,
    )

    ax.set_xlim(-0.5, 11.5)
    ax.set_ylim(0, ax.get_ylim()[1])

    ax.legend_.remove()

    ax.set_xticklabels([calendar.month_name[i] for i in range(1, 13)])
    # ax.set_xlabel("Month of Year", fontsize=14, labelpad=12)
    ax.set_xlabel("")
    ax.set_ylabel("Mean Days to Ticket Closure", fontsize=12, labelpad=15)
    ax.tick_params(axis="both", length=0)
    ax.tick_params(axis="y", pad=28)

    ax2 = fig.add_axes([0.1, 0.11, 0.76, 0.77])  # left, bottom, width, height
    ax2.patch.set_alpha(0)

    lplot = sns.lineplot(
        data=df3,
        x="month_opened",
        y="rounded_days_active",
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
        bbox_to_anchor=(0.9, 0.648),
    )
    legend.get_title().set_fontsize(12)
    legend.get_frame().set_linewidth(0.25)

    ax2.set_xticklabels([])
    ax2.set_yticklabels([])
    ax2.set_xlabel("")
    ax2.set_ylabel("")
    ax2.tick_params(axis="both", length=0)

    ax2.axvline(x=4.55, linestyle="--", color="red", ymin=0, ymax=0.95)

    ax2.text(
        1.93,
        plt.ylim()[1] * 0.865,
        "End of full month data for 2023",
        color="r",
        ha="left",
        rotation=0,
    )
    ax2.grid(color="k", linestyle="-", axis="y", alpha=0.1)

    plt.suptitle(
        "The average number of days to close a ticket has been on a general decline since mid-2022",
        fontsize=14,
        ha="left",
        va="top",
        x=0.1,
        y=0.9,
    )

    sns.despine(bottom=True, left=True)

    # plt.savefig('average_days_to_close.png', dpi=300, bbox_inches='tight')
    st.pyplot(fig=fig)

progress_bar.progress(40, text=progress_text)

products_of_interest = [
    "Oracle Primavera Unifier",
    "Adapters",
    "Microsoft Power BI",
    "Enablon",
    "Oracle Primavera P6",
    "Other",
]

df4 = df.copy().query("`product_type`.notnull()")
df4.loc[~df4.product_type.isin(products_of_interest), "product_type"] = "Other"

df5 = (
    df4.groupby(by=["year_opened", "month_opened", "product_type"])
    .product_type.count()
    .reset_index(name="count")
)

df5["year_month"] = df5.year_opened.astype(str) + "-" + df5.month_opened.astype(str)
df5["year_month_style"] = pd.to_datetime(df5["year_month"], format="%Y-%m")
df5["month_year_style"] = df5.year_month_style.dt.strftime("%b. %Y").apply(
    lambda x: x.replace("May.", "May")
)

# with st.expander("Ticket count by product"):
with tab3:
    # Fig 3: Average tickets by product per month
    fig, ax = plt.subplots(figsize=(30, 12))

    brplot = sns.barplot(
        data=df5.query("year_month >= '2022-1' and year_month < '2023-5'"),
        x="month_year_style",
        y="count",
        hue="product_type",
        palette=custom_palette,
        errorbar=None,
        hue_order=products_of_interest,
    )

    legend = ax.legend(
        facecolor="white",
        framealpha=1,
        fontsize=16,
        loc="upper left",
        bbox_to_anchor=(0.01, 1.0051),
    )
    legend.get_frame().set_linewidth(0.25)

    ax.set_xlabel("")
    ax.set_ylabel("Count of Tickets", fontsize=18, labelpad=18)
    ax.set_xticklabels(ax.get_xticklabels(), fontsize=14)
    ax.set_yticks(ax.get_yticks())
    ax.set_yticklabels(ax.get_yticklabels(), fontsize=14)
    ax.tick_params(axis="both", length=0)

    plt.suptitle(
        "A general increase in ticket counts across the board is observed, though an increase in Oracle Primavera Unifier and Adapters tickets are the most prominent",
        x=0.113,
        y=0.93,
        ha="left",
        va="bottom",
        fontsize=20,
    )

    ax.grid(color="k", linestyle="-", axis="y", alpha=0.1)
    sns.despine(bottom=True, left=True)

    # plt.savefig('count_product_tickets.png', dpi=300, bbox_inches='tight')
    st.pyplot(fig=fig)

progress_bar.progress(60, text=progress_text)

df6 = df.copy()
df6.loc[
    df6.client_name == "The Red Sea Development Co., (TRSDC)", "client_name"
] = "TRSDC"
clients_of_interest = ["Neom", "TRSDC", "NYP", "Denver", "Enstoa", "Other"]
df6.loc[~df6.client_name.isin(clients_of_interest), "client_name"] = "Other"
df7 = (
    df6.groupby(by=["year_opened", "month_opened", "client_name"])
    .client_name.count()
    .reset_index(name="count")
)
df7["year_month"] = df7.year_opened.astype(str) + "-" + df7.month_opened.astype(str)
df7["year_month_style"] = pd.to_datetime(df7["year_month"], format="%Y-%m")
df7["month_year_style"] = df7.year_month_style.dt.strftime("%b. %Y").apply(
    lambda x: x.replace("May.", "May")
)

# with st.expander("Ticket count by client"):
with tab4:
    # Fig 4: Average tickets by client per month
    fig, ax = plt.subplots(figsize=(30, 12))

    brplot = sns.barplot(
        data=df7.query("year_month >= '2022-1' and year_month < '2023-5'"),
        x="month_year_style",
        y="count",
        hue="client_name",
        palette=custom_palette,
        # palette='viridis',
        errorbar=None,
        hue_order=clients_of_interest,
    )

    legend = ax.legend(
        facecolor="white",
        framealpha=1,
        fontsize=16,
        loc="upper left",
        bbox_to_anchor=(0.01, 1.0051),
    )
    legend.get_frame().set_linewidth(0.25)

    ax.set_xlabel("")
    ax.set_ylabel("Count of Tickets", fontsize=18, labelpad=18)
    ax.set_xticklabels(ax.get_xticklabels(), fontsize=14)
    ax.set_yticks(ax.get_yticks())
    ax.set_yticklabels(ax.get_yticklabels(), fontsize=14)
    ax.tick_params(axis="both", length=0)

    plt.suptitle(
        # "The recent influx of tickets is largely due to a significant increase in the number of tickets coming from NEOM and TRSDC in particular",
        "The recent influx of tickets is largely due to a significant increase in the number of tickets coming from NEOM, TRSDC, and many other clients in aggregate",
        x=0.1121,
        y=0.93,
        ha="left",
        va="bottom",
        fontsize=20,
    )

    ax.grid(color="k", linestyle="-", axis="y", alpha=0.1)
    sns.despine(bottom=True, left=True)

    # plt.savefig('count_client_tickets.png', dpi=300, bbox_inches='tight')
    st.pyplot(fig=fig)

progress_bar.progress(80, text=progress_text)

df8 = df.query("ticket_status == 'Closed'")
df8 = (
    df8.groupby(by=["year_opened", "month_opened", "product_type"])
    .days_active.agg(np.mean)
    .reset_index(name="average_days_active")
)
df8["rounded_days_active"] = np.ceil(
    df8["average_days_active"].dt.total_seconds() / (24 * 3600)
).astype(int)
df8["year_month"] = df8.year_opened.astype(str) + "-" + df8.month_opened.astype(str)
df8["year_month_style"] = pd.to_datetime(df8["year_month"], format="%Y-%m")
df8["month_year_style"] = df8.year_month_style.dt.strftime("%b. %Y").apply(
    lambda x: x.replace("May.", "May")
)

# with st.expander("Average days to close by product"):
with tab5:
    # Fig 5: Average tickets by client per month
    fig, ax = plt.subplots(figsize=(30, 12))

    brplot = sns.barplot(
        data=df8.query("year_month >= '2022-1' and year_month < '2023-5'"),
        x="month_year_style",
        y="rounded_days_active",
        hue="product_type",
        palette=custom_palette,
        errorbar=None,
        hue_order=products_of_interest,
    )

    legend = ax.legend(
        facecolor="white",
        framealpha=1,
        fontsize=16,
        loc="upper right",
        bbox_to_anchor=(0.95, 1),
    )
    legend.get_frame().set_linewidth(0.25)

    ax.set_xlabel("")
    ax.set_ylabel("Mean days to ticket closure", fontsize=18, labelpad=18)
    ax.set_xticklabels(ax.get_xticklabels(), fontsize=14)
    ax.set_yticks(ax.get_yticks())
    ax.set_yticklabels(ax.get_yticklabels(), fontsize=14)
    ax.tick_params(axis="both", length=0)

    plt.suptitle(
        "The average number of days spent on tickets of all products across the board has gone down significantly with time",
        x=0.113,
        y=0.93,
        ha="left",
        va="bottom",
        fontsize=20,
    )

    ax.grid(color="k", linestyle="-", axis="y", alpha=0.1)
    sns.despine(bottom=True, left=True)

    # plt.savefig('average_days_by_product.png', dpi=300, bbox_inches='tight')
    st.pyplot(fig=fig)


progress_bar.progress(100, text=progress_text)

success_message = st.success("Done!", icon="✅")
st.balloons()

time.sleep(3)
upload_success.empty()
progress_bar.empty()
success_message.empty()


# import requests
# import streamlit as st

# # url = "https://www.tiktok.com/@osamamustufa786/video/7206645648219737370?is_from_webapp=1&sender_device=pc"
# url = st.text_input(
#     label="url box", placeholder="Input a TikTok URL here: ", max_chars=200
# )

# if not url:
#     st.warning("Please enter a valid TikTok link")
#     st.stop()

# st.success("Loading...")

# headers = {
#     "authority": "tikwm.com",
#     "accept": "application/json, text/javascript, */*; q=0.01",
#     "accept-language": "en-US,en;q=0.9",
#     "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
#     "origin": "https://tikwm.com",
#     "referer": "https://tikwm.com/",
#     "sec-ch-ua": '"Chromium";v="112", "Microsoft Edge";v="112", "Not:A-Brand";v="99"',
#     "sec-ch-ua-mobile": "?0",
#     "sec-ch-ua-platform": '"Windows"',
#     "sec-fetch-dest": "empty",
#     "sec-fetch-mode": "cors",
#     "sec-fetch-site": "same-origin",
#     "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.58",
#     "x-requested-with": "XMLHttpRequest",
# }

# data = {
#     "url": url,
#     "count": "12",
#     "cursor": "0",
#     "web": "1",
#     "hd": "1",
# }

# response = requests.post("https://tikwm.com/api/", headers=headers, data=data)

# print(response.status_code)
# response_data = response.json()
# print(response_data)

# vid = requests.get(f'https://tikwm.com{response_data["data"]["hdplay"]}').content

# st.video(vid, format="video/mp4")

import time
import calendar
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import altair as alt
import zipfile
import base64


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


def get_base64_encoded_file(file_path):
    with open(file_path, "rb") as file:
        encoded_file = base64.b64encode(file.read()).decode()
    return encoded_file


@st.cache_data()
def load_data(file):
    return pd.read_excel(file)


def create_figures(
    data,
    current_month=None,
    download_figs=False,
    interactive_charts=False
    # start_month=None,
    # start_year=None,
    # end_month=None,
    # end_year=None,
):
    if not current_month:
        current_month = datetime.now().month

    interactive_charts = False

    custom_date = False

    # if (
    #     start_month != "January"
    #     or start_year != 2022
    #     or end_month != "June"
    #     or end_year != 2023
    # ):
    #     custom_date = True
    #     primary_year = start_year
    #     primary_month = start_month
    #     current_year = end_year
    #     current_month = datetime.strptime(end_month, "%B").month
    #     # current_month = end_month
    #     secondary_year_month = f"{current_year}-{current_month}"

    if not custom_date:
        current_year = 2023
        primary_year = current_year - 4
        primary_month = 1
        secondary_year_month = "2022-1"

    progress_text = "Loading..."
    progress_bar = st.progress(0, progress_text)

    # TODO: A LOT
    # TODO: move and rename tabs instead of messing around like below
    # TODO: @s don't work well in df.query()s for some reason, replace w f-strings if necessary (mem issue?)
    # TODO: make literally everything MD lol so that it doesn't reset stuff
    # TODO: make a 'reset_date' button so that date can be restored to normal if messed around with a bit too much
    # have to consider that charts are different dates, so actually 'reset' would just make the appearance
    # the same as the start, but the charts would also be the same as the start, ie. not following the appearnce
    # note: primary = tab1 and tab 2
    #   secondary = tab3, tab4, and tab5
    tab1, tab3, tab4, tab2, tab5 = st.tabs(
        [
            "Tickets per Month",
            "Ticket Count by Product",
            "Ticket Count by Client",
            "Average Days to Close Tickets",
            "Average Days to Close Tickets by Product",
        ]
    )
    if download_figs:
        temp_download_all_button = download_section.markdown(
            f"""
        <style>
        .temp-download-all-button {{
            text-decoration: none !important;
            padding: 6px 12px;
            background-color: transparent;
            color: white !important;
            border-radius: 4px;
            border: 2px solid #D3D3D3;
            cursor: not-allowed;
            display: inline-block;
            transition: background-color 0s, border-color 0s, color 0s;
            width: 100%;
            box-sizing: border-box;
            text-align: center;
        }}
        .temp-download-all-button:hover {{
            text-decoration: none !important;
            border-color: red;
            color: red !important;
        }}
        </style>
        <div class="temp-download-all-button">Please wait...</div>
        """,
            unsafe_allow_html=True,
        )

    df = load_data(data)

    # Pre-processing

    df = df.drop(
        columns=["Latest Update", "Tickets", "Assignee name", "Requester name"]
    )
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
        col1, col2 = st.columns([0.8, 0.2], gap="small")

        with col1:
            # st.write(f"end_month: {end_month}")
            # st.write(start_month, start_year, end_month, end_year)
            # st.write(primary_month, primary_year)
            # st.write(f"curr_month:{current_month} ")
            # st.write(f"curr_year: {current_year}")
            # Fig 1: Tickets per month
            if interactive_charts:
                custom_palette2 = [
                    "#264653",
                    "#2A9D8F",
                    "#E9C46A",
                    "#F4A261",
                    "#E76F51",
                ]

                source = df_monthly_grouped.query(
                    f"(year_opened >= ({primary_year}) & year_opened < {current_year}) | (year_opened == {current_year} & month_opened < {current_month})"
                )

                base = alt.Chart(source).properties(height=600)

                highlight = alt.selection(
                    type="single",
                    on="mouseover",
                    fields=["month_opened"],
                    nearest=True,
                )

                tooltip = [
                    alt.Tooltip("month_opened:O", title="Month of Year"),
                    alt.Tooltip("ticket_count:Q", title="Tickets Opened"),
                    alt.Tooltip("year_opened:N", title="Year"),
                ]

                color = alt.Color(
                    "year_opened:N",
                    legend=alt.Legend(title="Year", titleFontSize=20, labelFontSize=16),
                    scale=alt.Scale(range=custom_palette2),
                )

                points = (
                    base.mark_circle()
                    .encode(opacity=alt.value(0))
                    .add_selection(highlight)
                )

                line = base.mark_line(strokeWidth=4).encode(
                    x=alt.X(
                        "month_opened:O",
                        title="Month of Year",
                        axis=alt.Axis(
                            values=list(range(1, 13)),
                            tickCount=12,
                            labelExpr="datum.value === 1 ? 'January' : datum.value === 2 ? 'February' : datum.value === 3 ? 'March' : datum.value === 4 ? 'April' : datum.value === 5 ? 'May' : datum.value === 6 ? 'June' : datum.value === 7 ? 'July' : datum.value === 8 ? 'August' : datum.value === 9 ? 'September' : datum.value === 10 ? 'October' : datum.value === 11 ? 'November' : 'December'",
                            labelAngle=315,
                            titlePadding=20,
                        ),
                    ),
                    y=alt.Y("ticket_count", title="Tickets Opened"),
                    color=color,
                    opacity=alt.condition(highlight, alt.value(1), alt.value(0.2)),
                    tooltip=tooltip,
                )

                chart = (
                    (points + line)
                    .configure_axis(
                        titleFontSize=20,
                        labelFontSize=16,
                    )
                    .interactive()
                )

                st.altair_chart(chart, use_container_width=True)

            # if not interactive_charts:
            fig, ax = plt.subplots(figsize=(13.6, 7))

            bplot = sns.barplot(
                data=df_monthly_grouped.query(f"year_opened >= {primary_year}"),
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
                    f"(year_opened >= ({primary_year}) & year_opened < {current_year}) | (year_opened == {current_year} & month_opened < {current_month})"
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

            if current_month != 1:
                ax2.axvline(
                    x=current_month - 0.75,
                    linestyle="--",
                    color="red",
                    ymin=0,
                    ymax=0.95,
                )

            ax2.grid(color="k", linestyle="-", axis="y", alpha=0.1)

            plt.suptitle(
                f"Number of Zendesk Tickets Opened per Month {current_year - 4} - {current_year}",
                fontsize=14,
                ha="left",
                va="top",
                x=0.12,
                y=0.93,
            )

            sns.despine(bottom=True, left=True)

            if not interactive_charts:
                st.pyplot(fig=fig)

            download_tab_1_button = st.empty()
            download_tab_1_button.button(
                "Download This Figure", disabled=True, key="tab1_download"
            )

            if download_figs:
                plt.savefig("tickets_per_month.png", dpi=300, bbox_inches="tight")
                download_tab_1_button.empty()
                download_file_path = "tickets_per_month.png"
                css = f"""
                    <style>
                    .download-button {{
                        text-decoration: none;
                        padding: 6px 12px;
                        background-color: transparent;
                        color: white !important;
                        border-radius: 4px;
                        border: 0.5px solid #D3D3D3 !important;
                        cursor: pointer;
                        display: inline-block;
                        transition: background-color 0s, border-color 0s, color 0s;
                    }}
                    .download-button:hover {{
                        border-color: red !important;
                        color: red !important;
                        text-decoration: none;
                    }}
                    .download-button:active {{
                        text-decoration: none;
                    }}
                    </style>
                    
                    <a href="data:application/octet-stream;base64,{get_base64_encoded_file(download_file_path)}" download="tickets_per_month.png" class="download-button">Download This Figure</a>
                    """
                # TODO: can prolly remove css from other buttons, not sure why but it works
                st.markdown(css, unsafe_allow_html=True)

        with col2:
            value = df_monthly_grouped.query(
                "`year_opened` == @current_year and `month_opened` == @current_month - 1"
            ).ticket_count.squeeze()

            delta_month = round(
                (
                    df_monthly_grouped.query(
                        "`year_opened` == @current_year and `month_opened` == @current_month - 1"
                    ).ticket_count.squeeze()
                    - df_monthly_grouped.query(
                        "`year_opened` == @current_year and `month_opened` == @current_month - 2"
                    ).ticket_count.squeeze()
                )
                / df_monthly_grouped.query(
                    "`year_opened` == @current_year and `month_opened` == @current_month - 2"
                ).ticket_count.squeeze()
                * 100,
                1,
            )

            delta_year = round(
                (
                    df_monthly_grouped.query(
                        "`year_opened` == @current_year and `month_opened` == @current_month - 1"
                    ).ticket_count.squeeze()
                    - df_monthly_grouped.query(
                        "`year_opened` == @current_year - 1 and `month_opened` == @current_month - 1"
                    ).ticket_count.squeeze()
                )
                / df_monthly_grouped.query(
                    "`year_opened` == @current_year - 1 and `month_opened` == @current_month - 1"
                ).ticket_count.squeeze()
                * 100,
                1,
            )

            st.metric(
                label="No. Tickets",
                value=value,
                delta=f"{delta_month}%",
                delta_color="inverse",
                help=f"The number of tickets {'increased' if delta_month > 0 else 'decreased'} by {delta_month}% month over month and {'increased' if delta_year > 0 else 'decreased'} by {delta_year}% year over year.",
            )

            df_monthly_grouped_styled = df_monthly_grouped.rename(
                columns={
                    "year_opened": "Year",
                    "month_opened": "Month",
                    "ticket_count": "Ticket Count",
                }
            )
            df_monthly_grouped_styled = df_monthly_grouped_styled[::-1].style.format(
                {"Year": "{:.0f}"}
            )

            st.dataframe(
                df_monthly_grouped_styled, use_container_width=True, hide_index=True
            )

    progress_bar.progress(20, text=progress_text)

    df3 = (
        df.query("ticket_status == 'Closed' and year_opened >= @current_year - 4")
        .groupby(by=["year_opened", "month_opened"])
        .days_active.agg(np.mean)
        .reset_index(name="average_days_active")
    )

    df3["rounded_days_active"] = np.ceil(
        df3["average_days_active"].dt.total_seconds() / (24 * 3600)
    ).astype(int)

    # with st.expander("Average days to close tickets"):
    with tab2:
        col1, col2 = st.columns([0.8, 0.2], gap="small")

        with col1:
            # Fig 2: Average tickets per month
            fig, ax = plt.subplots(figsize=(13.6, 7))

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

            # ax2.axvline(x=5.55, linestyle="--", color="red", ymin=0, ymax=0.95)
            if current_month != 1:
                ax2.axvline(
                    x=current_month - 0.45,
                    linestyle="--",
                    color="red",
                    ymin=0,
                    ymax=0.95,
                )

            ax2.grid(color="k", linestyle="-", axis="y", alpha=0.1)

            plt.suptitle(
                f"Average Number of Days to Close Tickets per Month {current_year - 4} - {current_year}",
                fontsize=14,
                ha="left",
                va="top",
                x=0.1,
                y=0.9,
            )

            sns.despine(bottom=True, left=True)

            st.pyplot(fig=fig)
            download_tab_2_button = st.empty()
            download_tab_2_button.button(
                "Download This Figure", disabled=True, key="tab2_download"
            )

            if download_figs:
                plt.savefig("average_days_to_close.png", dpi=300, bbox_inches="tight")
                download_tab_2_button.empty()
                download_file_path = "average_days_to_close.png"
                st.markdown(
                    f"""
                    <style>
                    .download-button {{
                        text-decoration: none;
                        padding: 6px 12px;
                        background-color: transparent;
                        color: white;
                        border-radius: 4px;
                        border: 2px solid #D3D3D3;
                        cursor: pointer;
                        display: inline-block;
                        transition: background-color 0.3s, border-color 0.1s, color 0.1s;
                    }}
                    .download-button:hover {{
                        border-color: red;
                        color: red;
                    }}
                    </style>
                    
                    <a href="data:application/octet-stream;base64,{get_base64_encoded_file(download_file_path)}" download="average_days_to_close.png" class="download-button">Download This Figure</a>
                    """,
                    unsafe_allow_html=True,
                )

        with col2:
            avg_days_value = df3.query(
                "`year_opened` == @current_year and `month_opened` == @current_month - 1"
            ).rounded_days_active.squeeze()

            delta_month_change_metric = round(
                (
                    (
                        df3.query(
                            "`year_opened` == @current_year and `month_opened` == @current_month - 1"
                        ).rounded_days_active.squeeze()
                        - df3.query(
                            "`year_opened` == @current_year and `month_opened` == @current_month - 2"
                        ).rounded_days_active.squeeze()
                    )
                    / df3.query(
                        "`year_opened` == @current_year and `month_opened` == @current_month - 2"
                    ).rounded_days_active.squeeze()
                )
                * 100,
                1,
            )

            delta_year_change_metric = round(
                (
                    (
                        df3.query(
                            "`year_opened` == @current_year and `month_opened` == @current_month - 1"
                        ).rounded_days_active.squeeze()
                        - df3.query(
                            "`year_opened` == @current_year - 1 and `month_opened` == @current_month - 1"
                        ).rounded_days_active.squeeze()
                    )
                    / df3.query(
                        "`year_opened` == @current_year - 1 and `month_opened` == @current_month - 1"
                    ).rounded_days_active.squeeze()
                )
                * 100,
                1,
            )
            st.metric(
                label="Avg. Days to Close",
                value=avg_days_value,
                delta=f"{delta_month_change_metric}%",
                delta_color="inverse",
                help=f"The average number of days to close a ticket  {'increased' if delta_month_change_metric > 0 else 'decreased'} by {delta_month_change_metric}% month over month and  {'increased' if delta_year_change_metric > 0 else 'decreased'} by {delta_year_change_metric}% year over year.",
            )

            df3_styled = df3.drop(columns="average_days_active").rename(
                columns={
                    "year_opened": "Year",
                    "month_opened": "Month",
                    "rounded_days_active": "Days Active",
                }
            )

            df3_styled = df3_styled[::-1].style.format({"year_opened": "{:.0f}"})

            st.dataframe(df3_styled, use_container_width=True, hide_index=True)

    progress_bar.progress(40, text=progress_text)

    # also consider start date here
    products_of_interest = list(
        df.query("year_opened >= 2022 and product_type.notnull()")
        .product_type.value_counts(dropna=True)[:6]
        .reset_index()
        .product_type
    )

    if "Other" in products_of_interest:
        products_of_interest.remove("Other")
        products_of_interest.append("Other")
    else:
        products_of_interest.append("Other")

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
        col1, col2 = st.columns([0.8, 0.2], gap="small")

        with col1:
            # Fig 3: Average tickets by product per month
            fig, ax = plt.subplots(figsize=(30, 13))

            brplot = sns.barplot(
                data=df5.query(
                    f"year_month >= '{current_year - 1}-1' and year_month < '{current_year}-{current_month}'"
                ),
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
                f"Number of Tickets per Month by Product {current_year - 1} - Present",
                x=0.113,
                y=0.93,
                ha="left",
                va="bottom",
                fontsize=20,
            )

            ax.grid(color="k", linestyle="-", axis="y", alpha=0.1)
            sns.despine(bottom=True, left=True)

            st.pyplot(fig=fig)
            download_tab_3_button = st.empty()
            download_tab_3_button.button(
                "Download This Figure", disabled=True, key="tab3_download"
            )

            if download_figs:
                plt.savefig("count_product_tickets.png", dpi=300, bbox_inches="tight")
                download_tab_3_button.empty()
                download_file_path = "count_product_tickets.png"
                st.markdown(
                    f"""
                    <style>
                    .download-button {{
                        text-decoration: none;
                        padding: 6px 12px;
                        background-color: transparent;
                        color: white;
                        border-radius: 4px;
                        border: 2px solid #D3D3D3;
                        cursor: pointer;
                        display: inline-block;
                        transition: background-color 0.3s, border-color 0.1s, color 0.1s;
                    }}
                    .download-button:hover {{
                        border-color: red;
                        color: red;
                    }}
                    </style>
                    
                    <a href="data:application/octet-stream;base64,{get_base64_encoded_file(download_file_path)}" download="count_product_tickets.png" class="download-button">Download This Figure</a>
                    """,
                    unsafe_allow_html=True,
                )

        with col2:
            prev_mo_vals = [
                df5.query(
                    f"`year_opened` == {current_year} and `month_opened` == {current_month - 2} and `product_type` == @i"
                    # "`year_opened` == @current_year and `month_opened` == @current_month - 2 and `product_type` == @i"
                )["count"].squeeze()
                for i in products_of_interest
            ]
            curr_mo_vals = [
                df5.query(
                    f"`year_opened` == {current_year} and `month_opened` == {current_month - 1} and `product_type` == @i"
                )["count"].squeeze()
                for i in products_of_interest
            ]
            delta_vals = [
                round((curr - prev) / prev * 100, 1)
                for prev, curr in zip(prev_mo_vals, curr_mo_vals)
            ]

            for idx, i in enumerate(curr_mo_vals):
                st.metric(
                    label=products_of_interest[idx],
                    value=i,
                    delta=f"{delta_vals[idx]}%",
                    delta_color="inverse",
                    help=f"The number of tickets for {products_of_interest[idx]} {'increased' if delta_vals[idx] > 0 else 'decreased'} by {delta_vals[idx]}% month over month",
                )

    progress_bar.progress(60, text=progress_text)

    df6 = df.copy()
    df6.loc[
        df6.client_name == "The Red Sea Development Co., (TRSDC)", "client_name"
    ] = "TRSDC"
    # this might be something to consider if including a start date
    clients_of_interest = list(
        df6.query("year_opened >= 2022")
        .client_name.value_counts(dropna=True)[:5]
        .reset_index()
        .client_name
    ) + ["Other"]
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
        col1, col2 = st.columns([0.8, 0.2], gap="small")

        with col1:
            # Fig 4: Average tickets by client per month
            fig, ax = plt.subplots(figsize=(30, 13))

            brplot = sns.barplot(
                data=df7.query(
                    f"year_month >= '{current_year - 1}-1' and year_month < '{current_year}-{current_month}'"
                ),
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
                f"Number of Tickets per Month by Client {current_year - 1} - Present",
                x=0.1121,
                y=0.93,
                ha="left",
                va="bottom",
                fontsize=20,
            )

            ax.grid(color="k", linestyle="-", axis="y", alpha=0.1)
            sns.despine(bottom=True, left=True)

            st.pyplot(fig=fig)
            download_tab_4_button = st.empty()
            download_tab_4_button.button(
                "Download This Figure", disabled=True, key="tab4_download"
            )

            if download_figs:
                plt.savefig("count_client_tickets.png", dpi=300, bbox_inches="tight")
                download_tab_4_button.empty()
                download_file_path = "count_client_tickets.png"
                st.markdown(
                    f"""
                    <style>
                    .download-button {{
                        text-decoration: none;
                        padding: 6px 12px;
                        background-color: transparent;
                        color: white;
                        border-radius: 4px;
                        border: 2px solid #D3D3D3;
                        cursor: pointer;
                        display: inline-block;
                        transition: background-color 0.3s, border-color 0.1s, color 0.1s;
                    }}
                    .download-button:hover {{
                        border-color: red;
                        color: red;
                    }}
                    </style>
                    
                    <a href="data:application/octet-stream;base64,{get_base64_encoded_file(download_file_path)}" download="count_client_tickets.png" class="download-button">Download This Figure</a>
                    """,
                    unsafe_allow_html=True,
                )

        with col2:
            prev_mo_vals = [
                df7.query(
                    f"`year_opened` == {current_year} and `month_opened` == {current_month - 2} and `client_name` == @i"
                )["count"].squeeze()
                for i in clients_of_interest
            ]

            curr_mo_vals = [
                df7.query(
                    f"`year_opened` == {current_year} and `month_opened` == {current_month - 1} and `client_name` == @i"
                )["count"].squeeze()
                for i in clients_of_interest
            ]

            delta_vals = [
                round((curr - prev) / prev * 100, 1)
                for prev, curr in zip(prev_mo_vals, curr_mo_vals)
            ]

            for idx, i in enumerate(curr_mo_vals):
                st.metric(
                    label=clients_of_interest[idx],
                    value=i,
                    delta=f"{delta_vals[idx]}%",
                    delta_color="inverse",
                    help=f"The number of tickets for {clients_of_interest[idx]} {'increased' if delta_vals[idx] > 0 else 'decreased'} by {delta_vals[idx]}% month over month",
                )

    progress_bar.progress(80, text=progress_text)

    df8 = df.query("ticket_status == 'Closed' and product_type.notnull()")
    df8.loc[~df8.product_type.isin(products_of_interest), "product_type"] = "Other"

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
        col1, col2 = st.columns([0.8, 0.2], gap="small")

        with col1:
            # Fig 5: Average tickets by client per month
            fig, ax = plt.subplots(figsize=(30, 13))

            brplot = sns.barplot(
                data=df8.query(
                    f"year_month >= '{current_year - 1}-1' and year_month < '{current_year}-{current_month}'"
                ),
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
                f"Average Number of Days to Close Tickets each Month by Product {current_year - 1} - Present",
                x=0.113,
                y=0.93,
                ha="left",
                va="bottom",
                fontsize=20,
            )

            ax.grid(color="k", linestyle="-", axis="y", alpha=0.1)
            sns.despine(bottom=True, left=True)

            st.pyplot(fig=fig)
            download_tab_5_button = st.empty()
            download_tab_5_button.button(
                "Download This Figure", disabled=True, key="tab5_download"
            )

            if download_figs:
                plt.savefig("average_days_by_product.png", dpi=300, bbox_inches="tight")
                download_tab_5_button.empty()
                download_file_path = "average_days_by_product.png"
                st.markdown(
                    f"""
                    <a href="data:application/octet-stream;base64,{get_base64_encoded_file(download_file_path)}" download="average_days_by_product.png" class="download-button">Download This Figure</a>
                    """,
                    unsafe_allow_html=True,
                )

        with col2:
            prev_mo_vals = [
                df8.query(
                    f"`year_opened` == {current_year} and `month_opened` == {current_month - 2} and `product_type` == @i"
                )["rounded_days_active"].squeeze()
                for i in products_of_interest
            ]

            curr_mo_vals = [
                df8.query(
                    f"`year_opened` == {current_year} and `month_opened` == {current_month - 1} and `product_type` == @i"
                ).rounded_days_active.squeeze()
                for i in products_of_interest
            ]

            delta_vals = [
                round((curr - prev) / prev * 100, 1)
                for prev, curr in zip(prev_mo_vals, curr_mo_vals)
            ]
            for idx, i in enumerate(curr_mo_vals):
                st.metric(
                    label=products_of_interest[idx],
                    value=i,
                    delta=f"{delta_vals[idx]}%",
                    delta_color="inverse",
                    # help=f"The average number of days to close out {products_of_interest[idx]} {'increased' if delta_vals[idx] > 0 else 'decreased'} by {delta_vals[idx]}% month over month",
                )

    progress_bar.progress(100, text=progress_text)

    if download_figs:
        figures = [
            "tickets_per_month.png",
            "average_days_to_close.png",
            "count_product_tickets.png",
            "count_client_tickets.png",
            "average_days_by_product.png",
        ]

        with zipfile.ZipFile("figures.zip", "w") as zipf:
            for figure in figures:
                zipf.write(figure)

        download_section.markdown(
            f"""
        <style>
        .download-all-button {{
            text-decoration: none !important;
            padding: 6px 12px;
            background-color: transparent;
            color: white !important;
            border-radius: 4px;
            border: 2px solid #D3D3D3;
            cursor: pointer;
            display: inline-block;
            transition: background-color 0s, border-color 0s, color 0s;
            width: 100%;
            box-sizing: border-box;
            text-align: center;
        }}
        .download-all-button:hover {{
            text-decoration: none !important;
            border-color: red;
            color: red !important;
        }}
        </style>
        <a href="data:application/zip;base64,{get_base64_encoded_file("figures.zip")}" download="figures.zip" class="download-all-button">Download All Figures</a>
        """,
            unsafe_allow_html=True,
        )
        temp_download_all_button.empty()

    progress_bar.empty()

    return


st.subheader("Input Excel file below or select an archived report from the sidebar")

uploaded_file = st.file_uploader(label="hidden label", label_visibility="collapsed")
file_removed = False

current_year = datetime.now().year
current_month = datetime.now().month


# st.sidebar.divider()

# st.sidebar.subheader("Custom Date Configuration:")
# st.sidebar.subheader(":blue[in testing...]")

# st.sidebar.divider()


# st.sidebar.subheader("Interactive Charts:")
# interactive_charts_check = st.sidebar.checkbox(
#     "Enable Interactive Charts",
#     help="Check to enable interactive charts. Does not support downloading of interactive charts, will instead download static charts if download is enabled.",
# )

st.sidebar.subheader("Configure Start Date :red[NOT ACTIVE YET]")

start_month = st.sidebar.selectbox(
    label="Starting Month",
    options=([calendar.month_name[i] for i in range(1, 13)]),
    index=0,
    help="Please select a starting month for the figures. ",
)
start_year = st.sidebar.selectbox(
    label="Starting Year",
    options=([current_year - i for i in range(0, 10)]),
    index=1,
    help="Please select a starting year for the figures.",
)
st.sidebar.subheader("Configure End Date :red[NOT ACTIVE YET]")
end_month = st.sidebar.selectbox(
    label="Ending Month",
    options=([calendar.month_name[i] for i in range(1, 13)]),
    index=current_month - 1,
    help="Please select an ending month for the figures.",
)
end_year = st.sidebar.selectbox(
    label="Ending Year",
    options=([current_year - i for i in range(0, 10)]),
    index=0,
    help="Please select an ending year for the figures.",
)

st.sidebar.write(f"Selected Range:")
st.sidebar.write(f"{start_month}, {start_year} - {end_month}, {end_year}")

st.sidebar.divider()

st.sidebar.subheader("Figure Downloads:")
download_section = st.sidebar.container()
download_checkbox = download_section.checkbox(
    "Enable Figure Downloads",
    help="Check to enable figure downloads. Slows down load time if enabled. Will enable both individual figure downloads as well as downloading all figures at once.",
)

st.sidebar.divider()

st.sidebar.subheader("Archived Reports:")
if st.sidebar.button(label="April 2023", use_container_width=True):
    create_figures(
        data="coe_kpi_04_2023.xlsx", current_month=5, download_figs=download_checkbox
    )
    file_removed = True
if st.sidebar.button(label="May 2023", use_container_width=True):
    create_figures(
        data="coe_kpi_05_2023.xlsx",
        current_month=6,
        download_figs=download_checkbox,
        # interactive_charts=interactive_charts_check
        # start_month=start_month,
        # start_year=start_year,
        # end_month=end_month,
        # end_year=end_year,
    )
    file_removed = True

if uploaded_file and not file_removed:
    # will only work for current month
    # for example, in june, can run the report with all of may data, but can't run a report with no may data
    upload_success = st.success(
        f"{uploaded_file.name} has been successfully uploaded!",
        icon="✅",
    )
    create_figures(
        data=uploaded_file,
        download_figs=download_checkbox,
    )

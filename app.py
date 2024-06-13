import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(layout="wide")

# Custom CSS to increase the width of the metric containers
st.markdown(
    """
    <style>
    [data-testid="metric-container"] {
        width: 100%;
        min-width: 200px;
        max-width: 220px;
        padding: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def set_page(page_name):
    st.session_state["current_page"] = page_name

# Always Start on Introduction
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Introduction"

# Pages Menu
st.sidebar.title("UK General Election Predictor")
st.sidebar.header("About")
if st.sidebar.button("Introduction"):
    set_page("Introduction")
if st.sidebar.button("Methodology"):
    set_page("Methodology")

st.sidebar.header("Models")
if st.sidebar.button("Polls Model"):
    set_page("Polling Model")
if st.sidebar.button("Polls & Econ Model"):
    set_page("Polling + Eco Model")
if st.sidebar.button("Polls, Econ, Alt Model"):
    set_page("Polling + Eco + Alt Data")
if st.sidebar.button("Polls, Econ, Alt, Sent Model"):
    set_page("Polling + Eco + Alt Sentiment")
# if st.sidebar.button("Data"):
#     set_page("Data")
# if st.sidebar.button("Charts"):
#     set_page("Charts")

# Party Colors
party_colors = {
    "Labour": "#dd0018",
    "Conservative": "#005af0",
    "SNP": "#fff293",
    "Liberal Democrats": "#ffa331",
    "Plaid Cymru": "#00d4a7",
    "UKIP": "#480c64",
    "Green": "#00bc3e",
    "Others": "#909090"
}

# Legend
def display_legend(election_year, data_path_2010:str, data_path_2015:str, data_path_2017:str,
                   data_path_2019:str, data_path_2024:str):

    data_path = None

    if election_year == 2010:
        data_path = data_path_2010
    elif election_year == 2015:
        data_path = data_path_2015
    elif election_year == 2017:
        data_path = data_path_2017
    elif election_year == 2019:
        data_path = data_path_2019
    elif election_year == 2024:
        data_path = data_path_2024

    party_count_df = pd.read_csv(data_path)
    legend_html = ""
    for party, color in party_colors.items():
        if party in party_count_df['elected_mp_party_name'].values:
            legend_html += f"<span style='font-size:20px; color:{color};'>⬣</span> <span style='font-size:15px;'>{party}</span> &nbsp;&nbsp;&nbsp;"
    st.markdown(f"<div style='display: flex; justify-content: center; align-items: center;'>{legend_html}</div>", unsafe_allow_html=True)

# Handle slider for election year
def election_year_slider():
    # Slider
    col1, col2, col3 = st.columns([1,3,1])

    election_year = None

    with col2:
        election_year = st.select_slider('Select election year:', options=[2010, 2015, 2017, 2019, 2024])

    return election_year

# Hexmap Page Template
def display_hexmap(election_year:int, data_path_2010:str, data_path_2015:str, data_path_2017:str,
                   data_path_2019:str, data_path_2024:str):
    """
    Generates a hexmap of the UK constituency seats, coloured by winning parties.

    :param election_year: The election year.
    :param data_path_2010: Path to the 2010 election data.
    :param data_path_2015: Path to the 2015 election data.
    :param data_path_2017: Path to the 2017 election data.
    :param data_path_2019: Path to the 2019 election data.
    :param data_path_2024: Path to the 2024 election data.

    :return: Hexmap.
    """
    col1, col2, col3 = st.columns([1,3,1])


    with col2:

        # CSV Path Variable
        csv_path = None

        # Loading CSVs
        if election_year == 2010:
            csv_path = data_path_2010
        elif election_year == 2015:
            csv_path = data_path_2015
        elif election_year == 2017:
            csv_path = data_path_2017
        elif election_year == 2019:
            csv_path = data_path_2019
        elif election_year == 2024:
            csv_path = data_path_2024

        constituency_df = pd.read_csv(csv_path)

        # Define functions to flip and rotate coordinates
        def flip_coords(x, y):
            return x, -y

        def rotate_coords_anticlockwise(x, y):
            return -y, x

        # Apply the flipping and rotation transformations
        constituency_df[['x_flipped', 'y_flipped']] = constituency_df.apply(lambda row: flip_coords(row['coord_one'], row['coord_two']), axis=1).apply(pd.Series)
        constituency_df[['x_rotated', 'y_rotated']] = constituency_df.apply(lambda row: rotate_coords_anticlockwise(row['x_flipped'], row['y_flipped']), axis=1).apply(pd.Series)

        # Create the plotly figure
        fig = go.Figure()

        # Add hexagons to the figure with the transformed coordinates
        for _, row in constituency_df.iterrows():
            fig.add_trace(go.Scatter(
                x=[row['x_rotated']],
                y=[row['y_rotated']],
                mode='markers',
                marker_symbol='hexagon2',
                marker=dict(size=18, color=row['color'], line=dict(color='black', width=0.5)),
                text=row['constituency_name'],
                hoverinfo='text'
            ))

        # Update layout
        fig.update_layout(
            xaxis=dict(showgrid=False, zeroline=False, visible=False),
            yaxis=dict(showgrid=False, zeroline=False, visible=False),
            plot_bgcolor='white',
            margin=dict(l=0, r=0, t=0, b=0),
            height=800,
            hovermode='closest',
            showlegend=False
        )


        st.plotly_chart(fig)

# Scorecards
def display_constituency_seat_metrics(election_year, label, data_path_2010:str, data_path_2015:str, data_path_2017:str,
                   data_path_2019:str, data_path_2024:str):

    data_path = None

    # Set the path based on the election year
    if election_year == 2010:
        data_path = data_path_2010
    elif election_year == 2015:
        data_path = data_path_2015
    elif election_year == 2017:
        data_path = data_path_2017
    elif election_year == 2019:
        data_path = data_path_2019
    elif election_year == 2024:
        data_path = data_path_2024

    party_count_df = pd.read_csv(data_path)
    previous_year_count = {}

    # Compute previous year counts if the election year is not 2010
    if election_year != 2010:
        if election_year == 2015:
            previous_year = 2010
        else:
            previous_year = election_year - 2 if election_year != 2024 else 2019
        previous_party_count_csv_path = Path(f"data/party_count/ge_{previous_year}_party_count.csv")
        previous_party_count_df = pd.read_csv(previous_party_count_csv_path)
        previous_year_count = dict(zip(previous_party_count_df['elected_mp_party_name'], previous_party_count_df['elected_mp_party_count']))

    st.write(label)
    cols = st.columns(len(party_count_df))
    for i, (index, row) in enumerate(party_count_df.iterrows()):
        party_name = row['elected_mp_party_name']
        count = row['elected_mp_party_count']

        # Set delta and delta_color only if there is a previous year to compare
        if election_year == 2010:
            delta = None
            delta_color = "normal"
        else:
            delta = count - previous_year_count.get(party_name, 0)
            delta_color = "normal" if delta != 0 else "off"

        with cols[i]:
            if election_year == 2010:
                st.metric(label=party_name, value=count)
            else:
                st.metric(label=party_name, value=count, delta=delta, delta_color=delta_color)


def display_vote_share_metrics(election_year, label, data_path_2010:str, data_path_2015:str, data_path_2017:str,
                   data_path_2019:str, data_path_2024:str):
    # Define paths based on election year
    data_path = None

    # Set the path based on the election year
    if election_year == 2010:
        data_path = data_path_2010
    elif election_year == 2015:
        data_path = data_path_2015
    elif election_year == 2017:
        data_path = data_path_2017
    elif election_year == 2019:
        data_path = data_path_2019
    elif election_year == 2024:
        data_path = data_path_2024

    party_count_df = pd.read_csv(data_path)
    previous_year_vote_share = {}

    # Compute previous year vote shares if the election year is not 2010
    if election_year != 2010:
        if election_year == 2015:
            previous_year = 2010
        else:
            previous_year = election_year - 2 if election_year != 2024 else 2019
        previous_vote_share_csv_path = Path(f"data/vote_share/ge_{previous_year}_vote_share.csv")
        previous_vote_share_df = pd.read_csv(previous_vote_share_csv_path)
        previous_year_vote_share = dict(zip(previous_vote_share_df['party_code'], previous_vote_share_df['mean_average']))

    st.write(label)
    cols = st.columns(len(party_count_df))
    for i, (index, row) in enumerate(party_count_df.iterrows()):
        party_code = row['party_code']
        mean_average = row['mean_average']

        # Set delta and delta_color only if there is a previous year to compare
        if election_year == 2010:
            delta = None
            delta_color = "normal"
        else:
            delta = mean_average - previous_year_vote_share.get(party_code, 0)
            delta_color = "normal" if delta != 0 else "off"

        with cols[i]:
            if election_year == 2010:
                st.metric(label=party_code, value=f"{mean_average}%")
            else:
                st.metric(label=party_code, value=f"{mean_average}%", delta=f"{delta}%", delta_color=delta_color)

# Handle rendering of pages

# Introduction Page
if st.session_state["current_page"] == "Introduction":
    st.title("Introduction")
    st.write("""
        Welcome to the UK Electoral Map Project!

        There is nothing here YET... go away!
    """)

# Methodology Page
if st.session_state["current_page"] == "Methodology":
    st.title("Methodology")
    st.write("""
        Methodology Page.
    """)

# Polling Model Page
if st.session_state["current_page"] == "Polling Model":
    col1, col2, col3 = st.columns([1,3,1])

    with col2:
        st.title("Polling Model")

    election_year = election_year_slider()

    display_legend(
        election_year,
        "data/polls_model/hexmap/polls_model_hexmap_2010.csv",
        "data/polls_model/hexmap/polls_model_hexmap_2015.csv",
        "data/polls_model/hexmap/polls_model_hexmap_2017.csv",
        "data/polls_model/hexmap/polls_model_hexmap_2019.csv",
        "data/polls_model/hexmap/polls_model_hexmap_2024.csv"
    )

    display_hexmap(
        election_year,
        "data/polls_model/hexmap/polls_model_hexmap_2010.csv",
        "data/polls_model/hexmap/polls_model_hexmap_2015.csv",
        "data/polls_model/hexmap/polls_model_hexmap_2017.csv",
        "data/polls_model/hexmap/polls_model_hexmap_2019.csv",
        "data/polls_model/hexmap/polls_model_hexmap_2024.csv",
    )

#     display_constituency_seat_metrics(
#         election_year,
#         "Constituency Seat Count",
#         "data/party_count/ge_2010_party_count.csv",
#         "data/party_count/ge_2015_party_count.csv",
#         "data/party_count/ge_2017_party_count.csv",
#         "data/party_count/ge_2019_party_count.csv",
#         "data/party_count/ge_2024_party_count.csv",
#     )


#     display_vote_share_metrics(
#         election_year,
#         "National Vote Share",
#         "data/vote_share/ge_2010_vote_share.csv",
#         "data/vote_share/ge_2015_vote_share.csv",
#         "data/vote_share/ge_2017_vote_share.csv",
#         "data/vote_share/ge_2019_vote_share.csv",
#         "data/vote_share/ge_2024_vote_share.csv",
#     )

# # Polling + Eco Model Page
# elif st.session_state["current_page"] == "Polling + Eco Model":
#     col1, col2, col3 = st.columns([1,3,1])

#     with col2:
#         st.title("Polling + Eco Model")

#     election_year = election_year_slider()

#     display_legend(election_year)

#     display_hexmap(
#         election_year,
#         "data/constituencies/ge_2010_constituencies.csv",
#         "data/constituencies/ge_2015_constituencies.csv",
#         "data/constituencies/ge_2017_constituencies.csv",
#         "data/constituencies/ge_2019_constituencies.csv",
#         "data/constituencies/ge_2024_constituencies.csv"
#     )

#     display_constituency_seat_metrics(
#         election_year,
#         "Constituency Seat Count",
#         "data/party_count/ge_2010_party_count.csv",
#         "data/party_count/ge_2015_party_count.csv",
#         "data/party_count/ge_2017_party_count.csv",
#         "data/party_count/ge_2019_party_count.csv",
#         "data/party_count/ge_2024_party_count.csv",
#     )


#     display_vote_share_metrics(
#         election_year,
#         "National Vote Share",
#         "data/vote_share/ge_2010_vote_share.csv",
#         "data/vote_share/ge_2015_vote_share.csv",
#         "data/vote_share/ge_2017_vote_share.csv",
#         "data/vote_share/ge_2019_vote_share.csv",
#         "data/vote_share/ge_2024_vote_share.csv",
#     )

# # Polling + Eco + Alt Data Page
# elif st.session_state["current_page"] == "Polling + Eco + Alt Data":
#     col1, col2, col3 = st.columns([1,3,1])

#     with col2:
#         st.title("Polling + Eco + Alt Data")

#     election_year = election_year_slider()

#     display_legend(election_year)

#     display_hexmap(
#         election_year,
#         "data/constituencies/ge_2010_constituencies.csv",
#         "data/constituencies/ge_2015_constituencies.csv",
#         "data/constituencies/ge_2017_constituencies.csv",
#         "data/constituencies/ge_2019_constituencies.csv",
#         "data/constituencies/ge_2024_constituencies.csv"
#     )

#     display_constituency_seat_metrics(
#         election_year,
#         "Constituency Seat Count",
#         "data/party_count/ge_2010_party_count.csv",
#         "data/party_count/ge_2015_party_count.csv",
#         "data/party_count/ge_2017_party_count.csv",
#         "data/party_count/ge_2019_party_count.csv",
#         "data/party_count/ge_2024_party_count.csv",
#     )

#     display_vote_share_metrics(
#         election_year,
#         "National Vote Share",
#         "data/vote_share/ge_2010_vote_share.csv",
#         "data/vote_share/ge_2015_vote_share.csv",
#         "data/vote_share/ge_2017_vote_share.csv",
#         "data/vote_share/ge_2019_vote_share.csv",
#         "data/vote_share/ge_2024_vote_share.csv",
#     )

# # Polling + Eco + Alt Sentiment Page
# elif st.session_state["current_page"] == "Polling + Eco + Alt Sentiment":
#     col1, col2, col3 = st.columns([1,3,1])

#     with col2:
#         st.title("Polling + Eco + Alt Sentiment")

#     election_year = election_year_slider()

#     display_legend(election_year)

#     display_hexmap(
#         election_year,
#         "data/constituencies/ge_2010_constituencies.csv",
#         "data/constituencies/ge_2015_constituencies.csv",
#         "data/constituencies/ge_2017_constituencies.csv",
#         "data/constituencies/ge_2019_constituencies.csv",
#         "data/constituencies/ge_2024_constituencies.csv"
#     )

#     display_constituency_seat_metrics(
#         election_year,
#         "Constituency Seat Count",
#         "data/party_count/ge_2010_party_count.csv",
#         "data/party_count/ge_2015_party_count.csv",
#         "data/party_count/ge_2017_party_count.csv",
#         "data/party_count/ge_2019_party_count.csv",
#         "data/party_count/ge_2024_party_count.csv",
#     )


#     display_vote_share_metrics(
#         election_year,
#         "National Vote Share",
#         "data/vote_share/ge_2010_vote_share.csv",
#         "data/vote_share/ge_2015_vote_share.csv",
#         "data/vote_share/ge_2017_vote_share.csv",
#         "data/vote_share/ge_2019_vote_share.csv",
#         "data/vote_share/ge_2024_vote_share.csv",
#     )

# # # Data Page
# # elif st.session_state["current_page"] == "Data":
# #     col1, col2, col3 = st.columns([1,3,1])

# #     with col2:
# #         st.title("Data")

# #     election_year = election_year_slider()

# #     display_legend(election_year)

# #     display_hexmap(
# #         election_year,
# #         "data/constituencies/ge_2010_constituencies.csv",
# #         "data/constituencies/ge_2015_constituencies.csv",
# #         "data/constituencies/ge_2017_constituencies.csv",
# #         "data/constituencies/ge_2019_constituencies.csv",
# #         "data/constituencies/ge_2024_constituencies.csv"
# #     )

# #     display_constituency_seat_metrics(
# #         election_year,
# #         "Constituency Seat Count",
# #         "data/party_count/ge_2010_party_count.csv",
# #         "data/party_count/ge_2015_party_count.csv",
# #         "data/party_count/ge_2017_party_count.csv",
# #         "data/party_count/ge_2019_party_count.csv",
# #         "data/party_count/ge_2024_party_count.csv",
# #     )


# #     display_vote_share_metrics(
# #         election_year,
# #         "National Vote Share",
# #         "data/vote_share/ge_2010_vote_share.csv",
# #         "data/vote_share/ge_2015_vote_share.csv",
# #         "data/vote_share/ge_2017_vote_share.csv",
# #         "data/vote_share/ge_2019_vote_share.csv",
# #         "data/vote_share/ge_2024_vote_share.csv",
# #     )

# # # Charts Page
# # elif st.session_state["current_page"] == "Charts":

#     # st.title("Charts")

#     # election_year = election_year_slider()

#     # display_legend(election_year)

#     # display_hexmap(
#     #     election_year,
#     #     "data/constituencies/ge_2010_constituencies.csv",
#     #     "data/constituencies/ge_2015_constituencies.csv",
#     #     "data/constituencies/ge_2017_constituencies.csv",
#     #     "data/constituencies/ge_2019_constituencies.csv",
#     #     "data/constituencies/ge_2024_constituencies.csv"
#     # )

#     # display_constituency_seat_metrics(
#     #     election_year,
#     #     "Constituency Seat Count",
#     #     "data/party_count/ge_2010_party_count.csv",
#     #     "data/party_count/ge_2015_party_count.csv",
#     #     "data/party_count/ge_2017_party_count.csv",
#     #     "data/party_count/ge_2019_party_count.csv",
#     #     "data/party_count/ge_2024_party_count.csv",
#     # )


#     # display_vote_share_metrics(
#     #     election_year,
#     #     "National Vote Share",
#     #     "data/vote_share/ge_2010_vote_share.csv",
#     #     "data/vote_share/ge_2015_vote_share.csv",
#     #     "data/vote_share/ge_2017_vote_share.csv",
#     #     "data/vote_share/ge_2019_vote_share.csv",
#     #     "data/vote_share/ge_2024_vote_share.csv",
#     # )

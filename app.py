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

    footer {visibility: hidden;}

    </style>
    """,
    unsafe_allow_html=True
)

def set_page(page_name):
    st.session_state["current_page"] = page_name

# Always Start on "Polling + Econ + Social Media Model"
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Polling + Econ + Social Media Model"


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
if st.sidebar.button("Polls & Economics Model"):
    set_page("Polling + Econ Model")
if st.sidebar.button("Polls & Social Media Model"):
    set_page("Polling + Social Media Model")
if st.sidebar.button("Polls, Economics & Social Media Model"):
    set_page("Polling + Econ + Social Media Model")
# if st.sidebar.button("Data"):
#     set_page("Data")
# if st.sidebar.button("Charts"):
#     set_page("Charts")

# Party Colors
party_colors = {
    "Conservative": "#005af0",
    "Labour": "#dd0018",
    "Green": "#00bc3e",
    "Liberal Democrats": "#ffa331",
    "Plaid Cymru": "#00d4a7",
    "SNP": "#fff293",
    "UKIP": "#480c64",
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
        election_year = st.select_slider('Select election year:', options=[2010, 2015, 2017, 2019, 2024], value=2019)

    return election_year

# Hexmap Logic
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

        # # Define a function to calculate hexagon coordinates based on the "odd-r" formation
        # def calc_coords(row, col):
        #     if row % 2 == 1:
        #         col = col + 0.5
        #     row = row * np.sqrt(3) / 2
        #     return col, row

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
                marker=dict(
                    size=16,
                    color=row['color'],
                    line=dict(color='black', width=0.5),
                    angle=90),
                text=row['constituency_name'],
                hoverinfo='text'
            ))

        # Update layout
        fig.update_layout(
            xaxis=dict(showgrid=False, zeroline=False, visible=False),
            yaxis=dict(showgrid=False, zeroline=False, visible=False),
            plot_bgcolor='#0E1117',
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
    predicted_party_count = dict(zip(party_count_df['Party'], party_count_df['Total_Constituencies']))

    # Read actual data only if the year is not 2010 or 2024
    if election_year not in [2024]:
        actuals_csv_path = Path(f"data/actuals/seat_share/actual_seat_share_{election_year}.csv")
        actuals_party_count_df = pd.read_csv(actuals_csv_path)
        actuals_party_count = dict(zip(actuals_party_count_df['Party'], actuals_party_count_df['Total_Constituencies']))

    st.subheader(label)
    cols = st.columns(len(predicted_party_count))
    for i, (party_name, predicted_count) in enumerate(predicted_party_count.items()):
        if election_year in [2024]:
            with cols[i]:
                st.metric(label=party_name, value=predicted_count)
        else:
            actual_count = actuals_party_count.get(party_name, 0)
            delta = actual_count - predicted_count
            delta_color = "normal" if delta != 0 else "off"
            with cols[i]:
                st.metric(label=party_name, value=predicted_count, delta=delta, delta_color=delta_color)

    st.write("*Delta markers display the difference between our model prediction and actual results*")

def display_vote_share_metrics(election_year, label, data_path_2010:str, data_path_2015:str, data_path_2017:str,
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

    party_share_df = pd.read_csv(data_path)
    predicted_party_share = dict(zip(party_share_df['Party'], party_share_df['Vote_Share']))

    # Read actual data only if the year is not 2010 or 2024
    if election_year not in [2024]:
        actuals_csv_path = Path(f"data/actuals/vote_share/actual_vote_share_{election_year}.csv")
        actuals_party_share_df = pd.read_csv(actuals_csv_path)
        actuals_party_share = dict(zip(actuals_party_share_df['Party'], actuals_party_share_df['Vote_Share']))

    st.subheader(label)
    cols = st.columns(len(predicted_party_share))
    for i, (party_name, predicted_share) in enumerate(predicted_party_share.items()):
        if election_year in [2024]:
            with cols[i]:
                st.metric(label=party_name, value=str(predicted_share) + "%")
        else:
            actual_share = actuals_party_share.get(party_name, 0)
            delta = np.round(actual_share - predicted_share)
            delta_color = "normal" if delta != 0 else "off"
            with cols[i]:
                st.metric(label=party_name, value=str(predicted_share) + "%", delta=delta, delta_color=delta_color)



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

    election_year = election_year_slider()

    with col2:
        st.title(f"Polling Model – {election_year} Election Prediction")

    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)

    display_vote_share_metrics(
        election_year,
        f"National Vote Share",
        "data/polls_model/vote_share/polls_model_vote_share_2010.csv",
        "data/polls_model/vote_share/polls_model_vote_share_2015.csv",
        "data/polls_model/vote_share/polls_model_vote_share_2017.csv",
        "data/polls_model/vote_share/polls_model_vote_share_2019.csv",
        "data/polls_model/vote_share/polls_model_vote_share_2024.csv",
    )

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    display_constituency_seat_metrics(
        election_year,
        "Constituency Seat Count",
        "data/polls_model/seat_share/polls_model_seat_share_2010.csv",
        "data/polls_model/seat_share/polls_model_seat_share_2015.csv",
        "data/polls_model/seat_share/polls_model_seat_share_2017.csv",
        "data/polls_model/seat_share/polls_model_seat_share_2019.csv",
        "data/polls_model/seat_share/polls_model_seat_share_2024.csv",
    )

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    st.markdown(f"<div style='display: flex; justify-content: center; align-items: center; font-size:1.8rem; font-weight: 600; margin: 0.5rem 0'>Constituency Seat Map</div>", unsafe_allow_html=True)

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

# Polling + Eco Model Page
elif st.session_state["current_page"] == "Polling + Econ Model":
    col1, col2, col3 = st.columns([1,3,1])

    election_year = election_year_slider()

    with col2:
        st.title(f"Polling & Economics Model – {election_year} Election Prediction")

    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)

    display_vote_share_metrics(
        election_year,
        "National Vote Share",
        "data/polls_econ_model/vote_share/polls_model_econ_vote_share_2010.csv",
        "data/polls_econ_model/vote_share/polls_model_econ_vote_share_2015.csv",
        "data/polls_econ_model/vote_share/polls_model_econ_vote_share_2017.csv",
        "data/polls_econ_model/vote_share/polls_model_econ_vote_share_2019.csv",
        "data/polls_econ_model/vote_share/polls_model_econ_vote_share_2024.csv",
    )

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    display_constituency_seat_metrics(
        election_year,
        "Constituency Seat Count",
        "data/polls_econ_model/seat_share/polls_model_econ_seat_share_2010.csv",
        "data/polls_econ_model/seat_share/polls_model_econ_seat_share_2015.csv",
        "data/polls_econ_model/seat_share/polls_model_econ_seat_share_2017.csv",
        "data/polls_econ_model/seat_share/polls_model_econ_seat_share_2019.csv",
        "data/polls_econ_model/seat_share/polls_model_econ_seat_share_2024.csv",
    )

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    st.markdown(f"<div style='display: flex; justify-content: center; align-items: center; font-size:1.8rem; font-weight: 600; margin: 0.5rem 0'>Constituency Seat Map</div>", unsafe_allow_html=True)

    display_legend(
        election_year,
        "data/polls_econ_model/hexmap/polls_econ_model_hexmap_2010.csv",
        "data/polls_econ_model/hexmap/polls_econ_model_hexmap_2015.csv",
        "data/polls_econ_model/hexmap/polls_econ_model_hexmap_2017.csv",
        "data/polls_econ_model/hexmap/polls_econ_model_hexmap_2019.csv",
        "data/polls_econ_model/hexmap/polls_econ_model_hexmap_2024.csv"
    )

    display_hexmap(
        election_year,
        "data/polls_econ_model/hexmap/polls_econ_model_hexmap_2010.csv",
        "data/polls_econ_model/hexmap/polls_econ_model_hexmap_2015.csv",
        "data/polls_econ_model/hexmap/polls_econ_model_hexmap_2017.csv",
        "data/polls_econ_model/hexmap/polls_econ_model_hexmap_2019.csv",
        "data/polls_econ_model/hexmap/polls_econ_model_hexmap_2024.csv"
    )

# Polling + Alt Model Page
elif st.session_state["current_page"] == "Polling + Social Media Model":
    col1, col2, col3 = st.columns([1,3,1])

    election_year = election_year_slider()

    with col2:
        st.title(f"Polling & Social Media Model – {election_year} Election Prediction")

    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)

    display_vote_share_metrics(
        election_year,
        "National Vote Share",
        "data/polls_alt_model/vote_share/polls_alt_model_vote_share_2010.csv",
        "data/polls_alt_model/vote_share/polls_alt_model_vote_share_2015.csv",
        "data/polls_alt_model/vote_share/polls_alt_model_vote_share_2017.csv",
        "data/polls_alt_model/vote_share/polls_alt_model_vote_share_2019.csv",
        "data/polls_alt_model/vote_share/polls_alt_model_vote_share_2024.csv",
    )

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    display_constituency_seat_metrics(
        election_year,
        "Constituency Seat Count",
        "data/polls_alt_model/seat_share/polls_alt_model_seat_share_2010.csv",
        "data/polls_alt_model/seat_share/polls_alt_model_seat_share_2015.csv",
        "data/polls_alt_model/seat_share/polls_alt_model_seat_share_2017.csv",
        "data/polls_alt_model/seat_share/polls_alt_model_seat_share_2019.csv",
        "data/polls_alt_model/seat_share/polls_alt_model_seat_share_2024.csv",
    )

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    st.markdown(f"<div style='display: flex; justify-content: center; align-items: center; font-size:1.8rem; font-weight: 600; margin: 0.5rem 0'>Constituency Seat Map</div>", unsafe_allow_html=True)

    display_legend(
        election_year,
        "data/polls_alt_model/hexmap/polls_alt_model_hexmap_2010.csv",
        "data/polls_alt_model/hexmap/polls_alt_model_hexmap_2015.csv",
        "data/polls_alt_model/hexmap/polls_alt_model_hexmap_2017.csv",
        "data/polls_alt_model/hexmap/polls_alt_model_hexmap_2019.csv",
        "data/polls_alt_model/hexmap/polls_alt_model_hexmap_2024.csv"
    )

    display_hexmap(
        election_year,
        "data/polls_alt_model/hexmap/polls_alt_model_hexmap_2010.csv",
        "data/polls_alt_model/hexmap/polls_alt_model_hexmap_2015.csv",
        "data/polls_alt_model/hexmap/polls_alt_model_hexmap_2017.csv",
        "data/polls_alt_model/hexmap/polls_alt_model_hexmap_2019.csv",
        "data/polls_alt_model/hexmap/polls_alt_model_hexmap_2024.csv"
    )

# Polling + Eco + Alt Page
elif st.session_state["current_page"] == "Polling + Econ + Social Media Model":
    col1, col2, col3 = st.columns([1,3,1])

    election_year = election_year_slider()

    with col2:
        st.title(f"Polls, Economics & Social Media Model – {election_year} Election Prediction")

    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)

    display_vote_share_metrics(
        election_year,
        "National Vote Share",
        "data/polls_econ_alt_model/vote_share/polls_eco_alt_model_vote_share_2010.csv",
        "data/polls_econ_alt_model/vote_share/polls_eco_alt_model_vote_share_2015.csv",
        "data/polls_econ_alt_model/vote_share/polls_eco_alt_model_vote_share_2017.csv",
        "data/polls_econ_alt_model/vote_share/polls_eco_alt_model_vote_share_2019.csv",
        "data/polls_econ_alt_model/vote_share/polls_eco_alt_model_vote_share_2024.csv",
    )

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    display_constituency_seat_metrics(
        election_year,
        "Constituency Seat Count",
        "data/polls_econ_alt_model/seat_share/polls_eco_alt_model_seat_share_2010.csv",
        "data/polls_econ_alt_model/seat_share/polls_eco_alt_model_seat_share_2015.csv",
        "data/polls_econ_alt_model/seat_share/polls_eco_alt_model_seat_share_2017.csv",
        "data/polls_econ_alt_model/seat_share/polls_eco_alt_model_seat_share_2019.csv",
        "data/polls_econ_alt_model/seat_share/polls_eco_alt_model_seat_share_2024.csv",
    )

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    st.markdown(f"<div style='display: flex; justify-content: center; align-items: center; font-size:1.8rem; font-weight: 600; margin: 0.5rem 0'>Constituency Seat Map</div>", unsafe_allow_html=True)

    display_legend(
        election_year,
        "data/polls_econ_alt_model/hexmap/polls_econ_alt_model_hexmap_2010.csv",
        "data/polls_econ_alt_model/hexmap/polls_econ_alt_model_hexmap_2015.csv",
        "data/polls_econ_alt_model/hexmap/polls_econ_alt_model_hexmap_2017.csv",
        "data/polls_econ_alt_model/hexmap/polls_econ_alt_model_hexmap_2019.csv",
        "data/polls_econ_alt_model/hexmap/polls_econ_alt_model_hexmap_2024.csv"
    )

    display_hexmap(
        election_year,
        "data/polls_econ_alt_model/hexmap/polls_econ_alt_model_hexmap_2010.csv",
        "data/polls_econ_alt_model/hexmap/polls_econ_alt_model_hexmap_2015.csv",
        "data/polls_econ_alt_model/hexmap/polls_econ_alt_model_hexmap_2017.csv",
        "data/polls_econ_alt_model/hexmap/polls_econ_alt_model_hexmap_2019.csv",
        "data/polls_econ_alt_model/hexmap/polls_econ_alt_model_hexmap_2024.csv"
    )

# # Data Page
# elif st.session_state["current_page"] == "Data":
#     col1, col2, col3 = st.columns([1,3,1])

#     with col2:
#         st.title("Data")

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

# # Charts Page
# elif st.session_state["current_page"] == "Charts":

#     st.title("Charts")

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

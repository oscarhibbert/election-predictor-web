import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path

def set_page(page_name):
    st.session_state["current_page"] = page_name

# Always Start on Introduction
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Introduction"

# Pages Menu
st.sidebar.title("Navigation")
if st.sidebar.button("Introduction"):
    set_page("Introduction")
if st.sidebar.button("Polling Model"):
    set_page("Polling Model")
if st.sidebar.button("Polling + Eco Model"):
    set_page("Polling + Eco Model")
if st.sidebar.button("Polling + Eco + Alt Data"):
    set_page("Polling + Eco + Alt Data")
if st.sidebar.button("Polling + Eco + Alt Sentiment"):
    set_page("Polling + Eco + Alt Sentiment")
if st.sidebar.button("Methodology"):
    set_page("Methodology")
if st.sidebar.button("Data"):
    set_page("Data")
if st.sidebar.button("Charts"):
    set_page("Charts")

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
def display_legend(election_year):
    if election_year == 2015:
        party_count_csv_path = Path("data/party_count/ge_2015_party_count.csv")
    elif election_year == 2017:
        party_count_csv_path = Path("data/party_count/ge_2017_party_count.csv")
    elif election_year == 2019:
        party_count_csv_path = Path("data/party_count/ge_2019_party_count.csv")
    else:
        party_count_csv_path = Path("data/party_count/ge_2019_party_count.csv")

    party_count_df = pd.read_csv(party_count_csv_path)
    legend_html = ""
    for party, color in party_colors.items():
        if party in party_count_df['elected_mp_party_name'].values:
            legend_html += f"<span style='font-size:20px; color:{color};'>⬣</span> <span style='font-size:15px;'>{party}</span> &nbsp;&nbsp;&nbsp;"
    st.markdown(f"<div style='display: flex; justify-content: center; align-items: center;'>{legend_html}</div>", unsafe_allow_html=True)

# Scorecards
def display_metrics(election_year, label):
    if election_year == 2015:
        party_count_csv_path = Path("data/party_count/ge_2015_party_count.csv")
    elif election_year == 2017:
        party_count_csv_path = Path("data/party_count/ge_2017_party_count.csv")
    elif election_year == 2019:
        party_count_csv_path = Path("data/party_count/ge_2019_party_count.csv")
    else:
        party_count_csv_path = Path("data/party_count/ge_2019_party_count.csv")

    party_count_df = pd.read_csv(party_count_csv_path)
    previous_year_count = {}
    if election_year != 2015:
        previous_year = election_year - 2 if election_year != 2024 else 2019
        previous_party_count_csv_path = Path(f"data/party_count/ge_{previous_year}_party_count.csv")
        previous_party_count_df = pd.read_csv(previous_party_count_csv_path)
        previous_year_count = dict(zip(previous_party_count_df['elected_mp_party_name'], previous_party_count_df['elected_mp_party_count']))

    st.write(label)
    cols = st.columns(len(party_count_df))
    for i, (index, row) in enumerate(party_count_df.iterrows()):
        party_name = row['elected_mp_party_name']
        count = row['elected_mp_party_count']
        if election_year == 2015:
            delta = None
            delta_color = "normal"
        else:
            delta = count - previous_year_count.get(party_name, 0)
            delta_color = "normal" if delta != 0 else "off"

        with cols[i]:
            if election_year == 2015:
                st.metric(label=party_name, value=count)
            else:
                st.metric(label=party_name, value=count, delta=delta, delta_color=delta_color)

# Intro Page
if st.session_state["current_page"] == "Introduction":
    st.title("Introduction")
    st.write("""
        Welcome to the UK Electoral Map Project!

        There is nothing here YET... go away!
    """)

# Hexmap Page Template
def display_hexmap(data_path_2010:str, data_path_2015:str, data_path_2017:str,
                   data_path_2019:str, data_path_2024:str):
    """
    Generates a hexmap of the UK constituency seats, coloured by winning parties.

    :param data_path_2010: Path to the 2010 election data.
    :param data_path_2015: Path to the 2015 election data.
    :param data_path_2017: Path to the 2017 election data.
    :param data_path_2019: Path to the 2019 election data.
    :param data_path_2024: Path to the 2024 election data.

    :return: Hexmap.
    """
    # Slider
    election_year = st.select_slider('Select election year:', options=[2015, 2017, 2019, 2024])

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

    # Define a function to calculate hexagon coordinates based on the "odd-r" formation
    def calc_coords(row, col):
        if row % 2 == 1:
            col = col + 0.5
        row = row * np.sqrt(3) / 2
        return col, row

    # Generate hexagon coordinates
    constituency_df['coords'] = constituency_df.apply(lambda row: calc_coords(row['coord_two'], row['coord_one']), axis=1)
    constituency_df[['x', 'y']] = pd.DataFrame(constituency_df['coords'].tolist(), index=constituency_df.index)

    fig = go.Figure()

    # Add hexagons to the figure
    for _, row in constituency_df.iterrows():
        fig.add_trace(go.Scatter(
            x=[row['x']],
            y=[row['y']],
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

    display_legend(election_year)
    st.plotly_chart(fig)
    display_metrics(election_year, "Constituency Seat Count")
    display_metrics(election_year, "National Vote Share")

# Polling Model Page
if st.session_state["current_page"] == "Polling Model":
    st.title("Polling Model")
    display_hexmap()

# Polling + Eco Model Page
elif st.session_state["current_page"] == "Polling + Eco Model":
    st.title("Polling + Eco Model")
    display_hexmap()

# Polling + Eco + Alt Data Page
elif st.session_state["current_page"] == "Polling + Eco + Alt Data":
    st.title("Polling + Eco + Alt Data")
    display_hexmap()

# Polling + Eco + Alt Sentiment Page
elif st.session_state["current_page"] == "Polling + Eco + Alt Sentiment":
    st.title("Polling + Eco + Alt Sentiment")
    display_hexmap()

# Methodology Page
elif st.session_state["current_page"] == "Methodology":
    st.title("Methodology")

# Data Page
elif st.session_state["current_page"] == "Data":
    st.title("Data")

# Charts Page
elif st.session_state["current_page"] == "Charts":
    st.title("Charts")

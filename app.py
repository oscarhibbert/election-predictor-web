import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path

# Define a function to set the page
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

# Intro Page
if st.session_state["current_page"] == "Introduction":
    st.title("Introduction")
    st.write("""
        Welcome to the UK Electoral Map Project!

        There is nothing here YET... go away!
    """)

# Hexmap Page Template
def display_hexmap():
    # Define the paths to the hex CSV file
    hex_csv_path = Path("data/uk_map_hex.csv")

    # Load the hex CSV file
    hex_df = pd.read_csv(hex_csv_path)

    # Create a slider in Streamlit
    election_year = st.select_slider('Select election year:', options=[2015, 2017, 2019, 2024])

    # Load the appropriate constituency CSV file based on the selected year
    if election_year == 2015:
        constituency_csv_path = Path("data/ge_2015_constituencies.csv")
    elif election_year == 2017:
        constituency_csv_path = Path("data/ge_2017_constituencies.csv")
    elif election_year == 2019:
        constituency_csv_path = Path("data/ge_2019_constituencies.csv")
    else:
        constituency_csv_path = Path("data/ge_2019_constituencies.csv")

    constituency_df = pd.read_csv(constituency_csv_path)

    # Merge the hex DataFrame with the constituency data DataFrame
    merged = hex_df.merge(constituency_df, left_on='constituency_name', right_on='constituency_name')

    # Define a function to calculate hexagon coordinates based on the "odd-r" formation
    def calc_coords(row, col):
        if row % 2 == 1:
            col = col + 0.5
        row = row * np.sqrt(3) / 2
        return col, row

    # Generate hexagon coordinates
    merged['coords'] = merged.apply(lambda row: calc_coords(row['coord_two'], row['coord_one']), axis=1)
    merged[['x', 'y']] = pd.DataFrame(merged['coords'].tolist(), index=merged.index)

    fig = go.Figure()

    # Add hexagons to the figure
    for _, row in merged.iterrows():
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

    # Display the plot in Streamlit
    st.plotly_chart(fig)

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

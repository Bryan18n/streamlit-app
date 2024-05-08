'''
Created on May 4, 2024

@author: bryan
Name: Bryan Ng
CS230: Section 1
Date: 7th May 2024 
Description: This program provides an interactive exploration tool for visualizing 
pub locations across the UK. Users can filter pubs by local authority, postal code, 
or search by pub name. The application displays this information through interactive 
maps and charts, enhancing user understanding of pub distributions.
'''
import pandas as pd
import streamlit as st
import pydeck as pdk
import plotly.express as px


# Function to load data from an Excel file
@st.cache_data
def load_data():
    """
    Loads data from an Excel file and processes it for use in the application.
    Converts latitude and longitude to numeric and drops entries without these values.
    """
    column_names = ["fsa_id", "name", "address", "postcode", "easting", "northing", "latitude", "longitude", "local_authority"]
    df = pd.read_excel("open_pubs_10000_sample.xlsx", header=0, names=column_names)
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
    df.dropna(subset=['latitude', 'longitude'], inplace=True)#drop rows or columns which contain missing values 
    return df

 
# Function to apply filters based on user input
def apply_filters(data, authorities, name_query, postal_code):
    """
    Applies various filters to the dataset based on user input.

    Parameters:
        data (pd.DataFrame): The original dataset.
        authorities (list): List of local authorities to filter by.
        name_query (str): The pub name to search for.
        postal_code (str): The postal code to filter by.

    """
    
    filtered_data = data.copy()
    if authorities and "All" not in authorities:  # Checks if the list is not empty and does not contain 'All'
        filtered_data = filtered_data[filtered_data['local_authority'].isin(authorities)]
    if name_query:
        trimmed_query = name_query.strip()
        filtered_data = filtered_data[filtered_data['name'].str.contains(trimmed_query, case=False, na=False)]
    if postal_code != "All":
        filtered_data = filtered_data[filtered_data['postcode'] == postal_code]
    return filtered_data


# Function to create a Pydeck map
def create_pydeck_map(data):
    
    if not data.empty:
        view_state = pdk.ViewState(
            latitude=data['latitude'].mean(),
            longitude=data['longitude'].mean(),
            zoom=10,
            pitch=50
        )
        layer = pdk.Layer(
            'ScatterplotLayer',
            data=data,
            get_position='[longitude, latitude]',
            get_color='[200, 30, 0, 160]',
            get_radius=80,
            pickable=True,
            auto_highlight=True,
            # Tooltip settings
            tooltip={
                "html": "<b>Name:</b> {name}<br><b>Address:</b> {address}<br><b>Postcode:</b> {postcode}<br><b>Local Authority:</b> {local_authority}",
                "style": {
                    "backgroundColor": "steelblue",
                    "color": "white"
                }
            }
        )
        deck = pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v9',
            initial_view_state=view_state,
            layers=[layer],
            tooltip={"text": "{name}\n{address}"}
        )
        st.pydeck_chart(deck)
    else:
        st.write("No data available to display on the map.")

# Function to create a bar chart using Plotly
def display_bar_chart(data):
    if not data.empty:
        chart_data = data['local_authority'].value_counts().reset_index()
        chart_data.columns = ['Local Authority', 'Count']
        fig = px.bar(chart_data, x='Local Authority', y='Count', title="Number of Pubs by Local Authority")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No chart data available.")
        
# Function to display the top 10 cities by number of pubs
def display_top_cities(data):
    if not data.empty:
        # Aggregate the number of pubs by local authority and get the top 10
        chart_data = data['local_authority'].value_counts().nlargest(10).reset_index()
        chart_data.columns = ['City', 'Number of Pubs']
        # Create a bar chart
        fig = px.bar(chart_data, x='City', y='Number of Pubs', title="Top 10 Cities by Number of Pubs")
        fig.update_layout(xaxis_title="City", yaxis_title="Number of Pubs", yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No chart data available.")
        
#sort by length of name 
def display_sorted_pubs(data):
    if not data.empty:
        # Calculate the length of each pub name and add it as a new column
        data['name_length'] = data['name'].apply(len)
        # Sort the dataframe by the length of the pub name
        sorted_data = data.sort_values(by='name_length', ascending=True)
        # Display the sorted data
        st.dataframe(sorted_data[['name', 'address', 'postcode', 'local_authority']])
    else:
        st.write("No data available to display.")
        
# Main function to structure the Streamlit app
def main():
    
    st.sidebar.title("London Pub Explorer")
    page = st.sidebar.radio("Navigation", ["Home", "Saved Pubs"])
    data = load_data()

    authority_options = ['All'] + sorted(data['local_authority'].unique().tolist())
    name_query = st.sidebar.text_input("Search by Pub Name", "", placeholder="Enter pub name...")
    postal_code_options = ['All'] + sorted(data['postcode'].dropna().unique().tolist())

    authorities = st.sidebar.multiselect("Filter by Local Authority", options=authority_options)
    postal_code = st.sidebar.selectbox("Filter by Postal Code", options=postal_code_options)

    filtered_data = apply_filters(data, authorities, name_query, postal_code)

    if page == "Home":
        st.title("Explore Pubs across London")
        st.image("london.jpg", width=700)  
        st.markdown("""
        ### Welcome to the London Pub Explorer!
        Discover and explore pubs across various regions of London. Filter by location, name, or postal code and find your next destination!
        """)
        create_pydeck_map(filtered_data)
        display_bar_chart(filtered_data)
        display_top_cities(data) 
        display_sorted_pubs(filtered_data)
        
    elif page == "Saved Pubs":
        st.title("Your Saved Pubs")
        if 'saved_pubs' not in st.session_state:
            st.session_state.saved_pubs = []
        pub_name = st.selectbox("Select a Pub to Save", ['None'] + filtered_data['name'].tolist())
        if st.button("Save Pub") and pub_name != 'None':
            st.session_state.saved_pubs.append(pub_name)
            st.success(f"Saved: {pub_name}")
        if st.session_state.saved_pubs:
            st.subheader("Saved Pubs")
            for pub in st.session_state.saved_pubs:
                st.write(pub)


main()





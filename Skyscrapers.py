'''
Name: Andrew Plympton
CS230: Section 6
Data: Skyscrapers
Website URL: https://andrewplymptonpythonfinal.streamlit.app/

Description: This data shows a map, scatterplot, sliderbar, and barcharts which explain the data in an interactive and easily digestible way.
This data shows a map, scatterplot, sliderbar, and barcharts which explain the data in an interactive and easily digestible way.
I used packages like pydeck, matplotlib, numpy, pandas, and streamlit to assist with making the data more easily digestible.
The part I thought was the most difficult was the map where I layered the data and created points which could be hovered over.
'''

import numpy as np
import pandas as pd
import streamlit as st
import pydeck as pdk
import matplotlib.pyplot as plt

def getData():

    #Read in file
    dat = pd.read_csv('skyscrapers.csv')

    #Create Data Headers
    dat.rename(columns={'material': 'Material',
                        'name': 'Name',
                        'location.city': 'City',
                        'location.latitude': "Latitude",
                        'location.longitude': 'Longitude',
                        'statistics.floors above': "Floors",
                        'statistics.height': 'Height',
                        'statistics.rank': 'Height Rank'},
                        inplace=True)

    #Replacing zeroes with NA values
    dat.replace(0, np.nan, inplace = True) # [DA1] Uses numpy function to convert zeroes to nan

    dat.dropna(inplace = True)

    return dat

def selectCity(dat, column_name = 'City'): #[PY1] Column name = city makes function default to city if not specified

    selectionList = sorted(set(dat[column_name]))  # [DA2] Ensure each city only appears once (Sorted alphabetically)

    selectInput = st.selectbox(f'Select {column_name}:', selectionList)  # [ST1] Uses streamlit widget to create a dropdown box

    return selectInput

def scraperByCityMap(dat, inputNames):

    #[DA7] Selected group columns
    selectedCity = dat.loc[dat['City'] == inputNames] #[DA4] Filtered data by City

    mapCenterLat = selectedCity['Latitude'].mean()
    mapCenterLon = selectedCity['Longitude'].mean()

    # Round building height to 2 decimals
    selectedCity['Height'] = selectedCity['Height'].round(2)


    #Create points on map for each skyscraper
    scraperDots = pdk.Layer( #Pydeck visualization tool to layer map visual
        "ScatterplotLayer",
        data = selectedCity,
        get_position = '[Longitude, Latitude]',
        get_radius = 150,
        get_color = [255,0,0],
        pickable = True)

    #Create display when hovering over dot (Pydeck)

    tool_tip = { #Tooltip config for Pydeck Layer (Note: Need to be in HTML/CSS formatting for formatted text and style)
        'html': 'Name: <b>{Name}</b></br>' # first key in the dictionary is displaying the content in html format
        'City: <b>{City}</b></br>'
        'Building Height: <b>{Height}m</b></br>'
        '# of Floors: <b>{Floors}</b></br>',

        # format tool tip using CSS to have the background color of the tool tip be steelblue and the font color be white
        "style": {'backgroundColor': 'steelblue', 'color': 'white'}
    }

    # [MAP] Create the map and add the hover box on each skyscraperDot
    skyscraperMap = pdk.Deck( #Using pydeck visualization to create map

        map_style= 'light', #[ST4]

        initial_view_state = pdk.ViewState(latitude=mapCenterLat, longitude=mapCenterLon, zoom=12),

        layers = [scraperDots],

        tooltip = tool_tip
    )
    st.pydeck_chart(skyscraperMap, use_container_width=True) #[ST2]


def skyscrapersPerCity(dat, max_cities=10):

    # Get list of cities from the data (No duplicates)
    cities = sorted(dat['City'].unique())

    # [ST1] Streamlit widget to select a city
    selected_city = st.selectbox('Select a City:', cities)

    # Filter the data based on the selected city
    filtered_data = dat[dat['City'] == selected_city]

    # Limit the number of skyscrapers to display (stop when reach max)
    if len(filtered_data) > max_cities:
        filtered_data = filtered_data.head(max_cities)
        st.write("Some skyscrapers were removed for visualization purposes.")

    # Plotting the bar chart (Matplotlib code examples formatting)
    plt.figure(figsize=(10, 6))
    plt.bar(filtered_data['Name'], filtered_data['Height'], color='steelblue') #x-data, y-data, color
    plt.xlabel('Skyscraper Name')
    plt.ylabel('Height (m)')
    plt.title(f'Skyscraper Heights in {selected_city}')
    plt.xticks(rotation=90)  # Rotate x-axis labels for better visibility

    st.pyplot(plt)

def scatterPlotSkyscrapers(dat):
    try:
        # [ST3] Multiselect to choose multiple cities
        selected_cities = st.multiselect(
            'Select Cities to Compare:',
            options=sorted(dat['City'].unique()),
            default=sorted(dat['City'].unique())[:3]  # Preselect first 3 cities
        )

        # Filter data based on selected cities ([DA4]: Filter data by condition)
        filtered_data = dat[dat['City'].isin(selected_cities)]

        # Handle empty selection case
        if filtered_data.empty:
            st.warning("No skyscrapers available for the selected cities.")
            return

        # [DA3] Find the top 5 tallest skyscrapers in the selection
        top_skyscrapers = filtered_data.nlargest(5, 'Height').copy()

        # Add the Height-to-Floor Ratio column for the table only
        top_skyscrapers['Height-to-Floor Ratio'] = top_skyscrapers['Height'] / top_skyscrapers['Floors']

        plt.figure(figsize=(10, 6)) #width, height

        # Generate unique colors for each city
        unique_cities = filtered_data['City'].unique()
        colors = plt.cm.tab10(range(len(unique_cities)))

        # Plot each city's data in a separate layer
        for i, city in enumerate(unique_cities): #pairs the city and i as unique pairs of data so that they are assigned unique colors
            city_data = filtered_data[filtered_data['City'] == city] #Only include data from city selected
            plt.scatter(
                city_data['Floors'], #X-axis
                city_data['Height'], #Y-axis
                color=colors[i], #Each instance of i is assigned a unique color
                s=50, #Size
                alpha=0.8, #Transparency
                edgecolors='k', #read that this draws an outline around dot and helps with visibility
                label=city  # City name for legend
            )

        # Add legend, labels, and title
        plt.legend(title='City')
        plt.xlabel('Number of Floors')
        plt.ylabel('Height (m)')
        plt.title('Skyscraper Heights vs. Floors')
        plt.grid(True)

        # Display the plot
        st.pyplot(plt)

        # Display the top skyscrapers as a table ([VIZ1]: Table visualization)
        st.subheader("Top 5 Tallest Skyscrapers")
        st.write(top_skyscrapers[['Name', 'City', 'Height', 'Floors', 'Height-to-Floor Ratio']])

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")  # [PY3] Handle potential errors

def getMaterialData(dataframe):
    # Replace "concrete/steel" with "steel/concrete" for consistency
    dataframe['Material'] = dataframe['Material'].replace({"concrete/steel": "steel/concrete"})

    # List comprehension -> Sort and iterate through each row and takes the index
    materials = sorted([row['Material'] for i, row in dataframe.iterrows()])
    return dataframe, materials

def skyscraperMaterialAnalysis(dat):
    # [DA6] Create a pivot table to analyze average skyscraper height by material
    material_pivot = dat.pivot_table(index='Material', values='Height', aggfunc='mean').reset_index()  # Group by, calculate values for, find the average

    # [PY2] Get material data
    pivot_data, material_list = getMaterialData(material_pivot)  # Calling previous function to get the material data

    plt.figure(figsize=(10, 6))  # Width, Height
    plt.bar(pivot_data['Material'], pivot_data['Height'], color='steelblue')
    plt.xlabel('Material')
    plt.ylabel('Average Height (m)')
    plt.title('Average Skyscraper Height by Material')
    plt.xticks(rotation=45)

    # [VIZ3] Display the plot
    st.pyplot(plt)

    # [VIZ1] Display the pivot data in a table
    st.subheader("Material Analysis Table")
    st.write(pivot_data)

def countHeightSlider(dat):

    #Get the max and min heights
    minHeight = dat['Height'].min()
    maxHeight = dat['Height'].max()

    #[ST4]
    userHeight = st.slider('Note: The height selected determines the # of taller skyscrapers:',
                           min_value = int(minHeight),
                           max_value = int(maxHeight),
                           value = int(minHeight),
                           step = 1)

    #filter depending on userheight
    filtered_data = dat[dat['Height'] >= userHeight]

    #Print Statement
    st.write(f"There are {len(filtered_data)} skyscrapers which are at least {userHeight} meters tall.")

    if not filtered_data.empty:

        if not filtered_data.empty:
            important_columns = ['Name', 'City', 'Height', 'Floors', 'Material']
            st.dataframe(filtered_data[important_columns])



def main():
    st.title("Skyscrapers in the United States")

    dat = getData()

    st.sidebar.title("All About Skyscrapers")
    menu = st.sidebar.radio("Select a section:",
                            ["Overview Map",
                            "Skyscrapers Per City",
                            "Scatter Plot: Skyscrapers",
                            "Material Analysis",
                             "Height Slider: Skyscrapers"])

    if menu == "Overview Map":
        inputCity = selectCity(dat, 'City')
        st.header(f':blue[Map of Skyscrapers in {inputCity}]', divider='blue')
        scraperByCityMap(dat, inputCity)

    elif menu == "Skyscrapers Per City":
        st.header(f":blue[Analysis of Skyscrapers Per City]", divider='blue')
        skyscrapersPerCity(dat)

    elif menu == "Scatter Plot: Skyscrapers":
        st.header(f':blue[Comparing Height:Floor Ratio By City:]', divider='blue')
        scatterPlotSkyscrapers(dat)

    elif menu == "Material Analysis":
        st.header(f':blue[Average Skyscraper Height by Material]', divider='blue')
        skyscraperMaterialAnalysis(dat)

    elif menu == "Height Slider: Skyscrapers":
        st.header(f':blue[Count Skyscrapers by Height]', divider='blue')
        countHeightSlider(dat)

if __name__ == '__main__':
    main()
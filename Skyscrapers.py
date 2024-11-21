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

def selectCity(dat, column_name = 'City'): #[PY1]

    selectionList = sorted(set(dat[column_name]))  # [DA2]

    selectInput = st.selectbox(f'Select {column_name}:', selectionList)  # [ST1]

    return selectInput

def scraperByCityMap(dat, inputNames):

    #[DA7] Selected group columns
    selectedCity = dat.loc[dat['City'] == inputNames] #[DA4] Filtered data by City

    mapCenterLat = selectedCity['Latitude'].mean()
    mapCenterLon = selectedCity['Longitude'].mean()

    # Round building height to 3 decimals
    selectedCity['Height'] = selectedCity['Height'].round(2)


    #Create points on map for each skyscraper
    scraperDots = pdk.Layer(
        "ScatterplotLayer",
        data = selectedCity,
        get_position = '[Longitude, Latitude]',
        get_radius = 150,
        get_color = [255,0,0],
        pickable = True)

    #Create display when hovering over dot (Pydeck)

    tool_tip = {
        'html': 'Name: <b>{Name}</b></br>'
        'City: <b>{City}</b></br>'
        'Building Height: <b>{Height}m</b></br>'
        '# of Floors: <b>{Floors}</b></br>',

        # format tool tip using CSS to have the background color of the tool tip be steelblue and the font color be white
        "style": {'backgroundColor': 'steelblue', 'color': 'white'}
    }

    # [MAP] Create the map and add the hover box on each skyscraperDot
    skyscraperMap = pdk.Deck(

        map_style= 'light', #[ST4]

        initial_view_state = pdk.ViewState(latitude=mapCenterLat, longitude=mapCenterLon, zoom=12),

        layers = [scraperDots],

        tooltip = tool_tip
    )
    st.pydeck_chart(skyscraperMap, use_container_width=True) #[ST2]


def skyscrapersPerCity(dat, max_cities=10):

    # Get the unique list of cities from the data
    cities = sorted(dat['City'].unique())

    # [ST1] Streamlit widget to select a city
    selected_city = st.selectbox('Select a City:', cities)

    # Filter the data based on the selected city
    filtered_data = dat[dat['City'] == selected_city]

    # Limit the number of skyscrapers to display (cut off after `max_cities`)
    if len(filtered_data) > max_cities:
        filtered_data = filtered_data.head(max_cities)
        st.write("Some skyscrapers were removed for visualization purposes.")

    # Display the skyscrapers and their heights in a bar plot
    st.header(f'Bar Chart of Skyscrapers in {selected_city}')

    # Plotting the bar chart (Matplotlib code examples formatting)
    plt.figure(figsize=(10, 6))
    plt.bar(filtered_data['Name'], filtered_data['Height'], color='steelblue')
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

        # Scatter plot: Height vs. Floors
        st.header("Scatter Plot: Height vs. Floors")

        plt.figure(figsize=(10, 6))

        # Generate unique colors for each city
        unique_cities = filtered_data['City'].unique()
        colors = plt.cm.tab10(range(len(unique_cities)))

        # Plot each city's data in a separate layer
        for i, city in enumerate(unique_cities):
            city_data = filtered_data[filtered_data['City'] == city]
            plt.scatter(
                city_data['Floors'],
                city_data['Height'],
                color=colors[i],
                s=50,
                alpha=0.8,
                edgecolors='k',
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

def skyscraperMaterialAnalysis(dat):
    # [DA6] Create a pivot table to analyze average skyscraper height by material
    material_pivot = dat.pivot_table(index='Material', values='Height', aggfunc='mean').reset_index()

    # [PY2] Return data and a sorted list of materials
    def getMaterialData(dataframe):
        # Replace "concrete/steel" with "steel/concrete" for consistency
        dataframe['Material'] = dataframe['Material'].replace({"concrete/steel": "steel/concrete"})

        materials = sorted([row['Material'] for _, row in dataframe.iterrows()])  # [PY4] List comprehension
        return dataframe, materials

    pivot_data, material_list = getMaterialData(material_pivot)

    # Handle empty data case
    if pivot_data.empty:
        st.warning("No skyscraper data available for the selected criteria.")

    # [VIZ3] Bar chart for average heights by material
    st.header("Average Skyscraper Height by Material")

    plt.figure(figsize=(10, 6))
    plt.bar(pivot_data['Material'], pivot_data['Height'], color='teal')
    plt.xlabel('Material')
    plt.ylabel('Average Height (m)')
    plt.title('Average Skyscraper Height by Material')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Display the plot
    st.pyplot(plt)

    # Display the pivot data in a table ([VIZ1]: Table visualization)
    st.subheader("Material Analysis Table")
    st.write(pivot_data)

def main():
    st.title("Skyscrapers")

    dat = getData()

    inputCity = selectCity(dat, 'City')
    st.header(f':blue[Map of Skyscrapers in {inputCity}]', divider='blue')
    scraperByCityMap(dat, inputCity)

    st.write('')
    st.write('')
    st.write('')
    st.write('')
    st.write('')


    skyscrapersPerCity(dat)

    st.write('')
    st.write('')
    st.write('')
    st.write('')
    st.write('')

    scatterPlotSkyscrapers(dat)

    st.write('')
    st.write('')
    st.write('')
    st.write('')
    st.write('')

    skyscraperMaterialAnalysis(dat)

if __name__ == '__main__':
    main()
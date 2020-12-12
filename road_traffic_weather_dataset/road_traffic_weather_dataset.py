import geopandas as gpd
import requests
import zipfile
import io
import matplotlib.pyplot as plt

import pandas as pd
import numpy as np
import seaborn as sns

import warnings
warnings.filterwarnings("ignore")

def consolidate():

    """
    Attach traffic information, weather information and county name to each road in Georgia.
    Provide functions to show statistics of the dataset.

    Returns
    -------
    A dataset with 7524 rows and 22 columns, containing the traffic, weather and road characteristics.
    Data columns (total 22 columns):
    Year_Record           7524 non-null int64
    State_Code            7524 non-null int64
    Route_ID              7524 non-null object
    AADT                  7524 non-null float64
    Future_AADT           968 non-null object
    Road_Lat              7524 non-null float64
    Road_Lon              7524 non-null float64
    Begin_Point           7524 non-null float64
    End_Point             7524 non-null float64
    County_Code           7524 non-null float64
    Functional_System     7522 non-null float64
    Facility_Type         7522 non-null float64
    Ownership             7524 non-null float64
    Through_Lanes         7524 non-null float64
    County_Name           7524 non-null object
    Station               7524 non-null object
    Station_Lat           7524 non-null float64
    Station_Lon           7524 non-null float64
    Cooling_Degree_Day    7524 non-null float64
    Days_wDeep_Snow       7524 non-null float64
    Monthly_Snowfall      7524 non-null float64
    Monthly_Temp          7524 non-null float64
    dtypes: float64(16), int64(2), object(4)

    Examples
    --------
    >>> import road_traffic_weather_dataset
    >>> road_traffic_weather_dataset.consolidate()
    Year_Record | State_Code |     Route_ID     |  AADT  | Future_AADT |  Road_Lat | ... Days_wDeep_Snow | Monthly_Snowfall | Monthly_Temp
    -----------------------------------------------------------------------------------------------------------------------------
        2018    |     13     | 1000100000100INC |  14200 |     None    | -85.154834|
    (7524 rows × 22 columns)
    """

    # Download the traffic zipfile
    url = 'http://www.dot.ga.gov/DriveSmart/Data/Documents/Traffic_GeoDatabase.zip'
    local_path = 'tmp/'
    print('Downloading traffic shapefile...')
    r = requests.get(url)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    print("Done")
    z.extractall(path=local_path) # extract to folder
    filenames = [y for y in sorted(z.namelist()) for ending in ['dbf', 'prj', 'shp', 'shx'] if y.endswith(ending)]
    print(filenames)

    # Load the dataset
    dbf, prj, shp, shx = [filename for filename in filenames]
    traffic_geo = gpd.read_file(local_path + shp)

    # Only include roads with aadt_vn and geometry column
    traffic_geo = traffic_geo[traffic_geo.AADT_VN.notnull()]
    traffic_geo = traffic_geo[traffic_geo.geometry.notnull()]

    # Drop columns with no values
    traffic_geo = traffic_geo.dropna(axis=1,how='all')

        # Function to get lat/long
    def getXY(pt):
        return (pt.x, pt.y)
    centroidseries = traffic_geo['geometry'].to_crs({'init': 'epsg:4326'}).centroid
    x,y = [list(t) for t in zip(*map(getXY, centroidseries))]

    # Add lat/lon columns
    traffic_geo['Road_Lat'] = x
    traffic_geo['Road_Lon'] = y
    traffic = pd.DataFrame(traffic_geo)

    # Download the road inventory zipfile
    url = 'http://www.dot.ga.gov/DriveSmart/Data/Documents/Road_Inventory_Excel.zip'
    local_path = 'tmp/'
    print('Downloading road inventory file...')
    r = requests.get(url)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    print("Done")

    # Extract to folder
    z.extractall(path=local_path)
    filenames = [y for y in z.namelist()]
    print(filenames)

    # Load the excel file
    road_xls = pd.read_excel(z.open('Road_Inventory_2019.xlsx'))
    road_xls.to_csv('road.csv', encoding='utf-8', index=False)
    road = pd.read_csv('road.csv')

    # See the percentage of NA in road columns
    for i in road.columns:
        percent_NA = round((road[i].isnull().sum()/len(road.index)),2)
        if percent_NA > 0.3:
            road = road.drop(i, axis=1)

    traffic = traffic.drop_duplicates(subset = ['Route_ID'])
    road = road.drop(['State_Code', 'Year_Record'], axis=1)
    road = road.drop_duplicates(subset = ['Route_ID'])

    # Merge road data and traffic data using Route_ID
    road_traffic = traffic.merge(road, how='inner', left_on=['Route_ID'], right_on=['Route_ID'])
    road_traffic = road_traffic.drop(['geometry'], axis=1)

    # Download county code data
    print('Downloading county code data...')
    county_code = pd.read_csv('https://www2.census.gov/geo/docs/reference/codes/files/national_county.txt', sep=",", header=None)
    print("Done")
    county_code = county_code.rename(columns={0:'fips_state', 1:'state_code', 2:'COUNTY_CODE', 3:'County_Name'})
    ga_code = county_code[county_code['fips_state'] == 'GA']
    ga_code = ga_code.drop(['fips_state', 'state_code', 4], axis=1)

    # Attach county code to the road dataset on COUNTY_CODE column
    road_traffic_code = road_traffic.merge(ga_code, how='inner', left_on=['COUNTY_CODE'], right_on=['COUNTY_CODE'])

    # Load the weather data
    url = 'https://raw.githubusercontent.com/QMSS-G5072-2020/Hengyu_Ai/master/Final_Project/Dataset/weather.csv?token=AMHA3VGM6SOKQXFFOLL6HSK73J6MQ'
    print('Downloading weather data...')
    weather = pd.read_csv(url)
    print("Done")

    # Define a function to find the closest weather station for a road
    road_traffic_code['STATION'] = 1
    def find_closest_weather(road_traffic_code):
        for m in range(len(road_traffic_code)):
            for i in range(len(weather)):
            # Calc distance between point and each weather station
                dist_lst = []
                dist = np.sqrt((road_traffic_code.Road_Lat.iloc[i]-weather.LATITUDE.iloc[i]) ** 2 +
                               (road_traffic_code.Road_Lon.iloc[i]-weather.LONGITUDE.iloc[i]) ** 2)
                dist_lst.append(dist)
            min_idx = dist_lst.index(min(dist_lst))
            road_traffic_code.STATION.iloc[m] = weather.STATION.iloc[min_idx]

    find_closest_weather(road_traffic_code)

    # Merge weather data to road dataset
    all_data = road_traffic_code.merge(weather, how='left', on=['STATION'])

    # Drop columns with no value
    all_data = all_data.dropna(axis=1,how='all')

    # Rename dataset columns
    all_data = all_data.drop(['Begin_Poin', 'End_Point_x', 'URBAN_CODE', 'NAME', 'DATE', 'ELEVATION'], axis=1)
    all_data.rename({'Year_Recor': 'Year_Record', 'AADT_VN': 'AADT', 'FUTURE_AAD': 'Future_AADT',
                 'End_Point_y': 'End_Point','COUNTY_CODE': 'County_Code', 'F_SYSTEM': 'Functional_System',
                 'FACILITY_TYPE': 'Facility_Type', 'OWNERSHIP': 'Ownership', 'THROUGH_LANES': 'Through_Lanes',
                 'LATITUDE': 'Station_Lat', 'LONGITUDE': 'Station_Lon', 'CDSD': 'Cooling_Degree_Day',
                 'DSND': 'Days_wDeep_Snow', 'SNOW': 'Monthly_Snowfall', 'TAVG': 'Monthly_Temp',
                 'county_name': 'County_Name', 'STATION': 'Station'}, axis=1, inplace=True)

    # Recode FACILITY_TYPE and OWNERSHIP variables to categorical
    all_data['Facility_Type'].replace([1,2,3,4,5,6,7],['One-Way','Two-Way','Couplet','Ramp','Non Mainline','Non Inventory Direction', 'Unbuilt'],inplace=True)
    all_data['Ownership'].replace([1,2,4,25],['State Highway','County Highway','City of Municipal ','Other Local Agency'],inplace=True)
    all_data.to_csv('all_data.csv')
    return all_data

# Traffic stats functions
def county_traffic_mean(county_name):
    all_data = pd.read_csv('all_data.csv')
    return int(all_data[all_data.County_Name == county_name].AADT.mean())
def county_traffic_min(county_name):
    all_data = pd.read_csv('all_data.csv')
    return int(all_data[all_data.County_Name == county_name].AADT.min())
def county_traffic_max(county_name):
    all_data = pd.read_csv('all_data.csv')
    return int(all_data[all_data.County_Name == county_name].AADT.max())
def county_traffic_dis(county_name):
    all_data = pd.read_csv('all_data.csv')
    return all_data[all_data.County_Name == county_name].AADT.hist()

# Road stats functions
def county_road_facility_type_hist(county_name):
    all_data = pd.read_csv('all_data.csv')
    return all_data[all_data.County_Name == county_name].Facility_Type.hist()
def county_road_ownership_hist(county_name):
    all_data = pd.read_csv('all_data.csv')
    return all_data[all_data.County_Name == county_name].Ownership.hist()
def county_road_through_la_hist(county_name):
    all_data = pd.read_csv('all_data.csv')
    return all_data[all_data.County_Name == county_name].Through_Lanes.hist()

# Road-AADT correlation functions
def county_facility_type_AADT_catplot(county_name):
    all_data = pd.read_csv('all_data.csv')
    return sns.catplot(x="Facility_Type", y="AADT", kind="box", data=all_data[all_data.County_Name == county_name])
def county_ownership_AADT_catplot(county_name):
    all_data = pd.read_csv('all_data.csv')
    return sns.catplot(x="Ownership", y="AADT", kind="box", data=all_data[all_data.County_Name == county_name])
def county_through_la_AADT_scatter(county_name):
    all_data = pd.read_csv('all_data.csv')
    return sns.scatterplot(data=all_data, x="Through_Lanes", y="AADT")

# Weather-AADT correlation functions
def coolingday_aadt_scatter(county_name):
    all_data = pd.read_csv('all_data.csv')
    return sns.scatterplot(data=all_data, x="Cooling_Degree_Day", y="AADT")
def deepsnow_aadt_scatter(county_name):
    all_data = pd.read_csv('all_data.csv')
    return sns.scatterplot(data=all_data, x="Days_wDeep_Snow", y="AADT")
def snowfall_aadt_scatter(county_name):
    all_data = pd.read_csv('all_data.csv')
    return sns.scatterplot(data=all_data, x="Monthly_Snowfall", y="AADT")
def temp_aadt_scatter(county_name):
    all_data = pd.read_csv('all_data.csv')
    return sns.scatterplot(data=all_data, x="Monthly_Temp", y="AADT")

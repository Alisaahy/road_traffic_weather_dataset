# road-traffic-weather-dataset 

![](https://github.com/Alisaahy/road_traffic_weather_dataset/workflows/build/badge.svg) [![codecov](https://codecov.io/gh/Alisaahy/road_traffic_weather_dataset/branch/main/graph/badge.svg)](https://codecov.io/gh/Alisaahy/road_traffic_weather_dataset) ![Release](https://github.com/Alisaahy/road_traffic_weather_dataset/workflows/Release/badge.svg) [![Documentation Status](https://readthedocs.org/projects/road_traffic_weather_dataset/badge/?version=latest)](https://road_traffic_weather_dataset.readthedocs.io/en/latest/?badge=latest)

Python package that consolidate, organize and clean road data, traffic data and weather data in Georgia.

## Installation

```bash
$ pip install -i https://test.pypi.org/simple/ road_traffic_weather_dataset
```

## Features

- Attach traffic information, weather information and county name to each road in Georgia.
- Provide functions to show statistics of the road, traffic and weather information in each county and the correlation between road, traffic and weather features.

## Dependencies

- python = "^3.8"
- pandas = "^1.1.5"
- geopandas = "^0.8.1"
- requests = "^2.25.0"
- matplotlib = "^3.3.3"
- numpy = "^1.19.4"
- seaborn = "^0.11.0"
- xlrd = "^1.2.0"

## Dataset generation
```bash
from road_traffic_weather_dataset import consolidate
dataset = consolidate()
```
Returns a dataset with 7524 rows and 22 columns, containing the traffic, weather and road characteristics. Data columns include (total 22 columns):
```bash
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
```

## Function list
### Traffic statistics functions
- county_traffic_mean(county_name)
- county_traffic_min(county_name)
- county_traffic_max(county_name)
- county_traffic_dis(county_name)
### Road statistics functions
- county_road_facility_type_hist(county_name)
- county_road_ownership_hist(county_name)
- county_road_through_la_hist(county_name)
### Road-AADT correlation functions
- county_facility_type_AADT_catplot(county_name)
- county_ownership_AADT_catplot(county_name)
- county_through_la_AADT_scatter(county_name)
### Weather-AADT correlation functions
- coolingday_aadt_scatter(county_name)
- deepsnow_aadt_scatter(county_name)
- snowfall_aadt_scatter(county_name)
- temp_aadt_scatter(county_name)
### Example
```
dataset.county_traffic_mean('Appling County')
dataset.county_traffic_dis('Appling County')
dataset.county_road_facility_type_hist('Appling County')
dataset.county_through_la_AADT_scatter('Appling County')
```

## Documentation

The official documentation is hosted on Read the Docs: https://road_traffic_weather_dataset.readthedocs.io/en/latest/

## Contributors

We welcome and recognize all contributions. You can see a list of current contributors in the [contributors tab](https://github.com/Alisaahy/road_traffic_weather_dataset/graphs/contributors).

### Credits

This package was created with Cookiecutter and the UBC-MDS/cookiecutter-ubc-mds project template, modified from the [pyOpenSci/cookiecutter-pyopensci](https://github.com/pyOpenSci/cookiecutter-pyopensci) project template and the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage).
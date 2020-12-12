from road_traffic_weather_dataset import __version__
from road_traffic_weather_dataset import road_traffic_weather_dataset

import pandas as pd
import numpy as np

def test_version():
    assert __version__ == '0.1.0'

def test_all_data_size():
    expected = (7524, 22)
    actual = road_traffic_weather_dataset.consolidate().shape
    assert actual == expected

def test_county_traffic_mean():
    text_example = 'Appling County'
    expected = 1602
    actual = road_traffic_weather_dataset.county_traffic_mean(text_example)
    assert actual == expected

def test_county_traffic_max():
    text_example = 'Appling County'
    expected = 3496
    actual = road_traffic_weather_dataset.county_traffic_max(text_example)
    assert actual == expected

def test_county_traffic_min():
    text_example = 'Appling County'
    expected = 130
    actual = road_traffic_weather_dataset.county_traffic_min(text_example)
    assert actual == expected

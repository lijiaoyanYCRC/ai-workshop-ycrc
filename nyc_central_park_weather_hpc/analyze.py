#!/usr/bin/env python3
"""Starter program: intentionally broken. Repair minimally for Exercise 1.

NOTE: Even after repair, this calculates ANNUAL means, not SUMMER means.
"""
import os
from pathlib import Path
import pandas as pd

HERE=Path(__file__).resolve().parent
input_name=os.environ.get('WEATHER_DATA','data/practice_synthetic_daily.csv')
source=HERE/input_name
weather=pd.read_csv(source,parse_dates=['DATE'])
weather['year']=weather['DATE'].dt.year
weather['daily_mean_c']=(weather['TMAX']+weather['TMIN'])/2
# BUG: the DataFrame does not contain this column name.
summary=weather.groupby('year')['temperature_c'].mean()
output=HERE/'results'/'preliminary_annual_means.csv'
output.parent.mkdir(exist_ok=True)
summary.to_csv(output,header=['mean_temperature_c'])
print(f'Wrote {output}')

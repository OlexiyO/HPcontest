# coding: utf-8
import numpy as np
import os
import pandas as pd
from flight_quest.util import RMSE2, LoadForDay


def DefaultAdjust():
  df = LoadForDay('2012-11-13')
  adjust = (-2 * df.flight_delta)[(df.flight_delta > -10) & (df.flight_delta < 50)]
  df['adjust'] = adjust
  df['adjust'] = df.adjust.fillna(20)[(df.flight_delta > -50) & (df.flight_delta < 50)]
  df['adjust'] = df.adjust.fillna(0)
  RMSE2(df.actual_gate_arrival, df.actual_runway_departure + df.actual_flight_time + df.scheduled_taxi_arrival)
  RMSE2(df.actual_gate_arrival, df.actual_runway_departure + df.actual_flight_time + df.scheduled_taxi_arrival + df.adjust)


def AddAirportAgg(df):
  """Adds aggregated airport features to ."""
  by_arr_airport = df.groupby('arrival_airport_code')
  flight_delay_by_arrival_airport = by_arr_airport.flight_delta.agg(np.mean)
  flight_delay_by_arrival_airport.name = 'flight_delay_by_arrival_airport'
  taxi_delay_by_arrival_airport = by_arr_airport.taxi_arrival_delta.agg(np.mean)
  taxi_delay_by_arrival_airport.name = 'taxi_delay_by_arrival_airport'
  airport_df = pd.DataFrame({'taxi_delay_by_arrival_airport': taxi_delay_by_arrival_airport,
                             'flight_delay_by_arrival_airport': flight_delay_by_arrival_airport})
  return df.join(airport_df, on='arrival_airport_code'), airport_df


def DelaysInAnAirportBetweenDays(df_one, df_two):
  # Take two data frames grouped by airport (second part of AddAirportAgg).
  # Merge them
  df_one_1 = pd.DataFrame({'one': df_one.taxi_delay_by_arrival_airport},
                          index=df_one.index)
  df_two_1 = pd.DataFrame({'two': df_two.taxi_delay_by_arrival_airport},
                          index=df_two.index)
  return df_one_1.join(df_two_1)


def ByAirport(date_str):
  df = LoadForDay(date_str)
  return AddAirportAgg(df)



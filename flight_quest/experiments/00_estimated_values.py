# This file recreates benchmark using last published estimations.

import os
import pandas as pd
from flight_quest import util
from flight_quest.io import local_constants
from flight_quest.util import OR, AND


def CreateOutputForDay(date_str, parent_dir, output_file, header=True):
  """Load data from input, process them and save to a file.

  Args:
    date_str: Usual date string, like "2012-11-25"
    parent_dir: Initial training set directory or leaderboard directory or similar.
    output_file: Either a filename or an open buffer.
    header: If True, will write header at the top of the file.
  """
  input_df = util.LoadForDay(date_str, parent_dir=parent_dir)
  input_df['full_runway_estimate'] = OR(input_df.estimated_runway_arrival, input_df.scheduled_runway_arrival)
  input_df['full_gate_estimate'] = OR(input_df.estimated_gate_arrival, input_df.scheduled_gate_arrival)
  test_file = os.path.join(util.DirForDate(date_str, parent_dir=local_constants.LEADERBOARD_DATA_DIR),
                           'test_flights.csv')
  test_flights = pd.read_csv(test_file)[['flight_history_id']]
  limited_df = input_df[['flight_history_id', 'full_gate_estimate', 'full_runway_estimate']]
  output_df = limited_df.merge(test_flights, on='flight_history_id')
  output_df['actual_runway_arrival'] = OR(output_df.full_runway_estimate, output_df.full_gate_estimate)
  output_df['actual_gate_arrival'] = OR(output_df.full_gate_estimate, output_df.full_runway_estimate)
  cols_to_print = ['flight_history_id', 'actual_runway_arrival', 'actual_gate_arrival']
  output_df.to_csv(output_file, cols=cols_to_print, index=False)
import pandas as pd


def calculate_distance_matrix(df)->pd.DataFrame():
    """
    Calculate a distance matrix based on the dataframe, df.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Distance matrix
    """
    # Write your logic here
    unique_ids = sorted(df['ID'].unique())
    num_ids = len(unique_ids)
    distance_matrix = pd.DataFrame(index=unique_ids, columns=unique_ids)

    
    distance_matrix = distance_matrix.fillna(0)

    
    for i in range(num_ids):
        for j in range(i+1, num_ids):
            id1, id2 = unique_ids[i], unique_ids[j]
            
            
            route1 = df[(df['Start_ID'] == id1) & (df['End_ID'] == id2)]
            route2 = df[(df['Start_ID'] == id2) & (df['End_ID'] == id1)]

            
            cumulative_distance = route1['Distance'].sum() + route2['Distance'].sum()

          
            distance_matrix.at[id1, id2] = cumulative_distance
            distance_matrix.at[id2, id1] = cumulative_distance

    return distance_matrix

def unroll_distance_matrix(df)->pd.DataFrame():
    """
    Unroll a distance matrix to a DataFrame in the style of the initial dataset.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Unrolled DataFrame containing columns 'id_start', 'id_end', and 'distance'.
    """
    # Write your logic here
    indices = distance_matrix.stack().index
    values = distance_matrix.stack().values

    unrolled_df = pd.DataFrame(indices.tolist(), columns=['id_start', 'id_end'])
    unrolled_df['distance'] = values

    
    unrolled_df = unrolled_df[unrolled_df['id_start'] != unrolled_df['id_end']]

    return unrolled_df


def find_ids_within_ten_percentage_threshold(df, reference_id)->pd.DataFrame():
    """
    Find all IDs whose average distance lies within 10% of the average distance of the reference ID.

    Args:
        df (pandas.DataFrame)
        reference_id (int)

    Returns:
        pandas.DataFrame: DataFrame with IDs whose average distance is within the specified percentage threshold
                          of the reference ID's average distance.
    """
    # Write your logic here
    reference_rows = unrolled_df[unrolled_df['id_start'] == reference_value]

    
    avg_distance = reference_rows['distance'].mean()

    
    lower_bound = avg_distance - 0.1 * avg_distance
    upper_bound = avg_distance + 0.1 * avg_distance

    
    result_ids = unrolled_df[(unrolled_df['distance'] >= lower_bound) & (unrolled_df['distance'] <= upper_bound)]['id_start'].unique()


    result_ids = sorted(result_ids)

    return result_ids


    


def calculate_toll_rate(df)->pd.DataFrame():
    """
    Calculate toll rates for each vehicle type based on the unrolled DataFrame.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame
    """
    # Wrie your logic here
    rate_coefficients = {'moto': 0.8, 'car': 1.2, 'rv': 1.5, 'bus': 2.2, 'truck': 3.6}

    
    for vehicle_type, rate_coefficient in rate_coefficients.items():
        unrolled_df[vehicle_type] = unrolled_df['distance'] * rate_coefficient

    return unrolled_df
  
def calculate_time_based_toll_rates(df)->pd.DataFrame():
    """
    Calculate time-based toll rates for different time intervals within a day.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame
    """
    # Write your logic here
     weekday_time_ranges = [(time(0, 0, 0), time(10, 0, 0)), (time(10, 0, 0), time(18, 0, 0)), (time(18, 0, 0), time(23, 59, 59))]
    weekend_time_ranges = [(time(0, 0, 0), time(23, 59, 59))]
    weekday_discount_factors = [0.8, 1.2, 0.8]
    weekend_discount_factor = 0.7

  
    result_df = pd.DataFrame(columns=unrolled_df.columns)

    
    for idx, row in unrolled_df.iterrows():
        id_start, id_end, distance, moto, car, rv, bus, truck = row[['id_start', 'id_end', 'distance', 'moto', 'car', 'rv', 'bus', 'truck']]

  
        for day_num in range(7):
            start_day = (datetime.strptime('Monday', '%A') + timedelta(days=day_num)).strftime('%A')
            end_day = (datetime.strptime('Monday', '%A') + timedelta(days=(day_num + 1) % 7)).strftime('%A')

          
            for time_range, discount_factor in zip(weekday_time_ranges if day_num < 5 else weekend_time_ranges,
                                                   weekday_discount_factors if day_num < 5 else [weekend_discount_factor]):
                start_time, end_time = time_range

                
                result_df = result_df.append({
                    'id_start': id_start,
                    'id_end': id_end,
                    'start_day': start_day,
                    'start_time': datetime.combine(datetime.min, start_time),
                    'end_day': end_day,
                    'end_time': datetime.combine(datetime.min, end_time),
                    'distance': distance,
                    'moto': moto * discount_factor,
                    'car': car * discount_factor,
                    'rv': rv * discount_factor,
                    'bus': bus * discount_factor,
                    'truck': truck * discount_factor
                }, ignore_index=True)

    return result_df
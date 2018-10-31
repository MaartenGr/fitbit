import pandas as pd
import numpy as np
import matplotlib as plt
import glob
import json
import seaborn as sns
from copy import deepcopy

# Helper Functions
def read_files(path):
    """ Used to combine all files in a folder
        It should be note that they have to be the same structure for this to work
    """
    all_paths = glob.glob(path + "*.csv")
    
    combine_df = pd.DataFrame()
    list_of_df = []
    
    for path in all_paths:
        df = pd.read_csv(path, index_col = None, header = 0)
        list_of_df.append(df)
        
    combine_df = pd.concat(list_of_df)
    combine_df = combine_df.drop('Unnamed: 0', 1)
    combine_df['time'] = pd.DatetimeIndex(combine_df['time'])
    
    return combine_df

def read_sleep():
    """ Since the files for sleep were saved as json, some searching for the right information was neccesary
        Combining the files was in exactly the same way as combine_files()
    """
    # Getting all paths in the map
    all_paths = glob.glob('../Files/Sleep/' + "*.txt")
    
    combine_df = pd.DataFrame()
    list_of_df = []
    
    # For each file, create a new dataframe and append it to the list of dataframes, then comcatenate all those dataframes
    for path in all_paths:
        with open(path) as outfile:
            sleep = outfile.readlines()
            
        sleep = json.loads(sleep[0])['sleep'][0]
           
        # Sleep efficiency is defined as the percent of time you were actually sleeping compared to how long you were in bed    
        df = pd.DataFrame({'time': sleep['dateOfSleep'], 
                          'minutesAsleep': sleep['minutesAsleep'], 
                          'minutesAwake': sleep['minutesAwake'], 
                          'timeInBed': sleep['timeInBed'], 
                          'startTime': sleep['startTime'], 
                          'endTime': sleep['endTime'],
                          'efficiency': sleep['efficiency']}, index=[0])

        list_of_df.append(df)
        
    combine_df = pd.concat(list_of_df)
    
    # Transforming time to DatetimeIndex
    combine_df['endTime'] = pd.DatetimeIndex(combine_df['endTime'])
    combine_df['startTime'] = pd.DatetimeIndex(combine_df['startTime'])
    combine_df['time'] = pd.DatetimeIndex(combine_df['time'])
    
    # Now, it will show the date of when you wake up, I want the date of when you go to bed, thus decrease day by 1
    combine_df['time'] = pd.DatetimeIndex(combine_df['time']) - pd.DateOffset(1)

    return combine_df

def read_and_combine_summaries(*types_data):
    """ Reads in the data for all summaries and combines them in a single dataframe
    """
    combine_df = pd.DataFrame()
    list_of_df = []
    
    for type_data in types_data:
        with open('../Files/Summaries/{}.txt'.format(type_data)) as output:
            file = output.readlines()   
        file = json.loads(file[0])
        file = pd.DataFrame(file['activities-{}'.format(type_data)])
        file.rename(columns={'value': type_data}, inplace=True)
        file.set_index('dateTime', inplace = True)
        list_of_df.append(file)
        
    combine_df = pd.concat(list_of_df, axis = 1)
    
    return combine_df

def resolve_duplicate_index(*df):
    """ Resetting the index is necessary because of: "cannot reindex from a duplicate axis"
    """
    for dataframe in df:
        dataframe.reset_index(inplace = True)
        dataframe = dataframe.drop('index', axis = 1, inplace = True)
    return 

def set_index_df(*df, field):
    """ Set the index for each dataframe provided
    """
    for dataframe in df:
        dataframe.set_index(field, inplace = True)
    return

def print_columns(df, name):
    """ Prints the colums of a certain dataframe in a clear and concise way
    """
    print('For the data "{}", we have {} datapoints and the following features:'.format(name, len(df)))
    for column in df.columns:
        print('- {}'.format(column))
    print()
    
def count_missing_data(df):
    """ Counts the missing values for each features
        and display the Total and the Percentage
    """
    # Calculates the total number of missing values for each feature
    total = df.isnull().sum().sort_values(ascending=False)
    
    # Calculates the percentage of missing values for each features
    percent = (df.isnull().sum()/df.isnull().count()).sort_values(ascending=False)
    
    # Combines the percentage and totals
    missing_data = pd.concat([total, percent], axis=1, keys=['Total', 'Percent'])
    
    # Only returns data that have missing values
    return missing_data[missing_data['Percent']>0]
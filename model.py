"""

    Helper functions for the pretrained model to be used within our API.

    Author: Explore Data Science Academy.

    Note:
    ---------------------------------------------------------------------
    Please follow the instructions provided within the README.md file
    located within this directory for guidance on how to use this script
    correctly.

    Importantly, you will need to modify this file by adding
    your own data preprocessing steps within the `_preprocess_data()`
    function.
    ----------------------------------------------------------------------

    Description: This file contains several functions used to abstract aspects
    of model interaction within the API. This includes loading a model from
    file, data preprocessing, and model prediction.  

"""

# Helper Dependencies
import numpy as np
import pandas as pd
import pickle
import json

def _preprocess_data(data):
    """Private helper function to preprocess data for model prediction.

    NB: If you have utilised feature engineering/selection in order to create
    your final model you will need to define the code here.


    Parameters
    ----------
    data : str
        The data payload received within POST requests sent to our API.

    Returns
    -------
    Pandas DataFrame : <class 'pandas.core.frame.DataFrame'>
        The preprocessed data, ready to be used our model for prediction.
    """
    # Convert the json string to a python dictionary object
    feature_vector_dict = json.loads(data)
    # Load the dictionary as a Pandas DataFrame.
    feature_vector_df = pd.DataFrame.from_dict([feature_vector_dict])

    # ---------------------------------------------------------------
    # NOTE: You will need to swap the lines below for your own data
    # preprocessing methods.
    #
    # The code below is for demonstration purposes only. You will not
    # receive marks for submitting this code in an unchanged state.
    # ---------------------------------------------------------------

    # ----------- Replace this code with your own preprocessing steps --------
    predict_vector = feature_vector_df[['Madrid_wind_speed','Bilbao_rain_1h','Valencia_wind_speed']]

    #Drop the Unnamed:0 column
    predict_vector = feature_vector_df.drop(['Unnamed: 0'], axis=1)

    #Replace null values in Valencia_pressure with Madrid_pressure
    predict_vector.loc[predict_vector['Valencia_pressure'].isna(),'Valencia_pressure'] = \
    predict_vector.loc[predict_vector['Valencia_pressure'].isna(), 'Madrid_pressure']

    #Convert time to numpy datetime object
    predict_vector['time'] = pd.to_datetime(predict_vector['time'], format='%Y-%m-%d %H:%M:%S')

    #Split time column to hour, day, month & year
    predict_vector['year'] = pd.DatetimeIndex(predict_vector['time']).year
    predict_vector['month'] = pd.DatetimeIndex(predict_vector['time']).month
    predict_vector['day'] = pd.DatetimeIndex(predict_vector['time']).day
    predict_vector['hour'] = pd.DatetimeIndex(predict_vector['time']).hour

    #Drop the time column
    predict_vector = predict_vector.drop(columns= 'time')

    # Re-organize the column features to have date features at the start
    col_titles = ['year'] + ['month'] + ['day'] + ['hour'] + \
        [col for col in predict_vector.columns \
        if col not in ['year', 'month', 'day', 'hour','load_shortfall_3h']] + \
            ['load_shortfall_3h']

    #Create dummy variables (winter, summer, autumn, spring) based on
    # weather seasons using the month column
    train_copy_df.loc[train_copy_df['month'].isin([1,2,3]),['winter','spring','summer','autumn']] = [1,0,0,0]
    train_copy_df.loc[train_copy_df['month'].isin([4,5,6]),['winter','spring','summer','autumn']] = [0,1,0,0]
    train_copy_df.loc[train_copy_df['month'].isin([7,8,9]),['winter','spring','summer','autumn']] = [0,0,1,0]
    train_copy_df.loc[train_copy_df['month'].isin([10,11,12]),['winter','spring','summer','autumn']] = [0,0,0,1]

    #change variable of season features from float to int
    train_copy_df = train_copy_df.astype(
        {
            'winter': int, 'summer': int, 'spring': int, 'autumn': int
        }
    )

    #Create dummy variables for  Valencia_wind_deg & Seville_pressure
    dummies_df = pd.get_dummies(train_copy_df[['Valencia_wind_deg','Seville_pressure']], drop_first = True)

    train_copy_df = pd.concat([train_copy_df, dummies_df], axis='columns')

    #Drop original Valencia_wind_deg & Seville_pressure
    train_copy_df = train_copy_df.drop(['Valencia_wind_deg', 'Seville_pressure' ], axis='columns')

    # Re-organize the columns to have load_shortfall_3h at the end
    column_titles = [col for col in train_copy_df.columns if col!= 'load_shortfall_3h'] + ['load_shortfall_3h']
    train_copy_df = train_copy_df.reindex(columns = column_titles)


    
    


    
    # ------------------------------------------------------------------------

    return predict_vector

def load_model(path_to_model:str):
    """Adapter function to load our pretrained model into memory.

    Parameters
    ----------
    path_to_model : str
        The relative path to the model weights/schema to load.
        Note that unless another file format is used, this needs to be a
        .pkl file.

    Returns
    -------
    <class: sklearn.estimator>
        The pretrained model loaded into memory.

    """
    return pickle.load(open(path_to_model, 'rb'))


""" You may use this section (above the make_prediction function) of the python script to implement 
    any auxiliary functions required to process your model's artifacts.
"""

def make_prediction(data, model):
    """Prepare request data for model prediction.

    Parameters
    ----------
    data : str
        The data payload received within POST requests sent to our API.
    model : <class: sklearn.estimator>
        An sklearn model object.

    Returns
    -------
    list
        A 1-D python list containing the model prediction.

    """
    # Data preprocessing.
    prep_data = _preprocess_data(data)
    # Perform prediction with model and preprocessed data.
    prediction = model.predict(prep_data)
    # Format as list for output standardisation.
    return prediction[0].tolist()

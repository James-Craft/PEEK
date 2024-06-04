import pandas as pd
import numpy as np
import chardet
from charset_normalizer import detect
import streamlit as st
import io
from settings import add_to_session_state
import re
import os
import numpy as np

@st.cache_data
def calculate_statistics(df):
    # Calculate and return descriptive statistics
    stats_df = df.describe(include="all").transpose()
    shape = df.shape
    return stats_df, shape

@st.cache_data(show_spinner=True)
def uploadedfilesload(uploaded_files):
    dfs = []
    errors = []
    file_names = []
    #load each of the files, determine encoding
    for file in uploaded_files:
        
        #grab filename and add it to files list
        file_name = file.name
        file_names.append(file_name)

        #encoding detection attempt no1
        #read file
        file_contents = file.read()
        #try and use charset_normalizer detect to determine file encoding 
        detected_encoding = detect(file_contents)['encoding']

        #encoding detection attempt no2
        # if we fail, we try and use chardet on error tell us the error plez
        if detected_encoding is None:
            try: 
                detected_encoding = chardet.detect(file_contents)
            except Exception as e:
                errors.append(f"Error reading file {file_name}: {(e)}")
            continue 

        filetype = file_name.split(".")[-1]
        if filetype == "csv":
            try:
                # Attempt to read CSV file with detected encoding
                df = pd.read_csv(io.BytesIO(file_contents), encoding=detected_encoding)
            except pd.errors.ParserError:
                errors.append(f"Error reading file {file_name}: {(e)}")
        elif filetype == "xlsx": # if it's not csv load xlsx
            try:
                df = pd.read_excel(file) # Attempt to read Excel file
            except Exception as e:
                errors.append(f"Error reading file {file_name}: {(e)}")
                continue 
        elif (filetype != "csv" and filetype != "xlsx"):
            st.error("Invalid file format. Please upload an Excel (xlsx) or CSV file.")
            return None
        try:
            dfs.append(df) # lets concat/append the dfs to the dfs list together
        except: # Exception : e 
            errors.append(f"Error processing file {file_name}: {(e)}")
            st.write('❌Sadly we have a problem with your file.. perhaps attempt to convert it via another program and try again.❌')
            st.write(error)

    master_df = None

    #create master df from either dfs if multiple dfs or just use the df
    #more should be done here
    if len(dfs)>1:
        master_df = pd.concat(dfs, ignore_index=True)
    elif len(dfs)==1:
        master_df = df
    elif dfs == None:
        st.write('serious error here')

    #if we've encountered any errors during this entire process tell us on streamlit aswell as in the command line
    if errors:
        print("Errors encountered during data loading:")
        for error in errors:
            st.write(error)
    else:
        st.write("🎉 Data loaded successfully! 🎉")
        add_to_session_state("master_df", master_df)
        add_to_session_state("current_df", master_df)
        add_to_session_state("file_names", file_names)
        add_to_session_state("dfs", dfs)

    return

#@st.cache_data
def detect_data_types(df):
   
    #Detect data types and create dictionaries for dimensions and metrics
    print(type(df))
    dimension_list = [col for col, dtype in df.dtypes.items() if dtype == "object"]
    metric_list = [col for col, dtype in df.dtypes.items() if dtype != "object"]
    col_list = [col for col in df]
    dim_met_dtype_dict = {col: dtype for col, dtype in df.dtypes.items()}
    add_to_session_state("dim_met_dtype_dict", dim_met_dtype_dict)
    add_to_session_state("dimension_list", dimension_list)
    add_to_session_state("metric_list", metric_list)
    add_to_session_state("col_list", col_list)

@st.cache_data
def deduplicate(df):
    # Deduplicate the DataFrame
    deduplicated_df = df.drop_duplicates()
    return deduplicated_df

def drop_columns(df, columns_to_drop):
    # Drop selected columns from the DataFrame
    updated_df = df.drop(columns=columns_to_drop, errors='ignore')
    return updated_df

@st.cache_data
def melt_data(df, melt_by):
     # Melt the DataFrame
    melted_df = pd.melt(df, id_vars=[melt_by])
    return melted_df

@st.cache_data
def group_data(df, group_by_columns):
    # Group the DataFrame by selected columns
    grouped_df = df.groupby(group_by_columns).sum().reset_index()
    return grouped_df

@st.cache_data
def transpose_data(df):
    # transpose the DataFrame by selected columns
    transposed_df = df.transpose()
    return transposed_df

@st.cache_data
def concat_data(df, concat_cols, seperator, concatname):
    for col in concat_cols:
        if col in df.columns:
            df[concatname] = df.apply(lambda row: seperator.join(str(row[col]) for col in concat_cols), axis=1)
    return df

def format_column(df, column, format_type ):

    if format_type == 'String':
        
        try:

            df[column] = df[column].astype(str)
        except ValueError:

            st.error(f"Cannot convert column '{column}' to string.")

    elif format_type == 'Integer':

        try:

            df[column] = df[column].astype(int)

        except ValueError:

            st.error(f"Cannot convert column '{column}' to integer.")

    elif format_type == 'Currency (£)':

        try:

            df[column] = df[column].apply(lambda x: f"£{x:.1f}")

        except ValueError:

            st.error(f"Cannot format column '{column}' as currency.")

    elif format_type == 'Currency ($)':

        try:

            df[column] = df[column].apply(lambda x: f"${x:.1f}")

        except ValueError:

            st.error(f"Cannot format column '{column}' as currency.")

    elif format_type == 'Custom':

        if st.session_state['custom_format']:

            try:

                df[column] = df[column].apply(st.session_state['custom_format'])

            except ValueError:

                st.error(f"Error applying custom format to column '{column}'.")

        else:

            st.error("Please provide a custom format function.")

    return df

def st_form_with_counters():
    # Function to add or remove multiselect boxes for dimensions and metrics
    current_list = []

    def add_or_remove_multiselect(counter, label, options):

        for i in range(counter):
            current_list.append(st.selectbox(f"{label} {i+1}", options=options))

    # Counters
    dimension_counter = st.number_input("Number of Dimensions",
                                        min_value=0,
                                        step=1, 
                                        value=0, 
                                        key="dimension_counter")

    metric_counter = st.number_input("Number of Metrics", 
                                     min_value=0,
                                     step=1,
                                     value=0, 
                                     key="metric_counter")

    # Call the function to add or remove multiselect boxes for dimensions and metrics
    add_or_remove_multiselect(dimension_counter, "Dimension", st.session_state['dimension_list'])
    add_or_remove_multiselect(metric_counter, "Metric", st.session_state['metric_list'])
    
    st.session_state['filter_key'] = current_list
    return

def create_filter_interface(dataset):
    # Ensure dataset is a DataFrame
    if isinstance(dataset, str):

        dataset = st.session_state[dataset]

    # Create a placeholder DataFrame to hold the filter conditions
    metric_filter_df = pd.DataFrame(columns=['Column', 'min', 'max'])
    dimension_filter_df = pd.DataFrame(columns=['Column', 'Condition', 'Value'])

    # Iterate through metric list to create input widgets
    for metric in st.session_state['filter_key']:

        metric_counter = st.session_state['metric_counter']

        for i in range(metric_counter):

            if metric in st.session_state['metric_list']:
                    
                    if metric not in metric_filter_df["Column"]:

                        try :
                                
                                if pd.api.types.is_numeric_dtype(dataset[metric]):

                                    min_val = st.sidebar.slider(f"Minimum value for metric filter {metric} {i}", 
                                                                min_value=float(dataset[metric].min()),
                                                                max_value=float(dataset[metric].max()),   
                                                                value=float(dataset[metric].min()),
                                                                key=f"Minimum_value_{metric}_{i}")
                                    
                                    max_val = st.sidebar.slider(f"Maximum value for {metric} {i}",
                                                                min_value=float(dataset[metric].min()),
                                                                max_value=float(dataset[metric].max()),
                                                                value=float(dataset[metric].max()),
                                                                key=f"Maximum_value_{metric}_{i}")
                                
                                    temp_series = pd.DataFrame(
                                        columns=['Column', 'min', 'max'], 
                                        data=[[metric, min_val, max_val]]
                                    )

                                    #metric_filter_df = pd.concat([metric_filter_df, temp_series], ignore_index=True)
                                    metric_filter_df = pd.merge(metric_filter_df, temp_series, how='outer')

                                    st.session_state['metric_filter_df'] = metric_filter_df

                        except st.errors.DuplicateWidgetID :
                            st.write('you cant have more than one metric filter per metric')
            #need to swap this out 
                         

    # Iterate through dimension list to create input widgets
    for dimension in st.session_state["filter_key"]:
            
            dimension_counter = st.session_state['dimension_counter']

            for i in range(dimension_counter):
                    
                    if dimension in st.session_state["dimension_list"]:

                        condition = st.sidebar.selectbox(f"Select your condition for dimension filter {dimension} {i}",
                                                        options=["RE contains", "RE matches exactly", "RE starts with", "RE ends with", "RE custom"])
                        
                        if condition == "custom RE":

                            value = st.text_input(f'Enter your expression for custom RE dimension filter {dimension} {i}', value="yes")

                        else:

                            value = st.text_input(f'Enter your expression for dimension filter {dimension} {i}', value="yes")
                        
                        temp_dim_df = pd.DataFrame(data=[{'Column': dimension, 'Condition': condition, 'Value': value}])
                        
                        dimension_filter_df = pd.merge(dimension_filter_df, temp_dim_df, how='outer')

                    st.session_state['dimension_filter_df'] = dimension_filter_df


    return

def apply_filter(dataframe):

    if 'dimension_filter_df' in st.session_state:

        dimension_filter_df = st.session_state['dimension_filter_df']

        for index, row in dimension_filter_df.iterrows():

            try:

                dimcolumn = row['Column']
                dimvalue = row['Value']
                condition = row['Condition']

                if condition == "RE contains":

                    dataframe = dataframe[dataframe[dimcolumn].str.contains(dimvalue, flags=re.IGNORECASE, regex=True)]

                elif condition == "RE matches exactly":

                    dataframe = dataframe[dataframe[dimcolumn].str.fullmatch(dimvalue, regex=True)]

                elif condition == "RE starts with":

                    pattern_starts_with = '^' + dimvalue
                    dataframe = dataframe[dataframe[dimcolumn].str.contains(pattern_starts_with, flags=re.IGNORECASE, regex=True)]

                elif condition == "RE ends with":
                    
                    pattern_ends_with = dimvalue + '$'
                    dataframe = dataframe[dataframe[dimcolumn].str.contains(pattern_ends_with, flags=re.IGNORECASE, regex=True)]

                elif condition == "RE custom":

                    dataframe = dataframe[dataframe[dimcolumn].str.contains(dimvalue, flags=re.IGNORECASE, regex=True)]

            except Exception as e:

                st.write(e)

    if 'metric_filter_df' in st.session_state:

        metric_filter_df = st.session_state['metric_filter_df']

        for index, row in metric_filter_df.iterrows():

            try:

                metric_column = row['Column']
                min_valueapp = row['min']
                max_valueapp = row['max']
                dataframe = dataframe[(dataframe[metric_column] >= min_valueapp) & (dataframe[metric_column] <= max_valueapp)]

            except Exception as e:

                st.write(e)

    return dataframe

def date_filter_fn(date_col, start_date, end_date):

    if 'current_df' in st.session_state:

        dataframe = st.session_state['current_df']
        dataframe = dataframe[(dataframe[date_col] >= start_date) & (dataframe[date_col] <= end_date)]

    return dataframe

def extract_date_components():

    df = st.session_state["current_df"]
    column_name = st.session_state["date_col"]
    
    # Attempt to parse the column to datetime
    df['parsed_date'] = pd.to_datetime(df[column_name], errors='coerce')
    
    # Extract day, month, and year
    df[f'{st.session_state["date_col"]}_day'] = df['parsed_date'].dt.day
    df[f'{st.session_state["date_col"]}_month'] = df['parsed_date'].dt.strftime('%B')
    df[f'{st.session_state["date_col"]}_year'] = df['parsed_date'].dt.year

    #work around to remove the commas from the year column
    #df[f'{st.session_state["date_col"]}_year'] = df['year'].astype(str).str.replace(',', '').astype(int)

    # Alert for rows where the date could not be parsed
    unparsed_rows = df[df['parsed_date'].isnull()].shape[0]
    
    # Drop the temporary parsed_date column
    df.drop(columns=['parsed_date'], inplace=True)
    
    if unparsed_rows > 0:

        message = f"Warning: {unparsed_rows} rows could not be parsed as dates and were set to NaN."

    else:

        message = "All rows parsed successfully."

    st.session_state["current_df"] = df

    return



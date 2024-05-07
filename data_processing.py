import pandas as pd
import chardet
from charset_normalizer import detect
import streamlit as st
import io
from settings import add_to_session_state

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
                errors.append(f"Error reading file {file_name}: {str(e)}")
            continue 

        filetype = file_name.split(".")[-1]
        if filetype == "csv":
            try:
                # Attempt to read CSV file with detected encoding
                df = pd.read_csv(io.BytesIO(file_contents), encoding=detected_encoding)
            except pd.errors.ParserError:
                errors.append(f"Error reading file {file_name}: {str(e)}")
        elif filetype == "xlsx": # if it's not csv load xlsx
            try:
                df = pd.read_excel(file) # Attempt to read Excel file
            except Exception as e:
                errors.append(f"Error reading file {file_name}: {str(e)}")
                continue 
        elif (filetype != "csv" and filetype != "xlsx"):
            st.error("Invalid file format. Please upload an Excel (xlsx) or CSV file.")
            return None
        try:
            dfs.append(df) # lets concat/append the dfs to the dfs list together
        except: # Exception : e 
            errors.append(f"Error processing file {file_name}: {str(e)}")
            st.write('❌Sadly we have a problem with your file.. perhaps attempt to convert it via another program and try again.❌')
            st.write(error)

    master_df = None

    #create master df from either dfs if multiple dfs or just use the df
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
        #create master df then set selected df to be master df
        if 'current_df' not in st.session_state:
            current_df = pd.DataFrame(data=master_df, columns=master_df.columns, index=master_df.index)

        add_to_session_state("master_df", master_df)
        add_to_session_state("current_df", master_df)
        add_to_session_state("file_names", file_names)
        add_to_session_state("dfs", dfs)

    return

@st.cache_data
def detect_data_types(df):
    # Detect data types and create dictionaries for dimensions and metrics
    dimension_list = [col for col, dtype in df.dtypes.items() if dtype == "object"]
    metric_list = [col for col, dtype in df.dtypes.items() if dtype != "object"]
    dim_met_dtype_dict = {col: dtype for col, dtype in df.dtypes.items()}
    add_to_session_state("dim_met_dtype_dict", dim_met_dtype_dict)
    add_to_session_state("dimension_list", dimension_list)
    add_to_session_state("metric_list", metric_list)

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

#
# testing space!!
#

def create_filter_interfaceold(metric_list, dimension_list):
    # Create a placeholder DataFrame to hold the filter conditions
    filter_df = pd.DataFrame(columns=['Column', 'Condition', 'Value'])

    # Iterate through metric list and dimension list to create input widgets
    for metric in metric_list:
        # For numerical columns, use a slider
        if metric['dtype'] in ['int', 'float']:
            min_val = st.sidebar.slider(f"Minimum value for {metric['name']}", float(metric['min']), float(metric['max']), float(metric['min']))
            max_val = st.sidebar.slider(f"Maximum value for {metric['name']}", float(metric['min']), float(metric['max']), float(metric['max']))
            filter_df = filter_df.append({'Column': metric['name'], 'Condition': 'between', 'Value': (min_val, max_val)}, ignore_index=True)
        # For date columns, use a date picker
        elif metric['dtype'] == 'datetime64':
            date_val = st.sidebar.date_input(f"Select date for {metric['name']}")
            filter_df = filter_df.append({'Column': metric['name'], 'Condition': '==', 'Value': date_val}, ignore_index=True)
    
    for dimension in dimension_list:
        # For string columns, use a drop-down
        if dimension['dtype'] == 'object':
            options = st.sidebar.multiselect(f"Select {dimension['name']}", dimension['values'])
            filter_df = filter_df.append({'Column': dimension['name'], 'Condition': 'in', 'Value': options}, ignore_index=True)

    return filter_df


def create_filter_interfacenewer(dataset, metric_list, dimension_list):
    # Create a placeholder DataFrame to hold the filter conditions
    filter_df = pd.DataFrame(columns=['Column', 'Condition', 'Value'])

    # Iterate through metric list to create input widgets
    for metric in metric_list:
        # For numerical columns, use a slider
        if metric['dtype'] in ['int', 'float']:
            min_val = st.sidebar.slider(f"Minimum value for {metric['name']}", float(dataset[metric['name']].min()), float(dataset[metric['name']].max()), float(dataset[metric['name']].min()))
            max_val = st.sidebar.slider(f"Maximum value for {metric['name']}", float(dataset[metric['name']].min()), float(dataset[metric['name']].max()), float(dataset[metric['name']].max()))
            filter_df = filter_df.append({'Column': metric['name'], 'Condition': 'between', 'Value': (min_val, max_val)}, ignore_index=True)
        # For date columns, use a date picker
        elif metric['dtype'] == 'datetime64':
            date_val = st.sidebar.date_input(f"Select date for {metric['name']}")
            filter_df = filter_df.append({'Column': metric['name'], 'Condition': '==', 'Value': date_val}, ignore_index=True)
    
    # Iterate through dimension list to create input widgets
    for dimension in dimension_list:
        # For string columns, use a drop-down
        if dimension['dtype'] == 'object':
            options = st.sidebar.multiselect(f"Select {dimension['name']}", dimension['values'])
            filter_df = filter_df.append({'Column': dimension['name'], 'Condition': 'in', 'Value': options}, ignore_index=True)

    return filter_df

def create_filter_interface(dataset, metric_list, dimension_list):
    # Create a placeholder DataFrame to hold the filter conditions
    filter_df = pd.DataFrame(columns=['Column', 'Condition', 'Value'])

    # Iterate through metric list to create input widgets
    for metric in metric_list:
        # For numerical columns, use a slider
        if dataset[metric].dtypes() in ['int', 'float']:
            min_val = st.sidebar.slider(f"Minimum value for {metric}", float(dataset[metric['name']].min()), float(dataset[metric['name']].max()), float(dataset[metric['name']].min()))
            max_val = st.sidebar.slider(f"Maximum value for {metric}", float(dataset[metric['name']].min()), float(dataset[metric['name']].max()), float(dataset[metric['name']].max()))
            filter_df = filter_df.append({'Column': metric['name'], 'Condition': 'between', 'Value': (min_val, max_val)}, ignore_index=True)
        # For date columns, use a date picker
        elif dataset[metric].dtypes() == 'datetime64':
            date_val = st.sidebar.date_input(f"Select date for {metric}")
            filter_df = filter_df.append({'Column': metric['name'], 'Condition': '==', 'Value': date_val}, ignore_index=True)
    
    # Iterate through dimension list to create input widgets
    for dimension in dimension_list:
        # For string columns, use a drop-down
        if dataset[dimension].dtypes() == 'object':
            options = st.sidebar.multiselect(f"Select {dimension['name']}", dimension['values'])
            filter_df = filter_df.append({'Column': dimension['name'], 'Condition': 'in', 'Value': options}, ignore_index=True)

    return filter_df
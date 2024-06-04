import streamlit as st
from data_processing import extract_date_components, date_filter_fn, apply_filter, format_column, calculate_statistics, uploadedfilesload, deduplicate, drop_columns, melt_data, group_data, detect_data_types, create_filter_interface, concat_data, transpose_data, st_form_with_counters
from settings import pivot_on, os_num_fn, visualise_on, start_graph_func, graph_on, reset_on_click, hide_ds_on_click, add_to_session_state, adjust_on_click # type: ignore
from visualization import launch_pivot
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import plotly.express as px
import random

def init_ss():
    #dictionary of items to initalise when we start
    ss_init_dict = dict(
    hideupload=False,
    Adjust=False,
    Analyse=False,
    custom_filter=False,
    barchart=False,
    format_col_show=False,
    piv_on = True,
    pivot_counter=0,
    uploaded_files=[],
    custom_format=None,
    col_list=[],
    show_graph=False,
    start_graph=False,
    vis_on=False,
    os_num=0
    )

    #initalise the dict
    for key, values in ss_init_dict.items():

        if key not in st.session_state:

            add_to_session_state(key, values)
    
    os_num_fn()

if 'ss_init_dict' not in st.session_state:
    init_ss()

def main():

    #column hijinks to attempt at center alignment lol
    bod1, bod2, bod3 = st.columns([0.05,0.9,0.05])

    with bod2:

        st.title("👀PEEK👀")
        st.write(st.session_state['os_text'])
        
        st.write("")
        #if we've uploaded a file/started messing withs the file lets hide the inital ramble
        if st.session_state["hideupload"] == False:

            st.write("")
            st.write("")
            st.header("Welcome!")
            st.write("We accept CSV and XLSX files and proudly invite multi-indexers to go elsewhere.")
            st.header("🕵🏼Find your files🕵🏼")

    #key streamlit file upload routine
    uploaded_files = st.file_uploader(" ", type=["csv", "xlsx"], accept_multiple_files=True)

    #if we've uploaded any files
    if uploaded_files:

        uploadedfilesload(uploaded_files)

        #the above function should create this.. lets wait until its in the ss
        if 'current_df' in st.session_state:

            #once it is lets do this
            detect_data_types(st.session_state['current_df'])

            #if we're hiding the features
            if st.session_state["hideupload"] == False:

                #if we've not agreed to hide it here's the descriptive stats bit
                for i, df in enumerate(st.session_state['dfs']):

                    #for each file give me the number of rows and columns
                    st.subheader(f"Uploaded File {i + 1}: {uploaded_files[i].name}")
                    st.write(f"Number of Rows: {len(df)}")
                    st.write(f"Number of Columns: {len(df.columns)}")

                #create columns so we can see the data and the descriptive stats next to each other
                colload, colview = st.columns(2)

                with colload:

                    #calulates the statics, then displays them
                    stats_df, shape = calculate_statistics(st.session_state['current_df'])
                    st.subheader("Descriptive Statistics")
                    st.write(stats_df)
                    st.subheader("Data Types")
                    dtypes_df = st.session_state['current_df'].dtypes.reset_index()
                    dtypes_df.columns = ['Column', 'Type']
                    st.table(dtypes_df)

                with colview:

                    #displays preview
                    st.subheader("Uploaded file(s)")
                    st.write(st.session_state['current_df'])

            #regardless of the hide upload lets open up a sidebar if we've files to look at! we're now indented one for sidebar activity
            if st.session_state["Adjust"] ==  True:

                st.session_state["hideupload"] == True
                st.write(st.session_state['current_df'])

                with st.sidebar:

                    #adjust quick access settings
                    st.header("Adjust Settings")
                    st.write('Quick actions')
                    st.button("Reset to original load", on_click=reset_on_click)
                    
                    #depulicate
                    if st.button("Quick Deduplicate (all dims)"): 

                        try: 

                            st.session_state['current_df'] = deduplicate(st.session_state['current_df'])
                            st.success("Deduplication completed!")

                        except Exception as e:

                            st.write(e)
                    
                    #transpose data
                    if st.button("Transpose Data"):

                        try:

                            st.session_state['current_df'] = transpose_data(st.session_state['current_df'])
                            st.write('current_df')
                            st.success("Data transposed!")

                        except Exception as e:

                            st.write(e)

                    st.divider()

                    st.write("Setup your date schema")
                    st.sidebar.selectbox("Select your date column",options=st.session_state["col_list"], key="date_col")

                    #date schema function
                    if st.button("Build date schema"):
                        try:
                            extract_date_components()
                            st.success("Date schema built!")
                        except Exception as e:
                            st.write(e)
                    
                    #filtering
                    st.subheader('Filter')

                    st.sidebar.subheader('Date Range Entry')
                    start_date = st.sidebar.date_input('Start Date', datetime(2024, 1, 1))
                    end_date = st.sidebar.date_input('End Date', datetime(2024, 9, 15))

                    if st.sidebar.button("Apply", key="date_filter"):

                        st.session_state["current_df"] = date_filter_fn(start_date, end_date)

                    st_form_with_counters()
                    current_df = st.session_state['current_df']

                    create_filter_interface('current_df')
                        
                    if st.button("Apply filters"):

                        st.session_state['current_df'] = apply_filter(st.session_state['current_df'])

                    st.divider()

                    #concat columns
                    st.subheader("Concat")

                    concat_cols = st.multiselect("Select columns to concat:",
                                                st.session_state['col_list'],
                                                key="concat_cols")
                    
                    seperator = st.text_input("chosen seperator", 
                                            value="_", 
                                            key="seperator")
                    
                    concatname = st.text_input("New column name", 
                                            value="Example", 
                                            key="concatname")

                    if st.button("Concat columns"):

                        try :

                            st.session_state['current_df'] = concat_data(st.session_state['current_df'],
                                                                    st.session_state['concat_cols'],
                                                                        st.session_state['seperator'],
                                                                        st.session_state['concatname'])
                            st.success("columns concatenated!")

                        except Exception as e:

                            st.write(e)
                    
                    st.divider()
                    
                    #format data
                    st.subheader("Format columns")
                    column_to_reformat = st.selectbox("Select column to reformat:", 
                                                      st.session_state['col_list'],
                                                       key="column_to_reformat")
                    
                    format_options = ['String','Integer', 'Currency (£)', 'Currency ($)', 'Custom']

                    st.selectbox("Select format type:", 
                                 format_options,
                                 key="chosen_format")

                    if st.button("Reformat"):

                        if st.session_state['custom_format'] != None:

                            try:

                                st.session_state['current_df'] = format_column(st.session_state['column_to_reformat'],
                                                                                st.session_state['chosen_format'])
                                st.write(st.session_state['current_df'])

                            except Exception as e:

                                st.write(e)

                        elif st.session_state['custom_format'] is None:

                            try:
                                st.session_state['current_df'] = format_column(st.session_state['column_to_reformat'],
                                                                                st.session_state['chosen_format'],
                                                                                None)
                                st.write(st.session_state['current_df'])

                            except Exception as e:

                                st.write(e)

                        else: st.write(f"Current_df is somehow not none and not not none, this is the equivalent of dividing by zero. Good luck son, {e}")


                    st.divider()

                    if st.button("Hide Adjust", key='hide_adjust_2'):

                        st.session_state["Adjust"] = False

            if st.session_state["Adjust"] == False:

                st.button("Adjust", on_click=adjust_on_click)
            

            #analyze step
            if st.session_state["Analyse"] == False:

                st.button("Analyse", on_click=hide_ds_on_click)


            if st.session_state["Analyse"] == True:

                st.header('Analyse')

                #graphing controls
                if st.session_state["vis_on"] == False:
                    st.button('Visualise data', on_click="visualise_on")

                if st.session_state["vis_on"] == True:

                    ###Selecting columns for index and values
                    index_col = st.selectbox("Select dimension columns",
                                              options=st.session_state['dimension_list'],
                                                key="graph_index_col")
                    
                    values_col = st.selectbox("Select metric columns",
                                               options=st.session_state['metric_list'],
                                                 key="graph_values_col")

                    # Creating pivot table
                    graph_table = pd.pivot_table(st.session_state['current_df'],
                                                  index=st.session_state['graph_index_col'],
                                                    values=st.session_state['graph_values_col'])

                    # Visualization options
                    graph_type = st.selectbox("Select graph type",
                                               options=["Bar Chart", "Pie Chart", "Line Chart", "Scatter Chart"],
                                               key="graph_type")
                
                    if st.button("Generate Graph"):#, on_click="graph_on"):
                        st.session_state['show_graph'] = True


                #pivot controls
                if st.session_state["piv_on"] == False:

                    st.button("Pivot", on_click=pivot_on)

                if st.session_state["piv_on"] == True:

                    st.subheader('Pivot Table')

                    bod_an_1, bod_an_2, bod_an_3, bod_an_4, bod_an_5 = st.columns([0.1,
                                                                                    0.26,0.26,0.26,
                                                                                    0.1])

                    with bod_an_2:

                        if st.button("Create new"):

                            st.session_state['pivot_counter'] += 1
                    
                    with bod_an_3:

                        if st.button("Remove one"):

                            st.session_state['pivot_counter'] -= 1

                    with bod_an_4:      
                        if st.button("Remove all"):

                            st.session_state['pivot_counter'] = 0
                
                    launch_pivot()


                # start of graphing bit
                if st.session_state['show_graph'] == True:

                    if st.session_state['graph_type'] == "Bar Chart":

                        graph_table = st.session_state["graph_table"]
                        fig, ax = plt.subplots()
                        graph_table.plot(kind='bar', ax=ax)
                        st.pyplot(fig)

                    elif st.session_state['graph_type'] == "Pie Chart":

                        fig = px.pie(values=st.session_state['value_col'],
                                      names=st.session_state['index_col'])
                        
                        st.plotly_chart(fig)

                    elif st.session_state['graph_type'] == "Line Chart":

                        fig, ax = plt.subplots()

                        graph_table.plot(ax=ax)
                        
                        st.pyplot(fig)

                    elif st.session_state['graph_type'] == "Scatter Chart":

                        if len(st.session_state["graph_values_col"]) != 2:

                            st.error("Scatter Chart requires exactly 2 value columns.")

                        else:

                            fig = px.scatter(graph_table,
                                              x=st.session_state['index_col'],
                                                y=st.session_state['value_col'], 
                                                color=graph_table.index)
                            
                            st.plotly_chart(fig)
                    else:
                        print('waiting...')


    elif uploaded_files and 'current_df' not in st.session_state:

        st.write("Something's gone wrong. JC - Uploaded_files is in the session state but we don't have a current_df. No idea mate.")

        
#the thing that does the thing
if __name__ == "__main__":
    main()

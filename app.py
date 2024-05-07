import streamlit as st
from data_processing import calculate_statistics, uploadedfilesload, deduplicate, drop_columns, melt_data, group_data, detect_data_types, create_filter_interface
from settings import reset_on_click, hide_ds_on_click, add_to_session_state, adjust_on_click, filter_on_click # type: ignore
import pandas as pd

def main():

    if 'hideupload' not in st.session_state:
        st.session_state.hideupload = False

    if 'Adjust' not in st.session_state:
        st.session_state["Adjust"] = False
    
    if 'Analyse' not in st.session_state:
        st.session_state["Analyse"] = False

    if 'Filter' not in st.session_state:
        st.session_state["Filter"] = False

    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []

    st.title("👀PEEK👀")
    st.write("")

    if st.session_state["hideupload"] == False:
        
        st.write("You can after adding data make adjustments to it before exploring and visualising your findings")
        st.write("We accept CSV and XLSX files and proudly invite multi-indexers to go fudge themselves.")
        st.header("🕵🏼Find your files🕵🏼")

    uploaded_files = st.file_uploader("Upload file(s)", type=["csv", "xlsx"], accept_multiple_files=True, key="uploaded_files")

    if uploaded_files:
        
    #if len(st.session_state['uploaded_files'])>1:
        if st.session_state["hideupload"] == False:
            uploadedfilesload(uploaded_files)
            detect_data_types(st.session_state['current_df']) 
            #if we've not agreed to hide it here's the descriptive stats bit
            for i, df in enumerate(st.session_state['dfs']):
                st.subheader(f"Uploaded File {i + 1}: {uploaded_files[i].name}")
                st.write(f"Number of Rows: {len(df)}")
                st.write(f"Number of Columns: {len(df.columns)}")
            colload, colview = st.columns(2)
            with colload:
                stats_df, shape = calculate_statistics(st.session_state['master_df'])
                st.subheader("Descriptive Statistics")
                st.write(stats_df)
            with colview:
                st.subheader("Uploaded file(s)")
                st.write(st.session_state['master_df'])
                #reardless of the hide upload lets open up a sidebar if we've files to look at! we're now indented one for sidebar activity
        if st.session_state["Adjust"] ==  True:
            with st.sidebar:
                st.header("Adjust")
                st.session_state.reset_on_button = False
                st.button("Reset", on_click=reset_on_click)
                if st.button("Deduplicate"):
                    st.session_state['current_df'] = deduplicate(st.session_state['current_df'])
                    st.success("Deduplication completed!")

                # Drop Columns
                columns_to_drop = st.multiselect("Select Columns to Drop:", st.session_state['current_df'].columns, key="columns_to_drop")
                if st.button("Drop Columns"):
                    st.session_state['current_df'] = drop_columns(st.session_state['current_df'], st.session_state["columns_to_drop"])
                    st.success("Columns dropped!")

                # Melt Data
                melt_by = st.multiselect("Select Columns to melt by:", st.session_state['current_df'].columns, key="melt_by")
                if st.button("Melt Data"):
                    st.session_state['current_df'] = melt_data(st.session_state['current_df'], st.session_state["melt_by"])
                    st.success("Data melted!")

                #transpose data

                #concat columns

                #split columns by seperator

                #convert data types

                # Group Data
                st.session_state['group_by_columns'] = st.multiselect("Select Columns to Group By:", st.session_state['dimension_list'])
                if st.button("Group Data"):
                    st.session_state['current_df'] = group_data(st.session_state['current_df'], st.session_state["group_by_columns"])
                    st.success("Data grouped!")

        if st.session_state["Filter"] == True:
            with st.sidebar:
                st.header('Filter')
                create_filter_interface(st.session_state['current_df'],st.session_state['metric_list'],st.session_state['dimension_list'])

        if st.session_state["Filter"] == False:
            st.button("Filter", on_click=filter_on_click)

        if st.session_state["Adjust"] == False:
            st.button("Adjust", on_click=adjust_on_click)

        if st.session_state["Analyse"] == False:
            st.button("Analyse", on_click=hide_ds_on_click)

        # Display Updated Data
        st.subheader("Updated Data:")
        st.write(st.session_state['current_df'])

        st.subheader('Re-Pivot')
        index_col = st.multiselect("Select column for index", options=st.session_state['current_df'].columns)
        values_col = st.multiselect("Select column for values", options=st.session_state['current_df'].columns)
        
        # Pivot table creation
        pivot_table = pd.pivot_table(st.session_state['current_df'], index=index_col, values=values_col)
        
        # Display pivot table
        st.subheader("Pivot Table")
        st.write(pivot_table)




#the thing that does the thing
if __name__ == "__main__":
    main()
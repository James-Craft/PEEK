
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import os

def launch_graph():

    st.title("Graphing App")

    return

def launch_pivot():
    if st.session_state['pivot_counter'] > 0:

        for i in range(st.session_state['pivot_counter']):
                
                inum = i+1
                
                index_col = st.multiselect(f"Customise dimension columns {inum}", 
                                        options=st.session_state['dimension_list'],
                                        default=st.session_state['dimension_list'],
                                        key=f"pivot_{inum}_ind_col")

                values_col = st.multiselect(f"Customise metric columns {inum}",
                                            options=st.session_state['metric_list'],
                                            default=st.session_state['metric_list'],
                                            key=f"pivot_{inum}_val_col")

                pivot_table = pd.pivot_table(st.session_state['current_df'],
                                                    index=st.session_state[f"pivot_{inum}_ind_col"],
                                                    values=st.session_state[f"pivot_{inum}_val_col"])
                
                if st.button("Restore defaults", key=f"pivot_{inum}_dim_add"):

                    index_col = st.session_state['dimension_list']
                    values_col = st.session_state['metric_list']
                    
                if len(index_col)>0:

                    try:

                        st.write(pivot_table)

                        if st.button(f"Save for now", key=f"pivot_{i}_save_for_now"):

                            try:

                                st.session_state['current_df'] = pivot_table
                                current_df = st.session_state['current_df']

                            except Exception as e:

                                st.write(f"Error: {e}")

                        if st.button(f"Save for later", key=f"pivot_{i}_save_for_later"):

                            try:

                                cwd = os.listdir()
                                export_dt = export_dt.strftime("%Y-%m-%d")  
                                pivot_table.to_csv(f"{cwd}/PEEKED_ON_{export_dt}.csv")

                            except Exception as e:

                                st.write(f"Error: {e}")

                    except ValueError:

                        print(ValueError)

                else :

                    st.write('you need more columns..')
    return

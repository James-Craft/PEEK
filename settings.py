import streamlit as st

def reset_on_click():
    add_to_session_state("selected_df", st.session_state['master_df'])

def hide_ds_on_click():
    st.session_state['hideupload'] = True

def adjust_on_click():
    st.session_state['Adjust'] = True

def add_to_session_state(item, value):
    st.session_state[item] = value

def filter_on_click():
    st.session_state['Filter'] = True
import streamlit as st
import random

def reset_on_click():

    st.session_state["current_df"] = st.session_state['master_df']

    return

def hide_ds_on_click():

    st.session_state['hideupload'] = True
    st.session_state['Analyse'] = True

    return

def adjust_on_click():
    
    st.session_state['hideupload'] = True
    st.session_state['Adjust'] = True

    return

def add_to_session_state(item, value):

    st.session_state[item] = value

    return

def graph_on():

    st.session_state['show_graph'] = True

    #   if st.session_state['show_graph'] == True:
    #     st.session_state['show_graph'] = False
    # elif st.session_state['show_graph'] == False:
    #     st.session_state['show_graph'] = True

    return

def start_graph_func():

    st.session_state['start_graph'] = True

    # if st.session_state['start_graph'] == True:
    #     st.session_state['start_graph'] = False
    # elif st.session_state['start_graph'] == False:
    #     st.session_state['start_graph'] =True

    return

def visualise_on():

    st.session_state['vis_on'] = True

    # if st.session_state['vis_on'] == True:
    #     st.session_state['vis_on'] = False
    # elif st.session_state['vis_on'] == False:
    #     st.session_state['vis_on'] =True

    return

def os_num_fn():
    # Generate a random num
    i = random.randint(1, 9)
    
    # Define the dictionary
    os_dict = {
        1: "Evenin' sugar lips",
        2: "The same thing we do every night Pinky, hardcore data analysis.",
        3: "Gewwon then sailor, just make it quick",
        4: "Load your data, change it or just see what's there...",
        5: "Better button up rude-boy, it's about to get filtyyyy",
        6: "D.R.E.A.M",
        7: "Data Rules Everything Around Me",
        8: "Dropping dirty data dubs since '23",
        9: "Deleting Folder System32 In Progress..."
    }
    
    # Check if the random number is a key
    if i in os_dict:
        # Set the value for ss
        st.session_state["os_text"] = os_dict[i]


def pivot_on():
    
    st.session_state["piv_on"] = True

    return

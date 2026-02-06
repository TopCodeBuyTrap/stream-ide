# pip install streamlit_option_menu
# pip install streamlit-multi-menu
import streamlit as st
from streamlit import expander
from streamlit_option_menu import option_menu

# 1. as sidebar menu
with st.sidebar:
	selected = option_menu("Main Menu", ["Home", 'Settings'],
	                       icons=['house', 'gear'], menu_icon="cast", default_index=1)
	selected

# 2. horizontal menu
with st.popover("Open popover"):
	selected2 = option_menu(None, ["Home", "Upload", "Tasks", 'Settings'],
                        icons=['house', 'cloud-upload', "list-task", 'gear'],
                        menu_icon="cast", default_index=0, orientation="vertical")
selected2

from streamlit_multi_menu import streamlit_multi_menu

### Define Menu
sub_menus = {"Finance":["Stock prediction","Turn around rate"],
             "Cars":["Drift","Garage"],
             "Food":["Ramen","Bubble Tea","Kitchen Design"]}

# Optinally you can supply google icons
sub_menu_icons = {
    "Finance": ["trending_up", "sync_alt"],
    "Cars": ["directions_car", "garage"],
    "Food": ["restaurant", "local_cafe", "kitchen"]
}

selected_menu = streamlit_multi_menu(menu_titles=list(sub_menus.keys()),
                              sub_menus=sub_menus,
                            sub_menu_icons = sub_menu_icons,
                            use_container_width=True)

if selected_menu != None:
    st.write("The selected menu is:",selected_menu)
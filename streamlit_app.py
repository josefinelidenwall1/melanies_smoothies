# Import python packages
import streamlit as st
import requests  
from snowflake.snowpark.functions import col
from cryptography.hazmat.primitives import serialization

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie!:cup_with_straw:")
st.write(
  """Choose the fruits you want in your custom Smoothie!
  """
)


name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# --- START OF CONNECTION FIX ---
key_string = st.secrets["connections"]["snowflake"]["private_key_str"]

p_key = serialization.load_pem_private_key(key_string.encode('utf-8'), password=None)
pkb = p_key.private_bytes(
    encoding=serialization.Encoding.DER,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

cnx = st.connection("snowflake", private_key=pkb)
# --- END OF CONNECTION FIX ---

session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
#st.dataframe(data=my_dataframe, use_container_width=True)

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:'
    , my_dataframe
    , max_selections=5
    )

if ingredients_list:
    ingredients_string=''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

    #st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                    values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    #st.write(my_insert_stmt)
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered, ' + name_on_order + '!', icon="✅")



smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")  
#st.text(smoothiefroot_response.json())
st_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

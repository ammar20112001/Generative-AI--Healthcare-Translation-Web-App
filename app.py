import streamlit as st

x = st.text_input("write your sentence:")

if x:
    st.write('Tranlated text')


button = st.button('Play Audio')

if button:
    st.write('Audio playing...')

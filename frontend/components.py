import streamlit as st

def section(title: str, caption: str | None = None):
    st.subheader(title)
    if caption: st.caption(caption)

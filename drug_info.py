import streamlit as st
from hydralit import HydraHeadApp


class druginfoApp(HydraHeadApp):

    def run(self):
        #-------------------existing untouched code------------------------------------------
        st.header('药品知识库')
        st.markdown("### Plot")

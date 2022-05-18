import streamlit as st
from streamlit.scriptrunner import get_script_run_ctx
from hydralit import HydraHeadApp


class druginfoApp(HydraHeadApp):

    def run(self):
        #-------------------existing untouched code------------------------------------------
        st.header('药品知识库')
        st.markdown("### Plot")
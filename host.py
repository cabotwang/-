from hydralit import HydraApp
import streamlit as st
from drug_info import druginfoApp
from cis_tool import cistoolApp

st.set_page_config(layout="wide")
if __name__ == '__main__':
    # this is the host application, we add children to it and that's it!
    st.title('药品测算平台')
    app = HydraApp(title='药品测算平台', favicon="🏠", navbar_theme={'menu_background':'royalblue'})
    # add all your application classes here
    app.add_app("测算工具", icon="⌨", app=cistoolApp())
    app.add_app("药品知识库", icon="📚", app=druginfoApp())

    # run the whole lot
    app.run()
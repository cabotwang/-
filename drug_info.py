import streamlit as st
import pandas as pd
from streamlit.scriptrunner import get_script_run_ctx
from hydralit import HydraHeadApp


data = pd.read_excel('./base_data/drug_cag.xlsx', usecols=['一级目录', '二级目录', '三级目录', '化学名'])
data.to_csv('./base_data/drug_cag.csv', index=False, encoding='utf-8_sig')

class druginfoApp(HydraHeadApp):

    def run(self):
        # -------------------existing untouched code------------------------------------------
        # st.header('药品知识库')
        @st.cache
        def data_read():
            drug_cag = pd.read_csv('./base_data/drug_cag.csv', usecols=['一级目录', '二级目录', '三级目录', '化学名'])
            return drug_cag

        data_drug_cag = data_read()
        set1 = set(data_drug_cag['一级目录'])

        ce, c1, ce, c2, ce = st.columns([0.07, 1, 0.07, 4, 0.07])

        with c1:
            st.write('按名称搜索')
            drug_name1 = st.text_input('请输入药品名称')
            submit = st.button('确认')
            st.write('按类别搜索')
            cag1 = st.selectbox('请选择药品大类', set1)
            set2 = set(data_drug_cag[data_drug_cag['一级目录'] == cag1]['二级目录'])
            cag2 = st.selectbox('请选择二级目录', set2)
            set3 = set(data_drug_cag[data_drug_cag['二级目录'] == cag2]['三级目录'])
            cag3 = st.selectbox('请选择三级目录', set3)
            set4 = set(data_drug_cag[data_drug_cag['三级目录'] == cag3]['化学名'])
            drug_name2 = st.selectbox('请选择药品', set4)
            submit2 = st.button('搜索')

        with c2:
            drug = ''
            if submit:
                drug = drug_name1
            if submit2:
                drug = drug_name2
            st.subheader(drug)


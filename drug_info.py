import streamlit as st
import pandas as pd
from hydralit import HydraHeadApp

data = pd.read_excel('./base_data/drug_cag.xlsx', usecols=['一级目录', '二级目录', '三级目录', '化学名', '英文名', '商品名',
                                                           '适应症', '用法用量', '招标价格', '招标时间', '招标规格', '中位使用时长',
                                                           '理论年花费', '中标省份'])
data.to_csv('./base_data/drug_cag.csv', index=False, encoding='utf-8_sig')


class druginfoApp(HydraHeadApp):

    def run(self):
        # -------------------existing untouched code------------------------------------------
        # st.header('药品知识库')
        df_slide = pd.DataFrame([], columns=['一级目录', '二级目录', '三级目录', '化学名', '英文名', '商品名',
                                             '适应症', '用法用量', '招标价格', '招标时间', '招标规格', '中位使用时长',
                                             '理论年花费', '中标省份'])
        @st.cache
        def data_read():
            drug_cag = pd.read_csv('./base_data/drug_cag.csv', usecols=['一级目录', '二级目录', '三级目录', '化学名', '英文名', '商品名',
                                                                        '适应症', '用法用量', '招标价格', '招标时间', '招标规格', '中位使用时长',
                                                                        '理论年花费', '中标省份'])

            def price_mod(p):
                try:
                    return '{:.0f}'.format(round(float(p), 0))
                except:
                    print(p)
                    return None
            drug_cag['招标价格'] = drug_cag['招标价格'].apply(price_mod)
            drug_cag['理论年花费'] = drug_cag['理论年花费'].apply(price_mod)
            drug_cag['招标时间'] = drug_cag['招标时间'].apply(lambda x: str(x).split(' ')[0])
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

            st.markdown("""
            <style>
            .label-font {
                font-size:22px !important; 
            }
            </style>
            """, unsafe_allow_html=True)
            if drug in data_drug_cag['化学名'].tolist():
                df_slide = data_drug_cag[data_drug_cag['化学名'] == drug]
                df_slide.index = df_slide['化学名']
                print('未找到化学名')
            elif drug in data_drug_cag['商品名'].tolist():
                df_slide = data_drug_cag[data_drug_cag['商品名'] == drug]
                df_slide.index = df_slide['商品名']
            else:
                df_slide = pd.DataFrame([], columns=['一级目录', '二级目录', '三级目录', '化学名', '英文名', '商品名',
                                                     '适应症', '用法用量', '招标价格', '招标时间', '招标规格', '中位使用时长',
                                                     '理论年花费', '中标省份'])

            if drug == '':
                pass
            else:
                st.markdown('<p class="label-font">英文名</p>', unsafe_allow_html=True)
                st.write(df_slide.loc[drug, '英文名'])

                st.markdown('<p class="label-font">商品名</p>', unsafe_allow_html=True)
                st.write(df_slide.loc[drug, '商品名'])

                st.markdown('<p class="label-font">适应症</p>', unsafe_allow_html=True)
                st.write(df_slide.loc[drug, '适应症'])

                st.markdown('<p class="label-font">用法用量</p>', unsafe_allow_html=True)
                st.write(df_slide.loc[drug, '用法用量'])

                st.markdown('<p class="label-font">招标信息</p>', unsafe_allow_html=True)
                st.table(df_slide[['招标价格', '招标规格', '中标省份', '招标时间']])

                st.markdown('<p class="label-font">中位使用时长</p>', unsafe_allow_html=True)
                st.write(df_slide.loc[drug, '中位使用时长'])

                st.markdown('<p class="label-font">理论年花费</p>', unsafe_allow_html=True)
                st.write('%s' % df_slide.loc[drug, '理论年花费'])
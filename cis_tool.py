import streamlit as st
import pandas as pd
from hydralit import HydraHeadApp
import math


# create a wrapper class
class cistoolApp(HydraHeadApp):
    def run(self):
        @st.cache(allow_output_mutation=True)
        def get_data():
            return []

        @st.cache
        def data_read():
            drug_utl = pd.read_csv('./base_data/incidence_rate.csv', usecols=['商品名', '适应症', '治疗评级', '使用率'])
            drug_cost = pd.read_csv('./base_data/drug_cost_peryear.csv', usecols=['商品名', '通用名', '适应症', '人均费用'])
            full_data = pd.read_csv('./base_data/full_data.csv', usecols=['唯一识别号', '地区', '适应症', '商品名', '通用名',
                                                                          '人次数', '药品总金额', '本次赔付金额', '既往症人数',
                                                                          '1万判定', '1.5万判定', '2万判定'])
            region_info = pd.read_csv('./base_data/region_info.csv', usecols=['地区', '参保率', '总参保人数', '非既往症', '既往症', '免赔额'])
            return drug_utl, drug_cost, full_data, region_info

        drug_utl, drug_cost, full_data, region_info = data_read()
        df = pd.DataFrame([], columns=['商品名', '通用名', '适应症', '治疗评级', '成本'])


        def _max_width_():
            max_width_str = f"max-width: 1900px;"
            st.markdown(
                f"""
            <style>
            .reportview-container.main.block-container{{
                {max_width_str}
            }}
            </style>    
            """,
                unsafe_allow_html=True,
            )

        _max_width_()

        with st.container():
            ce, c1, ce_1, c2, ce_2 = st.columns([0.07, 1.5, 0.07, 5, 0.07])

            with c1:
                uploader_measure = st.selectbox('测算方式', ('单个药品', '药品清单'))
                if uploader_measure == '单个药品':
                    drug_name = st.text_input("药品商品名")
                    ind_list = drug_cost[drug_cost['商品名'] == drug_name]['适应症'].tolist()
                    indication = st.selectbox("适应症:", ind_list)
                else:
                    druglist = st.file_uploader('上传药品清单', help='请上传excel文档', type=['xlsx'])
                    if druglist is not None:
                        data = pd.read_excel(druglist)

                deduction = st.text_input("免赔额:", value=0)
                par_rate = st.slider("参保率:", 0, 100, 40)

                PMH = st.checkbox('是否包含既往症患者')
                pmh_rate = -0.0096 * par_rate + 0.9457
                if PMH:
                    reburse_rate_1 = st.text_input("既往症患者赔付比例", value=50)
                    reburse_rate_2 = st.text_input("无既往症患者赔付比例", value=50)
                else:
                    reburse_rate_2 = st.text_input("赔付比例", value=80)
                    reburse_rate_1 = 0
                st.markdown("")
                add = st.button('进行测算')

                st.markdown("")

                def reburse_amount(amount, dedu, rb1, rb2, pmh_rate):
                    if float(amount) < float(dedu):
                        return 0
                    elif PMH:
                        return (float(amount) - float(dedu)) * (
                                float(rb1) * pmh_rate + float(rb2) * (1 - pmh_rate)) / 100
                    else:
                        return (float(amount) - float(dedu)) * (float(rb2) / 100)

                def ult_rate(base_rate, par_rate, cost, ded):
                    if PMH:
                        return base_rate*(-1.1299*par_rate+1.652) * min(1, math.exp(-0.9475*ded/cost+0.1394))
                    else:
                        return base_rate * (-1.1299 * par_rate + 1.652) * \
                               min(1, math.exp(-0.9475 * ded / cost + 0.1394))*0.3

                if add:
                    if uploader_measure == '单个药品':
                        if {'商品名': drug_name, '适应症': indication} not in get_data():
                            get_data().append({'商品名': drug_name, '适应症': indication})
                    else:
                        get_data().clear()
                        for row, columns in data.iterrows():
                            get_data().append({'商品名': columns['商品名'], '适应症': columns['适应症']})

                df1 = pd.DataFrame(data=get_data())
                df1 = pd.merge(df1, drug_cost, on=['商品名', '适应症'], how='left')
                df1 = pd.merge(df1, drug_utl, on=['商品名', '适应症'], how='left')
                df1['参保率'] = par_rate/100
                df1['免赔额'] = int(deduction)
                df1['使用率'] = df1.apply(lambda x:ult_rate(x['使用率'], x['参保率'], x['人均费用'], x['免赔额']), axis=1)
                df1['预计赔付金额'] = df1['人均费用'].apply(
                    lambda x: reburse_amount(x, deduction, reburse_rate_1, reburse_rate_2, pmh_rate))
                df1['成本'] = df1['使用率'] * df1['预计赔付金额']
                df1['使用率'] = df1['使用率'].apply(lambda x: '%.2f' % (x * 100000))
                df1 = df1[['商品名', '通用名', '适应症', '治疗评级', '使用率', '预计赔付金额', '成本']]
                df1['预计赔付金额'] = df1['预计赔付金额'].apply(lambda x: '%.0f' % x)
                df1 = df1.drop_duplicates(subset=['商品名', '适应症'])
                df = df1.set_index('商品名')

                with c2:
                    st.metric(label="药品成本", value='%.2f' % df['成本'].sum())
                    st.table(df)
                    clear = st.button('清除列表')
                    if clear:
                        get_data().clear()

        st.markdown("")
        with st.expander("详细说明", expanded=False):
            df1 = pd.merge(df, full_data, on=['商品名', '适应症'], how='inner')
            gdata = df1.groupby(['商品名', '地区', '适应症']).agg(
                {'人次数': 'count', '药品总金额': 'sum', '本次赔付金额': 'sum', '既往症人数': 'sum'}).reset_index()
            gdata.columns = ['商品名', '地区', '适应症', '人头数', '总费用', '总理赔金额', '既往症人数']
            gdata = pd.merge(gdata, region_info, on='地区', how='left')
            gdata['使用率(1/10万)'] = (gdata['人头数'] / gdata['总参保人数']).apply(lambda x: '%.2f' % (x * 100000))
            gdata['成本'] = gdata['总理赔金额'] / gdata['总参保人数']
            gdata['非既往症'] = gdata['非既往症'].apply(lambda x: format(x, '.0%'))
            gdata['人均自费'] = (gdata['总理赔金额'] / gdata['人头数']).apply(lambda x: int(x))
            gdata['既往症'] = gdata['既往症'].apply(lambda x: format(x, '.0%'))
            gdata['参保率'] = gdata['参保率'].apply(lambda x: format(x, '.0%'))
            gdata = gdata[['商品名', '适应症', '地区', '参保率', '使用率(1/10万)', '人均自费', '成本', '免赔额', '非既往症', '既往症']]
            gdata = gdata.set_index('商品名')
            # selection = aggrid_interactive_table(df=gdata)
            st.table(gdata)

            @st.cache
            def convert_df(df):
                # IMPORTANT: Cache the conversion to prevent computation on every rerun
                return df.to_csv().encode('utf-8')

            csv = convert_df(gdata)

            st.download_button(
                label="保存结果",
                data=csv,
                file_name='历史数据结果.csv',
                mime='text/csv',
            )
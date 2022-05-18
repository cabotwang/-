import pandas as pd
import streamlit as st


def main():
    @st.cache
    def data_read():
        drug_utl = pd.read_csv('incidence_rate.csv', usecols=['商品名', '适应症', '治疗评级', '使用率'])
        drug_cost = pd.read_csv('drug_cost_peryear.csv', usecols=['商品名', '通用名', '适应症', '人均费用'])
        full_data = pd.read_csv('full_data.csv', usecols=['唯一识别号', '地区', '适应症', '商品名', '通用名',
                                                                      '人次数',	'药品总金额',	'本次赔付金额', '既往症人数',
                                                                      '1万判定',	'1.5万判定',	'2万判定'])
        region_info = pd.read_csv('region_info.csv', usecols=['地区', '总参保人数', '非既往症', '既往症', '免赔额'])
        return drug_utl, drug_cost, full_data, region_info

    drug_utl, drug_cost, full_data, region_info = data_read()
    df = pd.DataFrame([], columns=['商品名', '通用名', '适应症', '治疗评级', '成本'])
    st.title('惠民保药品测算工具')

    def _max_width_():
        max_width_str = f"max-width: 1900px;"
        st.markdown(
            f"""
        <style>
        .reportview-container .main .block-container{{
            {max_width_str}
        }}
        </style>    
        """,
            unsafe_allow_html=True,
        )

    _max_width_()

    cols = st.columns(2)
    drug_name = cols[0].text_input("药品商品名")
    ind_list = drug_cost[drug_cost['商品名'] == drug_name]['适应症'].tolist()
    indication = cols[1].selectbox(
        "适应症:", ind_list)

    cols = st.columns(2)
    deduction = cols[0].text_input("免赔额:", value=0)
    par_rate = cols[1].slider("参保率:", 0, 100, 40)
    PMH = st.checkbox('是否包含既往症患者')
    pmh_rate = -0.0096*par_rate + 0.9457

    if PMH:
        cols = st.columns(2)
        reburse_rate_1 = cols[0].text_input("既往症患者赔付比例", value=50)
        reburse_rate_2 = cols[1].text_input("无既往症患者赔付比例", value=50)
    else:
        reburse_rate_2 = st.text_input("赔付比例", value=80)
        reburse_rate_1 = 0

    cols = st.columns(2)
    add = cols[0].button('增加药品')
    clear = cols[1].button('清除列表')
    if clear:
        st.experimental_memo.clear()

    def reburse_amount(amount, dedu, rb1, rb2, pmh_rate):
        if float(amount) < float(dedu):
            return 0
        else:
            return (float(amount)-float(dedu))*(float(rb1)*pmh_rate + float(rb2)*(1-pmh_rate))/100

    @st.cache(allow_output_mutation=True)
    def get_data():
        return []

    if add:
        get_data().append({'商品名': drug_name,'适应症': indication})
        df = pd.DataFrame(get_data())
        #
        df = pd.merge(df, drug_cost, on=['商品名', '适应症'], how='left')
        df = pd.merge(df, drug_utl, on=['商品名', '适应症'], how='left')
        df['赔付金额'] = df['人均费用'].apply(lambda x: reburse_amount(x, deduction, reburse_rate_1, reburse_rate_2, pmh_rate))
        df['成本'] = df['使用率'] * df['赔付金额']
        # df['使用率(1/10万)'] = df['使用率'].apply(lambda x: '%.2f' % (x*100000))
        # df['成本'] = df['成本'].apply(lambda x: '%.2f' % x)
        df = df[['商品名', '通用名', '适应症', '治疗评级', '成本']]
        df = df.drop_duplicates(subset=['商品名', '适应症'])
        df = df.set_index('商品名')
        st.write('药品成本为：%.2f' % df['成本'].sum())
        st.table(df)

    expander = st.expander("详细说明")
    with expander:
        df1 = pd.merge(df, full_data, on=['商品名', '适应症'], how='inner')
        gdata = df1.groupby(['商品名', '地区', '适应症']).agg(
            {'人次数': 'count', '药品总金额': 'sum', '本次赔付金额': 'sum', '1万判定': 'sum', '1.5万判定': 'sum',
             '2万判定': 'sum', '既往症人数': 'sum'}).reset_index()
        gdata.columns = ['商品名', '地区', '适应症', '人头数', '总费用', '总理赔金额', '1万以上人数', '1.5万以上人数',
                         '2万以上人数', '既往症人数']
        gdata = pd.merge(gdata, region_info, on='地区', how='left')
        gdata['使用率(1/10万)'] = (gdata['人头数']/gdata['总参保人数']).apply(lambda x: '%.2f' % (x*100000))
        gdata['成本'] = gdata['总理赔金额']/gdata['总参保人数']
        gdata['非既往症'] = gdata['非既往症'].apply(lambda x: format(x, '.0%'))
        gdata['人均自费'] = (gdata['总理赔金额']/gdata['人头数']).apply(lambda x: int(x))
        gdata['既往症'] = gdata['既往症'].apply(lambda x: format(x, '.0%'))
        gdata = gdata[['商品名', '地区', '使用率(1/10万)', '人均自费', '成本', '免赔额', '非既往症', '既往症']]
        gdata = gdata.set_index('商品名')
        st.table(gdata)
        # st.bar_chart(pd.DataFrame(gdata['发生率'].values.T, columns=gdata['地区'].tolist()))


if __name__ == '__main__':
    main()

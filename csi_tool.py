import pandas as pd
import streamlit as st

drug_utl = pd.read_excel('incidence_rate.xlsx', usecols=['商品名', '适应症', '治疗评级', '使用率'])
drug_cost = pd.read_excel('drug_cost_peryear.xlsx', usecols=['商品名', '通用名', '适应症', '人均费用'])
drug_list = []


def main():
    st.title('惠民保药品测算工具')
    cols = st.columns((1, 1))
    drug_name = cols[0].text_input("药品商品名")
    ind_list = drug_cost[drug_cost['商品名'] == drug_name]['适应症'].tolist()
    indication = cols[1].selectbox(
        "适应症:", ind_list)
    add = st.button('增加药品')

    def add_to_list(drug_name, indication):
        drug_list.append([drug_name, indication])

    if add:
        add_to_list(drug_name, indication)

    cols = st.columns(2)
    deduction = cols[0].text_input("免赔额:")
    par_rate = cols[1].slider("参保率:", 0, 100, 40)
    PMH = st.checkbox('是否包含既往症患者')
    pmh_rate = -0.0096*par_rate + 0.9457

    if PMH:
        cols = st.columns(2)
        reburse_rate_1 = cols[0].text_input("既往症患者赔付比例")
        reburse_rate_2 = cols[1].text_input("无既往症患者赔付比例")
    else:
        reburse_rate_2 = st.text_input("赔付比例")
        reburse_rate_1 = 0

    expander = st.expander("详细说明")

    def reburse_amount(amount, dedu, rb1, rb2, pmh_rate):
        if float(amount) < float(dedu):
            return 0
        else:
            return (float(amount)-float(dedu))*(float(rb1)*pmh_rate + float(rb2)*(1-pmh_rate))/100

    new_df = pd.DataFrame(drug_list, columns=['商品名', '适应症'])
    new_df = pd.merge(new_df, drug_cost, on=['商品名', '适应症'], how='left')
    new_df = pd.merge(new_df, drug_utl, on=['商品名', '适应症'], how='left')
    try:
        df = pd.concat([df, new_df])
    except:
        df = new_df
    df['赔付金额'] = df['人均费用'].apply(lambda x: reburse_amount(x, deduction, reburse_rate_1, reburse_rate_2, pmh_rate))
    df['成本'] = df['使用率'] * df['赔付金额']
    # df['使用率(1/10万)'] = df['使用率'].apply(lambda x: '%.2f' % (x*100000))
    df['成本'] = df['成本'].apply(lambda x: '%.2f' % x)
    df = df[['商品名', '通用名', '适应症', '治疗评级', '成本']]

    with expander:
        st.table(df)


if __name__ == '__main__':
    main()

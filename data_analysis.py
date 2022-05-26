import pandas as pd
import numpy as np
import random
import statsmodels.formula.api as smf
import math
import statsmodels.api as sm
import matplotlib.pyplot as plt


def data_analysis(df, city):
    data0 = df.groupby(['药品商品名', '人员编号', '诊断信息']).agg({'药品总金额': ['count', 'sum'], '本次赔付金额': 'sum'}).reset_index()
    data0.columns = ['药品名称', '个人凭证号', '诊断信息', '人次数', '发票自费总金额', '最终理赔金额']
    data0['1万判定'] = data0['发票自费总金额'].apply(lambda x: 1 if x > 10000 else 0)
    data0['2万判定'] = data0['发票自费总金额'].apply(lambda x: 1 if x > 20000 else 0)
    data0['50万判定'] = data0['最终理赔金额'].apply(lambda x: 1 if x > 500000 else 0)
    data0['100万判定'] = data0['最终理赔金额'].apply(lambda x: 1 if x > 1000000 else 0)
    gdata = data0.groupby(['药品名称', '诊断信息']).agg({'人次数': ['count', 'sum'], '发票自费总金额': 'sum', '最终理赔金额': ['sum', 'max'],
                                                 '1万判定': 'sum', '2万判定': 'sum', '50万判定': 'sum',
                                                 '100万判定': 'sum'}).reset_index()
    gdata.columns = ['药品名称', '诊断信息', '人头数', '人次数', '总费用', '总理赔金额', '最大理赔金额', '超过1万', '超过2万',
                     '超过50万', '超过100万']

    gdata['人均费用'] = gdata['总费用'] / gdata['人头数']
    gdata.to_excel('%s惠民保药品数据分析.xlsx' % city, sheet_name=city, encoding='utf-8_sig', index=False)


def sx_analysis(path, sheet_name):
    data = pd.read_excel(path, sheet_name=sheet_name, usecols=['人员编号', '药品通用名', '药品商品名', '诊断信息',
                                                               '药品总金额', '领药/发票时间', '本次赔付金额'])
    data = data.rename(columns={'人员编号': '人员编号', '药品商品名': '药品通用名', '药品通用名': '药品商品名', '药品总金额': '药品总金额',
                                '本次赔付金额': '本次赔付金额'})

    data_analysis(data, '绍兴')


def zs_analysis(path, sheet_name):
    data = pd.read_excel(path, sheet_name=sheet_name, usecols=['人员唯一号', '药品商品名' , '诊断信息',
                                                               '药品总金额_汇总', '领药/发票时间', '本次赔付金额'])
    data['诊断信息'] = data['诊断信息'].fillna('未知')
    data = data.rename(columns={'人员唯一号': '人员编号', '药品总金额_汇总': '药品总金额',})
    print(data)
    data_analysis(data, '舟山')


def sh_analysis(path, sheet_name):
    data = pd.read_excel(path, sheet_name=sheet_name, usecols=['药品名称', '购买产品名称', '参保类型', '诊断疾病名称',
                                                               '个人凭证号', '性别', '年龄', '既往症标识', '申请责任类型',
                                                               '报案日期', '结案日期', '发票自费总金额', '最终理赔金额'])
    data['既往症判定'] = data['既往症标识'].apply(lambda x: 1 if x == '既往症人群' else 0)
    gdata0 = data.groupby(['个人凭证号', '诊断疾病名称'])['药品名称'].count().reset_index()
    gdata0.columns = ['个人凭证号', '疾病名称', '次数']
    gdata0 = gdata0.sort_values(by='次数', ascending=False)
    gdata0.drop_duplicates(subset=['个人凭证号', '疾病名称'], inplace=True)
    print(gdata0)

    data = pd.merge(data, gdata0, on='个人凭证号', how='left')
    data = data.where(data.notnull(), None)
    print(data['诊断疾病名称'])

    def dn_choose(a, b):
        if a is not None:
            return a
        elif b is not None:
            return b
        else:
            return '未知'

    data['疾病诊断'] = data.apply(lambda x: dn_choose(x['诊断疾病名称'], x['疾病名称']), axis=1)
    data = data.drop_duplicates()
    data.to_excel('data1.xlsx', index=False)
    # data = data.drop('诊断疾病名称', '疾病名称')
    print(data)
    data0 = data.groupby(['药品名称', '个人凭证号', '疾病诊断']).agg({'发票自费总金额': ['count', 'sum'], '最终理赔金额': 'sum',
                                                         '既往症判定': 'max'}).reset_index()
    data0.columns = ['药品名称', '个人凭证号', '疾病诊断', '人次数', '发票自费总金额', '最终理赔金额', '既往症判定']
    data0['1万判定'] = data0['发票自费总金额'].apply(lambda x: 1 if x > 10000 else 0)
    data0['2万判定'] = data0['发票自费总金额'].apply(lambda x: 1 if x > 20000 else 0)
    data0['50万判定'] = data0['最终理赔金额'].apply(lambda x: 1 if x > 500000 else 0)
    data0['100万判定'] = data0['最终理赔金额'].apply(lambda x: 1 if x > 1000000 else 0)
    gdata_sh = data0.groupby(['药品名称', '疾病诊断']).agg({'人次数': ['count', 'sum'], '发票自费总金额': 'sum', '最终理赔金额': ['sum', 'max'],
                                                    '既往症判定': 'sum', '1万判定': 'sum', '2万判定': 'sum', '50万判定': 'sum',
                                                    '100万判定': 'sum'}).reset_index()
    gdata_sh.columns = ['药品名称', '疾病诊断', '人头数', '人次数', '总费用', '总理赔金额', '最大理赔金额', '既往症人数', '超过1万', '超过2万',
                        '超过50万', '超过100万']
    gdata_sh['既往症比例'] = (gdata_sh['既往症人数'] / gdata_sh['人头数']).apply(lambda x: '{:.2%}'.format(x))
    gdata_sh['人均费用'] = gdata_sh['总费用'] / gdata_sh['人头数']

    # gdata2 = data0.groupby(['药品名称', '既往症判定']).agg({'人次数': ['count', 'sum'], '发票自费总金额': 'sum', '最终理赔金额': ['sum', 'max'],
    #                                    '1万判定': 'sum', '2万判定': 'sum', '50万判定': 'sum', '100万判定': 'sum'}).reset_index()
    # gdata2.columns = ['药品名称', '既往症判定', '人头数', '人次数', '总费用', '总理赔金额', '最大理赔金额', '超过1万', '超过2万',
    #                     '超过50万', '超过100万']
    gdata_sh.to_excel('上海惠民保药品数据分析.xlsx', sheet_name='上海', encoding='utf-8_sig', index=False)
    # gdata2.to_excel('上海惠民保药品数据分析_gwz.xlsx', sheet_name='上海', encoding='utf-8_sig', index=False)


def hmb_analysis(path, sheet_name):
    data = pd.read_excel(path, sheet_name=sheet_name, usecols=['唯一识别号', '人员编号', '地区', '年龄', '性别', '诊断名称',
                                                               '诊断大类', '药品商品名', '药品通用名', '药品总金额',
                                                               '领药/发票时间', '本次赔付金额', '既往症标识'])
    # 使用boost映射空白诊断
    gdata_dn = data.groupby(['药品商品名', '诊断大类'])['唯一识别号'].count().reset_index()
    gdata_dn.columns = ['药品商品名', '诊断大类', '人次数']
    gdata_dn = gdata_dn[gdata_dn['诊断大类'] != '其他']
    drug_dict = {}
    for i in set(gdata_dn['药品商品名']):
        dn_list = []
        slide = gdata_dn[gdata_dn['药品商品名'] == i]
        for col, row in slide.iterrows():
            dn_list.extend([row['诊断大类']]*row['人次数'])
        drug_dict.update({i: dn_list})
        # print(drug_dict)
    # print(gdata_dn)

    data['既往症判定'] = data['既往症标识'].apply(lambda x: 1 if x == '既往症人群' else 0)
    data0 = data.groupby(['唯一识别号', '地区', '诊断大类',	'药品商品名'])['人员编号'].count().reset_index()
    data0.columns = ['唯一识别号', '地区', '诊断汇总',	'药品商品名',	'报销次数']
    data0 = data0.sort_values(by='报销次数', ascending=False)
    data0.drop_duplicates(subset=['唯一识别号', '地区', '药品商品名'], inplace=True)

    data = pd.merge(data, data0, on=['唯一识别号', '地区', '药品商品名'], how='left')
    data = data.where(data.notnull(), None)
    data = data.replace('其他', None)

    def dn_choose(a, b, c):
        if a is not None:
            return a
        elif b is not None:
            return b
        else:
            print(c)
            print(drug_dict[c])
            return random.choice(drug_dict[c])

    data['疾病诊断'] = data.apply(lambda x: dn_choose(x['诊断大类'], x['诊断汇总'], x['药品商品名']), axis=1)

    data0 = data.groupby(['唯一识别号', '地区', '疾病诊断',	'药品商品名',	'药品通用名']).agg(
        {'药品总金额': ['count', 'sum'], '本次赔付金额': 'sum', '既往症判定': 'max'}).reset_index()
    data0.columns = ['唯一识别号', '地区', '适应症',	'商品名',	'通用名', '人次数', '药品总金额', '本次赔付金额', '既往症人数']
    data0['1万判定'] = data0['药品总金额'].apply(lambda x: 1 if x > 10000 else 0)
    data0['1.5万判定'] = data0['药品总金额'].apply(lambda x: 1 if x > 15000 else 0)
    data0['2万判定'] = data0['药品总金额'].apply(lambda x: 1 if x > 20000 else 0)
    data0.to_csv('./base_data/full_data.csv', index=False,encoding='utf-8_sig')
    data_r = pd.read_excel('Z:\\工作\\其他政保业务\\惠民保数据分析\\base_data\\地区信息.xlsx')
    data_r.to_csv('./base_data/region_info.csv', index=False, encoding='utf-8_sig')
    gdata = data0.groupby(['商品名', '地区', '适应症']).agg(
        {'人次数': ['count', 'sum'], '药品总金额': 'sum', '本次赔付金额': 'sum', '1万判定': 'sum', '1.5万判定': 'sum',
         '2万判定': 'sum', '既往症人数': 'sum'}).reset_index()
    gdata.columns = ['商品名', '地区', '适应症', '人头数', '人次数', '总费用', '总理赔金额', '1万以上人数', '1.5万以上人数',
                     '2万以上人数', '既往症人数']
    gdata['人均费用'] = gdata['总费用'] / gdata['人头数']
    print(gdata)
    gdata.to_excel('惠民保药品数据分析.xlsx', encoding='utf-8_sig', index=False)


def deduction_model():
    # raw_data = pd.read_csv('./base_data/full_data.csv')
    # raw_data['5000判定'] = raw_data['药品总金额'].apply(lambda x: 1 if x > 5000 else 0)
    # gdata = raw_data.groupby(['商品名','地区']).agg(
    #     {'人次数': ['count', 'sum'], '药品总金额': 'sum', '5000判定': 'sum', '1万判定': 'sum', '1.5万判定': 'sum',
    #      '2万判定': 'sum'}).reset_index()
    # gdata.columns = ['商品名', '地区', '人头数', '人次数', '总费用','5000判定', '1万以上人数', '1.5万以上人数',
    #                  '2万以上人数']
    # gdata['人均费用'] = gdata['总费用'] / gdata['人头数']
    # gdata.to_csv('免赔额拟合.csv')
    data = pd.read_excel('./base_data/ded_data.xlsx')

    model = smf.ols(formula='np.exp(y)~x1+x2', data=data)
    results = model.fit()

    # 输出回归分析的结果
    print(results.summary())
    print('Parameters: ', results.params)
    print('R2: ', results.rsquared)
    # 结果
    # Parameters: Intercept -1.323613 -1.774 -0.873
    # np.log(x1) 0.216927 0.176 0.258 x1:药品年花费
    # x2 -0.130992 0.189 -0.073 x2:免赔额
    # R2: 0.7308400514572215
    # f(x) = min(0, -1.593702+LN(年花费)*0.248276+-0.170290*免赔额）


def incidence():
    data = pd.read_excel('惠民保药品数据分析.xlsx')
    data =data[data['总费用'] != 0]
    region_info = pd.read_csv('./base_data/region_info.csv', usecols=['地区', '总参保人数', '免赔额', '参保率'])
    print(data)
    gdata1 = data.groupby(['商品名', '适应症', '地区']).agg({'人头数': 'sum'}).reset_index()
    gdata1.columns = ['商品名', '适应症', '地区', '人数']

    gdata2 = data.groupby(['商品名', '适应症']).agg({'人头数': 'sum', '总费用': 'sum'}).reset_index()
    gdata2.columns = ['商品名', '适应症', '人数', '总费用']
    gdata2['人均总费用'] = gdata2['总费用']/gdata2['人数']
    print()

    gdata1 = pd.merge(gdata1, region_info, on='地区', how='left')
    gdata1 = pd.merge(gdata1, gdata2[['商品名', '适应症', '人均总费用']], on=['商品名', '适应症'], how='left')

    def shanghai_motify(x1, x2):
        if x1 == '上海':
            return x2/288*365
        elif x1 == '淄博':
            return x2*2
        else:
            return x2


    def qifuxian(x1, x2):
        # return min(1, -1.593702+np.log(x1)*0.248276+-0.170290*x2)
        return min(1, math.exp(-0.9475*x2/x1+0.1394))

    def canbao(x1, x2):
        return x1/(-1.1299*x2+1.652)
    gdata1['人数'] = gdata1.apply(lambda x: shanghai_motify(x['地区'], x['人数']), axis=1)
    gdata1['拟合使用率'] = gdata1.apply(lambda x: qifuxian(x['人均总费用'], x['免赔额']), axis=1)
    gdata1['拟合后使用率'] = gdata1['人数']/(gdata1['拟合使用率']*gdata1['总参保人数'])
    gdata1['拟合后使用率'] = gdata1.apply(lambda x: canbao(x['拟合后使用率'], x['参保率']), axis=1)
    print(gdata1)

    gdata3 = gdata1.groupby(['商品名', '适应症'])['拟合后使用率'].mean().reset_index()
    gdata3.columns = ['商品名',	'适应症', '使用率']
    treat_level = pd.read_csv('./base_data/incidence_rate.csv', usecols=['商品名', '适应症', '治疗评级'])
    gdata3 =pd.merge(gdata3, treat_level, on =['商品名', '适应症'], how='left')

    writer = pd.ExcelWriter('使用率测算.xlsx', engine='xlsxwriter')
    gdata1.to_excel(writer, sheet_name='按地区汇总', index=False, encoding='utf-8_sig')
    gdata3.to_excel(writer, sheet_name='汇总', encoding='utf-8_sig')
    writer.save()

    gdata3.to_csv('./base_data/incidence_rate.csv', index=False)


if __name__ == '__main__':
    # sh_analysis('Z:\\工作\\数据\\惠民保数据\\上海\\纯药品理赔明细\\理赔明细层信息统计_特药责任.xlsx', '结算明细数据')
    # hmb_analysis('Z:\\工作\\数据\\惠民保数据\\惠民保数据汇总.xlsx', '汇总表')
    # deduction_model()
    incidence()
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from hydralit import HydraHeadApp
from PIL import Image


# create a wrapper class
class modelexplainApp(HydraHeadApp):

    def run(self):
        plt.rcParams["font.sans-serif"] = ["SimHei"]  # 设置字体
        st.write('影响药品成本的因素包括，药品的理论使用率、免赔额、参保率、药品的人均医疗费用。同种药品治疗同种疾病，会参照相同的用法用量，因而年均花费比较相似。药品成本的的基本公式为：')
        st.latex(r'''
                药品成本 = 预计人均赔付金额*药品使用率
                        = (人均医疗费用-免赔额）*报销比例*药品理论使用率*参保率调整因子*免赔额/既往症调整因子''')
        st.markdown('')
        ce, c1, ce, c2, ce, c3, ce = st.columns([0.07, 1, 0.07, 1, 0.07, 1, 0.07])
        st.markdown("""
        <style>
        .label-font {
            font-size:22px !important; 
        }
        </style>
        """, unsafe_allow_html=True)
        st.markdown("""
        <style>
        .sublabel-font {
            font-size:18px !important; 
        }
        </style>
        """, unsafe_allow_html=True)
        with c1:
            st.markdown('<p class="label-font">*药品基础使用率*</p>', unsafe_allow_html=True)
            st.write('药品基础使用率的来源为历史数据和理论推演两种模式: '
                     '如果历史数据中包含了对应的药品及适应症，则采用历史数据中的基础使用率如历史数据中无对应药品，'
                     '但有对应适应症，则采用同种适应症的基础使用率，结合药品在适应中治疗评级确定药品的使用率。对应的流程关系如下：')
            image = Image.open('resources/utl_rate.png')
            st.image(image)
        with c2:
            st.markdown('<p class="label-font">*免赔额/既往症 -药品使用率*</p>', unsafe_allow_html=True)
            st.write('免赔额和既往症会影响药品的使用率，依托上海数据，构建了既往症和免赔额对于使用率的影响模型。'
                     '模型中的影响因子包含：药品的年均费用、免赔额、是否为既往症（虚拟变量）。')
            st.write('拟合后调整因子和免赔额的关系图如下（R-square 0.82)：')
            # st.latex(r'''
            #         免赔额调整因子 = min(1, e^{(-0.9475*免赔额/年均费用+0.1394)})''')
            x = np.linspace(0, 20000, num=10)
            y2 = np.exp(-0.9475*x/20000+0.1394)
            y3 = np.exp(-0.9475*x/30000+0.1394)
            y4 = np.exp(-0.9475*x/40000+0.1394)
            fig, ax = plt.subplots()
            ax.plot(x, y2, label='年均花费2万元')
            ax.plot(x, y3, label='年均花费3万元')
            ax.plot(x, y4, label='年均花费4万元')
            ax.set(xlim=(0, 20000), xlabel='免赔额',
                   ylim=(0.6, 1), ylabel='调整因子')
            plt.legend(loc='lower left')
            st.pyplot(fig)

            st.markdown('')
            st.markdown('<p class="sublabel-font">优化方向：</p>', unsafe_allow_html=True)
            st.write('目前不既往症的项目样本数据较少（仅有淄博一个地区）。因而对于既往症对于使用率的模型构建尚不完善。'
                     '需要更多的样本数据予以分析和补充。')
        with c3:
            st.markdown('<p class="label-font">*参保率-药品使用率*</p>', unsafe_allow_html=True)
            st.write('由于高风险人群更倾向于投保，所以在参保率低时的药品使用率会高于参保率较高时的药品使用率。'
                     '这种参保人群的风险成本除以全人群平均风险成本所得到的倍数定义为参保率调整因子。')
            st.write('拟合后调整因子和参保率的关系图如下（R-square 0.43)：')
            # st.latex(r'''
            #         参保率调整因子 = -0.626*ln(参保率) + 0.6168''')

            x = np.linspace(0.01, 1, num=99)
            y = -0.626*np.log(x) + 0.6168
            fig, ax = plt.subplots()
            ax.plot(x, y)
            ax.set(xlim=(0, 1), xlabel='参保率',
                   ylim=(0, 4), ylabel='调整因子')
            st.pyplot(fig)


            # st.subheader('参保率-药品使用率模型')

import pandas as pd
import streamlit as st
import altair as alt
from libs.fetcher import *
from libs.utils import *

st.title('Montana Covid-19 Model Comparison')

mod_var = st.sidebar.selectbox(
    label = 'Choose Variable',
    options = ['Hospitalizations'],
    index = 0
)

if mod_var == 'Hospitalizations':
    ihme = IhmeData().get_allbed()
    can = CanData().get_allbed()
    chime = ChimeData().get_allbed()

df = ihme.merge(
    can, 
    how='outer', 
    left_index=True, 
    right_index=True
    ).merge(
        chime, 
        how='outer', 
        left_index=True, 
        right_index=True
        )
df = df.interpolate(method='polynomial', order=3)
df_stats = calc_stats(df)

if st.checkbox('Show Statistics'):
    st.write(df_stats)

# Chart
df_melt = df.copy()

df_melt['Date'] = df_melt.index
df_melt = pd.melt(
    df_melt,
    id_vars='Date',
    var_name='Model',
    value_name='Hospitalizations'
)

chart = alt.Chart(df_melt).mark_line().encode(
        x='Date',
        y='Hospitalizations',
        color='Model',
        tooltip=['Date', 'Model','Hospitalizations']
    ).interactive()

st.altair_chart(chart, use_container_width=True)

st.markdown(
    """
    ### Models

    - **can_1:** CovidActNow - strict social distancing

    - **can_3:** CovidActNow - lax social distancing

    - **chime:** COVID-19 Hospital Impact Model for Epidemics

    - **ihme_lower:** UW Institute for Health Metrics and Evaluation - lower estimate

    - **ihme_mean:** UW Institute for Health Metrics and Evaluation - mean estimate
    
    - **ihme_upper:** UW Institute for Health Metrics and Evaluation - upper estimate

    ### CHIME parameters used
    - pop = 1050493

    - hosp market share = 90

    - current hosp patients = 31

    - 2020/03/13

    - social distance reduction = 30%

    - hosp % = 8.6

    - ICU % = 1.41

    - Ventilated % = 0.7052

    - Infectious days = 14

    - avg hosp sta = 10

    - avg days in ice = 9

    - days on vent = 10

    """
)

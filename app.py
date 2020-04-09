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
    umcphr = UmCphrData().get_allbed()

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
        # .merge(
        #     umcphr,
        #     how='outer',
        #     left_index=True,
        #     right_index=True
        #     )
df = df.interpolate(method='polynomial', order=3)
df.bfill(0, inplace=True)
df = df[(df.index >= '2020-03-10') & (df.index <= '2020-07-10')]
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

highlight = alt.selection(type='single', on='mouseover',
                          fields=['Model'], nearest=True)

# chart = alt.Chart(df_melt).mark_line().encode(
#         x='Date',
#         y='Hospitalizations',
#         # color='Model',
#         color=alt.condition(highlight, 'Model', alt.value("lightgray")),
#         # tooltip=['Date', 'Model','Hospitalizations']
#     ).add_selection(highlight)

# st.altair_chart(chart, use_container_width=True)

base = alt.Chart(df_melt).encode(
    x='Date:T',
    y='Hospitalizations:Q',
    color='Model:N',
    tooltip = ['Date', 'Model','Hospitalizations']
)

points = base.mark_circle().encode(
    opacity=alt.value(0)
).properties(width=600).add_selection(highlight).interactive()

lines = base.mark_line().encode(
    size=alt.condition(~highlight, alt.value(1), alt.value(3))
)

final = alt.layer(points, lines)

st.altair_chart(final, use_container_width=True)

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
    - pop = 1,050,493

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

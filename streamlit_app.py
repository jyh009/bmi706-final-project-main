import altair as alt
import pandas as pd


df = pd.read_csv('Medicare_Hospital_Spending_Per_Patient-Hospital.csv')


selected_states = ['MA', 'NY']
selected_hospitals = ['BOSTON MEDICAL CENTER', 'MASSACHUSETTS GENERAL HOSPITAL', 'CAMBRIDGE HEALTH ALLIANCE']

colors = ['red', 'green', 'blue']  
hospital_to_color = {hospital: color for hospital, color in zip(selected_hospitals, colors)}

df_filtered = df[df['State'].isin(selected_states)]

base = alt.Chart(df_filtered).encode(
    y=alt.Y('Score:Q', axis=alt.Axis(labels=False)),
    x=alt.X('Facility Name:N', axis=alt.Axis(title='Hospitals', labels=False), sort=None),  
    tooltip=['Facility Name', 'Score']
)


box_plot = base.mark_boxplot().encode(
    color=alt.value('lightgray'),
    opacity=alt.value(0.5)
)


dots = base.mark_circle(size=10).encode(  
    color=alt.Color('Color:N', legend=None),
    opacity=alt.value(1)
)


final_chart = (box_plot + dots).facet(
    column='State:N'
)

final_chart
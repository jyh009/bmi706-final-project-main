import altair as alt
import pandas as pd


df = pd.read_csv('Medicare_Hospital_Spending_Per_Patient-Hospital.csv')


selected_states = ['MA', 'NY']
selected_hospitals = ['BOSTON MEDICAL CENTER', 'MASSACHUSETTS GENERAL HOSPITAL', 'CAMBRIDGE HEALTH ALLIANCE']

colors = ['red', 'green', 'blue']
hospital_to_color = {hospital: color for hospital, color in zip(selected_hospitals, colors)}


def apply_color(row):
    return hospital_to_color.get(row['Facility Name'], 'black')

df['Color'] = df.apply(apply_color, axis=1)


df_filtered = df[df['State'].isin(selected_states)].copy() 
df_filtered['Score'] = pd.to_numeric(df_filtered['Score'], errors='coerce')



base = alt.Chart(df_filtered).encode(
    y='Score:Q',
    x='Facility Name:N',
    color='Color:N',
    tooltip=['Facility Name', 'Score']
).properties(
    width=450
)

dots = base.mark_circle(size=60).encode(
    opacity=alt.value(1)
)

final_chart = dots.facet(
    column='State:N',
    header=alt.Header(
        labelOrient='bottom',
        titleOrient='bottom'
    ),
    spacing=5
).transform_window(
    rank='rank(Score)',
    sort=[alt.SortField('Score', order='descending')]
)

final_chart
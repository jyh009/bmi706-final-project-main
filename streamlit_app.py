import altair as alt
import pandas as pd

### Task 1 : Medicare beneficiary spending per state and hospital 
df = pd.read_csv('Medicare_Hospital_Spending_Per_Patient-Hospital.csv')

selected_states = ['MA', 'NY']
selected_hospitals = ['BOSTON MEDICAL CENTER', 'MASSACHUSETTS GENERAL HOSPITAL', 'CAMBRIDGE HEALTH ALLIANCE']

#hard coded color for selected hospitals
colors = ['purple', 'green', 'blue']
light_gray_scale = alt.Scale(domain=['purple', 'green', 'blue', '#D3D3D3'], range=['purple', 'green', 'blue', '#D3D3D3'])

hospital_to_color = {hospital: color for hospital, color in zip(selected_hospitals, colors)}

#helper function to map hospital to either the special 3 colors or default (grey)
def apply_color(row):
    if row['Facility Name'] in hospital_to_color: 
        return hospital_to_color[row['Facility Name']]  
    else:
        return "#D3D3D3" 

#set color property for each hospital
df['Color'] = df.apply(apply_color, axis=1)


df_filtered = df[df['State'].isin(selected_states)].copy()
df_filtered['Score'] = pd.to_numeric(df_filtered['Score'], errors='coerce')
df_sorted = df_filtered.groupby('State').apply(lambda x: x.sort_values(by='Score', ascending=False)).reset_index(drop=True)

#create facility name vs Medicare Spending per Beneficiary scatterplot
base = alt.Chart(df_sorted).encode(
    y=alt.Y('Score:Q', axis=alt.Axis(title='Medicare Spending per Beneficiary'), scale=alt.Scale(domain=[0.6, 1.4])),
    x=alt.X('Facility Name:N', axis=alt.Axis(title='Hospitals', labels=False), sort='-y'),  
    tooltip=['Facility Name', 'Score']
).properties(
    width=550
)

dots = base.mark_circle().encode(
    color=alt.Color('Color:N', scale=light_gray_scale, legend=None),
    opacity=alt.value(1),
    order=alt.Order('Score:Q', sort='descending')
)

final_chart = dots.facet(
    column=alt.Column('State:N', header=alt.Header(labelOrient='bottom', titleOrient='bottom')),
    spacing=40
).configure_axis(
    labelFontSize=12,  
    titleFontSize=14
)

final_chart

### Task 3 - Payment per disease associated with complication rate 

complications_deaths_df = pd.read_csv('Complications_and_Deaths-Hospital.csv')
payment_value_care_df = pd.read_csv('Payment_and_Value_of_Care-Hospital.csv')
filtered_measures = [
    "Rate of complications for hip/knee replacement patients",
    "Death rate for heart attack patients",
    "Death rate for heart failure patients",
    "Death rate for pneumonia patients"
]
complications_deaths_filtered_df = complications_deaths_df[
    complications_deaths_df['Measure Name'].isin(filtered_measures)
]

#for each health condition (e.g. pnuemonia), mapping complication/death rate to appropriate payment measure
measure_name_mapping = {
    "Rate of complications for hip/knee replacement patients": "Payment for hip/knee replacement patients",
    "Death rate for heart attack patients": "Payment for heart attack patients",
    "Death rate for heart failure patients": "Payment for heart failure patients",
    "Death rate for pneumonia patients": "Payment for pneumonia patients"
}
complications_deaths_filtered_df['Payment Measure Name'] = complications_deaths_filtered_df['Measure Name'].map(measure_name_mapping)

#stringify facility IDs
complications_deaths_filtered_df['Facility ID'] = complications_deaths_filtered_df['Facility ID'].astype(str)
payment_value_care_df['Facility ID'] = payment_value_care_df['Facility ID'].astype(str)

# remove facilities that are listed as NA
complications_deaths_filtered_df.dropna(subset=['Facility Name'], inplace=True)
payment_value_care_df.dropna(subset=['Facility Name'], inplace=True)

#remove whitespace for facility name strings
complications_deaths_filtered_df['Facility Name'] = complications_deaths_filtered_df['Facility Name'].str.strip()
payment_value_care_df['Facility Name'] = payment_value_care_df['Facility Name'].str.strip()

#merge complications/death data frame with payment data frame
merged_df = complications_deaths_filtered_df.merge(
    payment_value_care_df,
    how='inner',
    left_on=['Facility ID', 'Payment Measure Name'],
    right_on=['Facility ID', 'Payment Measure Name']
)
print (complications_deaths_filtered_df.head())

#clean up column names in merged data set
merged_df.drop(['State_y'], axis=1, inplace=True)
merged_df.rename(columns={'State_x': 'State'}, inplace=True)

merged_df.drop(['Facility Name_y'], axis=1, inplace=True)
merged_df.rename(columns={'Facility Name_x': 'Facility Name'}, inplace=True)


#export merged dataset
merged_df.to_csv('merged_df_corrected.csv', index=False)

#subset the merged dataset to only 3 states that have been selected by user
filtered_df2 = merged_df[merged_df['State'].isin(selected_states)]

#remove any facilities with payment or scores that are NA
filtered_df2 = filtered_df2.dropna(subset=['Score', 'Payment'])

#convert payments and score to numeric type
filtered_df2['Payment'] = pd.to_numeric(filtered_df2['Payment'].str.replace('[\$,]', '', regex=True), errors='coerce')

filtered_df2['Score'] = pd.to_numeric(filtered_df2['Score'], errors='coerce')


#map hospitals to 3 colors
colors = ['red', 'green', 'blue'] 
hospital_to_color = {hospital: color for hospital, color in zip(selected_hospitals, colors)}
hospital_colors = alt.Scale(domain=['red', 'green', 'blue', 'lightgrey'], range=['red', 'green', 'blue', 'lightgray'])
filtered_df2['Color'] = filtered_df2['Facility Name'].map(hospital_to_color).fillna('lightgrey')

filtered_df2.to_csv('filtered.csv', index=False)



scatter_plots = []
measure_titles = {
    "Rate of complications for hip/knee replacement patients": "Hip/Knee Replacement",
    "Death rate for heart attack patients": "Heart Attack",
    "Death rate for heart failure patients": "Heart Failure", 
    "Death rate for pneumonia patients": "Pneumonia"
}

#create scatterplots for each state

for state in selected_states:
    for measure in filtered_measures:
        df_state_measure = filtered_df2[
            (filtered_df2['State'] == state) & 
            (filtered_df2['Measure Name'] == measure)
        ]
        
        
        max_payment = df_state_measure['Payment'].max()
        y_scale = alt.Scale(domain=(0, max_payment * 1.2))  
        
        scatter_plot = alt.Chart(df_state_measure).mark_point(filled=True, size=60).encode(
            x=alt.X('Score:Q', axis=alt.Axis(title='Complications')),
            y=alt.Y('Payment:Q', axis=alt.Axis(title='Payment ($)'), scale=y_scale),
            color=alt.Color('Color:N', scale=hospital_colors, legend=None),
            tooltip=['Facility Name:N', 'Score:Q', 'Payment:Q']
        ).properties(
            title=f"{state} - {measure_titles[measure]}",
            width=200,
            height=200  
        )
        
        scatter_plots.append(scatter_plot)


h_spacing = 50 
v_spacing = 100 

grid_chart = alt.vconcat(
    *[
        alt.hconcat(
            *scatter_plots[i:i + len(filtered_measures)], 
            spacing=h_spacing
        ) 
        for i in range(0, len(scatter_plots), len(filtered_measures))
    ],
    spacing=v_spacing
)


grid_chart

## Task 4 - plot hospital rating to Medicare spending 
hospital_info_df = pd.read_csv('Hospital_General_Information.csv')
medicare_spending_copy_df = pd.read_csv('Medicare_Hospital_Spending_Per_Patient-Hospital.csv')

#clean up hospital info and medicare spending tables before merging
hospital_info_df['Facility ID'] = hospital_info_df['Facility ID'].astype(str)
medicare_spending_copy_df['Facility ID'] = medicare_spending_copy_df['Facility ID'].astype(str)
medicare_spending_copy_df.dropna(subset=['Facility Name'], inplace=True)
hospital_info_df.dropna(subset=['Facility Name'], inplace=True)
merged_hospital_info_spending_df = medicare_spending_copy_df.merge(
    hospital_info_df,
    how='inner',
    left_on=['Facility ID'],
    right_on=['Facility ID']
)

#After merging, ensure that any hospitals with spending or ratings that are NA are rmeoved, and relabel facility name column
merged_hospital_info_spending_df.dropna(subset=['Hospital overall rating', 'Score'])
merged_hospital_info_spending_df['Score'] = pd.to_numeric(merged_hospital_info_spending_df['Score'].str.replace('[\$,]', '', regex=True), errors='coerce')
merged_hospital_info_spending_df.rename(columns={'Facility Name_x': 'Facility Name'}, inplace=True)
merged_hospital_info_spending_df.rename(columns={'State_x': 'State'}, inplace=True)

filtered_merged_hospital_info_spending_df = merged_hospital_info_spending_df[merged_hospital_info_spending_df['State'].isin(selected_states)]

#create boxplot only
rating_base = alt.Chart(filtered_merged_hospital_info_spending_df)

rating_boxplot = rating_base.mark_boxplot(extent='min-max').encode(
    x=alt.X('Hospital overall rating:N'),
    y=alt.Y('Score:Q', axis=alt.Axis(title='Medicare Spending per Beneficiary'), scale=alt.Scale(domain=[0.4,1.4]))
).properties(
    width=550,
    title="Hospital Rating versus Medicare Spending"
)

rating_jitter = rating_base.mark_circle(size=8).encode(
    x=alt.X('Hospital overall rating:N'),
    y=alt.Y('Score:Q', scale=alt.Scale(domain=[0.4,1.4])),
    yOffset="jitter:Q",
    color=alt.Color('Hospital overall rating:N').legend(None)
).transform_calculate(
    jitter='random()'
)

### To do - add state by state display and superimpose 3 hospitals



rating_boxplot + rating_jitter

print('Hospital Rating')
print(filtered_merged_hospital_info_spending_df.head())



## source: https://altair-viz.github.io/gallery/strip_plot_jitter.html
# https://stackoverflow.com/questions/62281179/how-to-adjust-scale-ranges-in-altair

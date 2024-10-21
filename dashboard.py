import streamlit as st
import pandas as pd
import plotly.express as px

# Load the data
data_2024 = pd.read_csv('predictions.csv')
full_data = pd.read_csv('data.csv')

# Define pitch type categories
fastballs = ['FF', 'FC', 'FA', 'SI']
breaking_balls = ['CU', 'KC', 'SL', 'ST', 'SV', 'SC', 'CS']
off_speed = ['CH', 'FS', 'FO', 'KN', 'EP']
full_data['PITCH_CATEGORY'] = full_data['PITCH_TYPE'].apply(lambda x: 'FB' if x in fastballs else
                                                            ('BB' if x in breaking_balls else
                                                             ('OS' if x in off_speed else 'Other')))

# Filter out rows where the pitch is not categorized (Other)
full_data = full_data[full_data['PITCH_CATEGORY'] != 'Other']

# Dashboard Title
st.title("2024 MLB Batter Pitch Mix Predictions and Analysis")

# Sidebar for user selection
st.sidebar.header("Player Selection")
player_name = st.sidebar.selectbox("Select Player", data_2024["PLAYER_NAME"].unique())

# Filter the data for the selected player in 2024 predictions
player_data_2024 = data_2024[data_2024["PLAYER_NAME"] == player_name]

# Filter the full dataset for more context on the selected player (2021-2023)
player_data_full = full_data[full_data["PLAYER_NAME"] == player_name]

# Display selected player
st.subheader(f"Pitch Mix Predictions for {player_name} (2024)")

# Display the predicted pitch mix (Fastball, Breaking Ball, Off-Speed)
pitch_data = player_data_2024[['PITCH_TYPE_FB', 'PITCH_TYPE_BB', 'PITCH_TYPE_OS']].mean()
fig = px.pie(values=pitch_data, names=['Fastball', 'Breaking Ball', 'Off-Speed'],
             title=f"Predicted Pitch Mix for {player_name}")
st.plotly_chart(fig)

# Dropdown for selecting pitch category
st.sidebar.header("Pitch Type Selection")
pitch_type = st.sidebar.selectbox("Select Pitch Type", ["Fastball (FB)", "Breaking Ball (BB)", "Off-Speed (OS)"])

# Map the selected pitch type to the internal category
pitch_mapping = {
    "Fastball (FB)": "FB",
    "Breaking Ball (BB)": "BB",
    "Off-Speed (OS)": "OS"
}
selected_pitch_category = pitch_mapping[pitch_type]

# Filter player data by the selected pitch category
filtered_data = player_data_full[player_data_full['PITCH_CATEGORY'] == selected_pitch_category]

#Launch Speed and Angle by Selected Pitch Category
st.subheader(f"Launch Speed and Angle for {player_name} - {pitch_type} (2021-2023)")
fig_launch = px.scatter(filtered_data, x="LAUNCH_SPEED", y="LAUNCH_ANGLE",
                        title=f"Launch Speed vs. Launch Angle for {player_name} ({pitch_type})",
                        labels={'LAUNCH_SPEED': 'Exit Velocity (mph)', 'LAUNCH_ANGLE': 'Launch Angle (°)'})
st.plotly_chart(fig_launch)

# Average wOBA by Pitch Category and Year
st.subheader(f"Average wOBA for {player_name} - {pitch_type} (2021-2023)")
# Group by year and pitch category,
woba_by_year = filtered_data.groupby(['GAME_YEAR', 'PITCH_CATEGORY']).agg(
    avg_woba=('ESTIMATED_WOBA_USING_SPEEDANGLE', 'mean')).reset_index()
fig_woba = px.line(woba_by_year, x="GAME_YEAR", y="avg_woba", color="PITCH_CATEGORY",
                   title=f"Average wOBA by Year for {player_name} - {pitch_type}",
                   labels={'avg_woba': 'Estimated wOBA', 'GAME_YEAR': 'Year'})
fig_woba.update_xaxes(tickmode='linear', tick0=2021, dtick=1)
st.plotly_chart(fig_woba)

# Summary Table for the selected pitch category
st.subheader(f"Summary Stats for {player_name} - {pitch_type} (2021-2023)")
# Aggregate data by year and pitch category
summary_data = filtered_data.groupby(['GAME_YEAR', 'PITCH_CATEGORY']).agg(
    avg_launch_speed=('LAUNCH_SPEED', 'mean'),
    avg_launch_angle=('LAUNCH_ANGLE', 'mean'),
    avg_woba=('ESTIMATED_WOBA_USING_SPEEDANGLE', 'mean'),
    delta_run_exp=('DELTA_RUN_EXP', 'sum')).reset_index()

st.write(summary_data)

# Heatmap for Pitch Locations by Pitch Category
st.subheader(f"Pitch Location Heatmap for {player_name} - {pitch_type} (2021-2023)")

# Create a hexbin plot for pitch locations
fig_heatmap = px.density_heatmap(filtered_data, x='PLATE_X', y='PLATE_Z',
                                 title=f"Pitch Location Heatmap for {player_name} - {pitch_type}",
                                 nbinsx=12, nbinsy=12, color_continuous_scale='reds',
                                 labels={'PLATE_X': 'Horizontal Location', 'PLATE_Z': 'Vertical Location'})

# Add the strike zone
strike_zone_top = filtered_data['SZ_TOP'].mean()
strike_zone_bot = filtered_data['SZ_BOT'].mean()
fig_heatmap.add_shape(type="rect", x0=-0.83, x1=0.83, y0=strike_zone_bot, y1=strike_zone_top,
                      line=dict(color="Red", width=2))

st.plotly_chart(fig_heatmap)

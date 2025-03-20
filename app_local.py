import streamlit as st
import pandas as pd

krakow_table_path = "data/silver/krakow/krakow_silver_data.csv"  # Adjust to your path
df_krakow = pd.read_csv(krakow_table_path)

gdansk_table_path = "data/silver/gdansk/gdansk_silver_data.csv"  # Adjust to your path
df_gdansk = pd.read_csv(gdansk_table_path)

poznan_table_path = "data/silver/poznan/poznan_silver_data.csv"  # Adjust to your path
df_poznan = pd.read_csv(poznan_table_path)

wroclaw_table_path = "data/silver/wroclaw/wroclaw_silver_data.csv"  # Adjust to your path
df_wroclaw = pd.read_csv(wroclaw_table_path)

warsaw_table_path = "data/silver/warsaw/warsaw_silver_data.csv"  # Adjust to your path
df_warsaw = pd.read_csv(warsaw_table_path)

slask_table_path = "data/silver/slask/slask_silver_data.csv"  # Adjust to your path
df_slask = pd.read_csv(slask_table_path)

# Create a dictionary to map cities to their respective DataFrames
city_dataframes = {
    "Kraków": df_krakow,
    "Gdańsk": df_gdansk,
    "Poznań": df_poznan,
    "Wrocław": df_wroclaw,
    "Warszawa": df_warsaw,
    "Śląsk": df_slask
}

# Streamlit App
def app():    
        
    st.title("Liga MT - Sezon Zimowy")
    st.header("by Stephen Barrie")

    # Sidebar Filters
    selected_city = st.sidebar.selectbox("Wybierz miasto", sorted(city_dataframes.keys()))
    selected_age = st.sidebar.selectbox("Wybierz kategorię wiekową", sorted(city_dataframes[selected_city]["category"].unique()))    
    # Filter Data
    filtered_df = city_dataframes[selected_city][
        #(city_dataframes[selected_city]["city"] == selected_city) & 
        (city_dataframes[selected_city]["category"] == selected_age)
    ]

    # Combine team names from home_team and away_team columns
    all_teams = pd.unique(filtered_df[["home_team", "away_team"]].values.ravel("K"))

    # Add "All Teams" option to the list of teams
    all_teams = ["Wszystkie Drużyny"] + sorted(all_teams)

    # Add team search to the sidebar
    selected_team = st.sidebar.selectbox("Wybierz nazwę zespołu", all_teams)

     # Filter data based on selected team
    if selected_team == "Wszystkie Drużyny":
        team_filtered_df = filtered_df  # Show all matches for the selected age category
    else:
        team_filtered_df = filtered_df[
            (filtered_df["home_team"] == selected_team) | 
            (filtered_df["away_team"] == selected_team)
        ]
       
    # Display League Table or Match Results
    view_option = st.radio("Wybierz Widok:", ["Tabela Ligowa", "Wyniki Meczu"])

    if view_option == "Tabela Ligowa":
        # Calculate home team standings
     
        home_standings = filtered_df.groupby("home_team").agg(
            Mecze=("home_team", "count"),
            Zwycięstwa=("home_goals", lambda x: (x > filtered_df.loc[x.index, "away_goals"]).sum()),
            Przegrane=("home_goals", lambda x: (x < filtered_df.loc[x.index, "away_goals"]).sum()),
            Remisy=("home_goals", lambda x: (x == filtered_df.loc[x.index, "away_goals"]).sum()),
            Strzelone_Bramki =("home_goals", "sum"),
            Stracone_Bramki=("away_goals", "sum")
        ).reset_index().rename(columns={"home_team": "Drużyna"})
        
        # Calculate away team standings
        away_standings = filtered_df.groupby("away_team").agg(
            Mecze=("away_team", "count"),
            Zwycięstwa=("away_goals", lambda x: (x > filtered_df.loc[x.index, "home_goals"]).sum()),
            Przegrane=("away_goals", lambda x: (x < filtered_df.loc[x.index, "home_goals"]).sum()),
            Remisy=("away_goals", lambda x: (x == filtered_df.loc[x.index, "home_goals"]).sum()),
            Strzelone_Bramki=("away_goals", "sum"),
            Stracone_Bramki=("home_goals", "sum")
        ).reset_index().rename(columns={"away_team": "Drużyna"})

        # Combine home and away standings
        league_table = pd.concat([home_standings, away_standings]).groupby("Drużyna").agg(
            Mecze=("Mecze", "sum"),
            Zwycięstwa=("Zwycięstwa", "sum"),
            Remisy=("Remisy", "sum"),
            Przegrane=("Przegrane", "sum"),
            Strzelone_Bramki=("Strzelone_Bramki", "sum"),
            Stracone_Bramki=("Stracone_Bramki", "sum")
        ).reset_index()

        league_table["Różnica_Bramek"] = league_table["Strzelone_Bramki"] - league_table["Stracone_Bramki"]
        league_table["Punkty"] = league_table["Zwycięstwa"] * 3 + league_table["Remisy"]

        # Sort the league table by Points (descending) and Goal Difference (descending)
        league_table_sorted = league_table.sort_values(by=["Punkty", "Różnica_Bramek"], ascending=[False, False])

        league_table_sorted = league_table_sorted.rename(columns={
        "Strzelone_Bramki": "Strzelone Bramki",
        "Stracone_Bramki": "Stracone Bramki",
        "Różnica_Bramek": "Różnica Bramek"       
        })
        
        # Reset the index to reflect rankings (starting from 1)
        league_table_sorted.reset_index(drop=True, inplace=True)
        league_table_sorted.index += 1  # Start rankings from 1 instead of 0

        
              
        st.dataframe(league_table_sorted)
    else:
        team_filtered_df["date"] = pd.to_datetime(team_filtered_df['date'], format="%d/%m/%Y").dt.date
        # Sort match results by date (most recent first)
        team_filtered_df_sorted = team_filtered_df[["date", "home_team", "home_goals", "away_team", "away_goals"]].sort_values(by="date", ascending=True)        

        # Reset the index to reflect the order (optional)
        team_filtered_df_sorted.reset_index(drop=True, inplace=True)
        team_filtered_df_sorted.index +=1

        team_filtered_df_sorted = team_filtered_df_sorted.rename(columns={
        "date": "Data",
        "home_team": "Drużyna Gospodarzy",
        "away_team": "Zespół Gości",
        "home_goals": "\u2003",
        "away_goals": "\u2800"
        })

        # Display the sorted match results in Streamlit
        st.dataframe(team_filtered_df_sorted)

# Run the Streamlit app
if __name__ == "__main__":
    app()
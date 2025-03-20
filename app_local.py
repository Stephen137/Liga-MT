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

    st.set_page_config(layout="wide")    
        
    st.title("Liga MT - Sezon Zimowy")
    st.header("by Stephen Barrie")

    st.markdown(
    """
    <style>
    .stMarkdown table th { background-color: #00172B; color: white; }
    .stMarkdown table td { color: white; }
    </style>
    """,
    unsafe_allow_html=True,
    )

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

     # Custom CSS for alternating every three rows
        st.markdown(
            """
            <style>
            /* Alternating every tworows */
            .stMarkdown table tr:nth-child(2n+1) {         

                background-color: #2E4E6F; /* Darker blue for the first rows */
            }
            .stMarkdown table tr:nth-child(2n+2) {
          
                background-color: #1C2E4A; /* Lighter blue for the next row */
            }
            .stMarkdown table th { background-color: #00172B; color: white; }
            .stMarkdown table td { color: white; }
            </style>
            """,
            unsafe_allow_html=True,
        )
        
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

        # Highlight the selected team in dark blue
        #def highlight_team(row):
            #if row["Drużyna"] == selected_team:
                #return ['<span style="color: #2E4E6F;">{}</span>'.format(val) for val in row]
            #else:
                #return row

        # Apply highlighting to the league table
        #league_table_sorted_styled = league_table_sorted.apply(highlight_team, axis=1)

        # Display the styled league table
        st.markdown(league_table_sorted.to_html(escape=False), unsafe_allow_html=True)   
                             
        #st.dataframe(league_table_sorted, height=1000, width=1500)
        
    else:
        
        # Apply filtering, sorting, and renaming logic consistently
        team_filtered_df["date"] = pd.to_datetime(team_filtered_df['date'], format="%d/%m/%Y").dt.date
        # Sort match results by date and group
        team_filtered_df_sorted = team_filtered_df[["date", "pitch", "group", "home_team", "home_goals", "away_team", "away_goals"]].sort_values(by=["date", "group"], ascending=[True, True])        
    
        # Reset the index to reflect the order (optional)
        team_filtered_df_sorted.reset_index(drop=True, inplace=True)
        team_filtered_df_sorted.index += 1        
    
        team_filtered_df_sorted = team_filtered_df_sorted.rename(columns={
            "date": "Data",
            "pitch": "Boisko",
            "group": "Grupa",
            "home_team": "Drużyna Gospodarzy",
            "away_team": "Zespół Gości",
            "home_goals": "\u2003",
            "away_goals": "\u2800"
        })
          
        if selected_team == "Wszystkie Drużyny" and view_option == "Wyniki Meczu":
            # Function to assign a background color based on "Grupa"
            def assign_background_color(group):
                if group == "A":
                    return "background-color: #2E4E6F;"  # Darker blue for Grupa A
                elif group == "B":
                    return "background-color: #1C2E4A;"  # Lighter blue for Grupa B
                elif group == "C":
                    return "background-color: #2E4E6F;"  # Darker blue for Grupa C
                elif group == "D":
                    return "background-color: #1C2E4A;"  # Lighter blue for Grupa D
                elif group == "E":
                    return "background-color: #2E4E6F;"  # Lighter blue for Grupa D
                elif group == "F":
                    return "background-color: #1C2E4A;"  # Lighter blue for Grupa D
                elif group == "G":
                    return "background-color: #2E4E6F;"  # Lighter blue for Grupa D
                elif group == "H":
                    return "background-color: #1C2E4A;"  # Lighter blue for Grupa D
                elif group == "I":
                    return "background-color: #2E4E6F;"  # Lighter blue for Grupa D
                elif group == "J":
                    return "background-color: #1C2E4A;"  # Lighter blue for Grupa D
                elif group == "K":
                    return "background-color: #2E4E6F;"  # Lighter blue for Grupa D
                elif group == "L":
                    return "background-color: #1C2E4A;"  # Lighter blue for Grupa D
                elif group == "M":
                    return "background-color: #2E4E6F;"  # Lighter blue for Grupa D
                    
                # Add more conditions if there are more groups
                else:
                    return ""  # Default (no background color)

            # Apply the background color to each row based on "Grupa"
            team_filtered_df_sorted["style"] = team_filtered_df_sorted["Grupa"].apply(assign_background_color)    
    
             # Generate the HTML table with inline styles, excluding the "style" column
            html_table = (
                team_filtered_df_sorted
                .style
                .apply(lambda x: [x["style"]] * len(x), axis=1)  # Apply styles
                .hide(axis="columns", subset=["style"])  # Hide the "style" column
                .to_html(escape=False, index=False)
            )
    
            # Display the styled match results
            st.markdown(html_table, unsafe_allow_html=True)

        else:                                        
            # Custom CSS for alternating every three rows
            st.markdown(
                """
                <style>
                /* Alternating every three rows */
                .stMarkdown table tr:nth-child(6n+1),
                .stMarkdown table tr:nth-child(6n+2),
                .stMarkdown table tr:nth-child(6n+3) {         
    
                    background-color: #2E4E6F; /* Darker blue for the first six rows */
                }
                .stMarkdown table tr:nth-child(6n+4),
                .stMarkdown table tr:nth-child(6n+5),
                .stMarkdown table tr:nth-child(6n+6) {
              
                    background-color: #1C2E4A; /* Lighter blue for the next six rows */
                }
                .stMarkdown table th { background-color: #00172B; color: white; }
                .stMarkdown table td { color: white; }
                </style>
                """,
                unsafe_allow_html=True,
            )
                
            # Highlight the selected team in red
            #def highlight_team_match(val):
                #if val == selected_team:
                    #return f'<span style="color: #2E4E6F;">{val}</span>'
                #return val
    
            # Apply highlighting to the "Drużyna Gospodarzy" and "Zespół Gości" columns
            #team_filtered_df_sorted["Drużyna Gospodarzy"] = team_filtered_df_sorted["Drużyna Gospodarzy"].apply(highlight_team_match)
            #team_filtered_df_sorted["Zespół Gości"] = team_filtered_df_sorted["Zespół Gości"].apply(highlight_team_match)
    
           # Display the styled match results
            st.markdown(team_filtered_df_sorted.to_html(escape=False), unsafe_allow_html=True)
                  
            #st.dataframe(team_filtered_df_sorted_styled, height=600, width=500)  # Set fixed height to enable scrolling     

# Run the Streamlit app
if __name__ == "__main__":
    app()

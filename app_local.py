import streamlit as st
import pandas as pd
from datetime import datetime

# Load data for each city
city_data = {
    "Kraków": pd.read_csv("data/silver/krakow/krakow_silver_data.csv"),
    "Gdańsk": pd.read_csv("data/silver/gdansk/gdansk_silver_data.csv"),
    "Poznań": pd.read_csv("data/silver/poznan/poznan_silver_data.csv"),
    "Wrocław": pd.read_csv("data/silver/wroclaw/wroclaw_silver_data.csv"),
    "Warszawa": pd.read_csv("data/silver/warsaw/warsaw_silver_data.csv"),
    "Śląsk": pd.read_csv("data/silver/slask/slask_silver_data.csv")
}

def calculate_league_table(df):
    """Helper function to calculate league table from a dataframe"""
    home = df.groupby("home_team").agg(
        Mecze=("home_team", "count"),
        Zwycięstwa=("home_goals", lambda x: (x > df.loc[x.index, "away_goals"]).sum()),
        Przegrane=("home_goals", lambda x: (x < df.loc[x.index, "away_goals"]).sum()),
        Remisy=("home_goals", lambda x: (x == df.loc[x.index, "away_goals"]).sum()),
        Gole_Strzelone=("home_goals", "sum"),
        Gole_Stracone=("away_goals", "sum")
    ).reset_index().rename(columns={"home_team": "Drużyna"})
    
    away = df.groupby("away_team").agg(
        Mecze=("away_team", "count"),
        Zwycięstwa=("away_goals", lambda x: (x > df.loc[x.index, "home_goals"]).sum()),
        Przegrane=("away_goals", lambda x: (x < df.loc[x.index, "home_goals"]).sum()),
        Remisy=("away_goals", lambda x: (x == df.loc[x.index, "home_goals"]).sum()),
        Gole_Strzelone=("away_goals", "sum"),
        Gole_Stracone=("home_goals", "sum")
    ).reset_index().rename(columns={"away_team": "Drużyna"})

    table = pd.concat([home, away]).groupby("Drużyna").agg({
        "Mecze": "sum", 
        "Zwycięstwa": "sum", 
        "Remisy": "sum", 
        "Przegrane": "sum",
        "Gole_Strzelone": "sum", 
        "Gole_Stracone": "sum"
    }).reset_index()
    
    # Calculate goal difference and points
    table["Różnica Bramek"] = table["Gole_Strzelone"] - table["Gole_Stracone"]
    table["Punkty"] = table["Zwycięstwa"] * 3 + table["Remisy"]
    
    # Rename columns after all calculations
    table = table.rename(columns={
        "Gole_Strzelone": "Strzelone Bramki",
        "Gole_Stracone": "Stracone Bramki"
    }).sort_values(["Punkty", "Różnica Bramek"], ascending=[False, False])
    
    table.index = range(1, len(table)+1)
    return table

def main():
    # Convert dates to datetime and sort for all city data
    for city in city_data:
        city_data[city]['date'] = pd.to_datetime(city_data[city]['date'], format='%d/%m/%Y')
        city_data[city] = city_data[city].sort_values('date')

    # Custom CSS for table styling
    st.markdown("""
    <style>
    .stMarkdown table tr:nth-child(2n+1) { background-color: #2E4E6F; }
    .stMarkdown table tr:nth-child(2n+2) { background-color: #1C2E4A; }
    .stMarkdown table th { background-color: #00172B; color: white; }
    .stMarkdown table td { color: white; }
    </style>
    """, unsafe_allow_html=True)

    # App title
    st.title("Liga Młodych Talentów #ZIMA2025")
    st.header("by Stephen Barrie")

    # Sidebar filters - always visible
    selected_city = st.sidebar.selectbox("Wybierz miasto", sorted(city_data.keys()))
    df = city_data[selected_city]
    selected_age = st.sidebar.selectbox("Wybierz kategorię wiekową", sorted(df["category"].unique()))
    df = df[df["category"] == selected_age]

    # Get all teams for the selected city and age group for sidebar
    all_teams = ["Wszystkie Drużyny"] + sorted(pd.unique(df[["home_team", "away_team"]].values.ravel("K")))
    selected_team = st.sidebar.selectbox("Wybierz drużynę", all_teams)

    # Get unique match dates for selected city and age group
    unique_dates = sorted(df['date'].dt.date.unique(), reverse=True)
    if len(unique_dates) == 0:
        st.error("Brak danych dla wybranej kombinacji miasta i kategorii wiekowej")
        return

    # Main view selection - now with three options
    view_option = st.radio("Wybierz Widok:", ["Tabela Ligowa", "Tabela Dnia", "Wyniki Meczu"])

    if view_option == "Tabela Ligowa":
        # Always show the overall league table for all teams
        league_table = calculate_league_table(df)
        st.subheader(f"Tabela Ligowa - Wszystkie Drużyny")
        st.markdown(league_table.to_html(escape=False), unsafe_allow_html=True)

    elif view_option == "Tabela Dnia":
        # Date selection for daily league tables
        selected_date_str = st.selectbox(
            "Wybierz datę",
            options=[d.strftime("%d/%m/%Y") for d in unique_dates],
            index=0  # Default to most recent date
        )
        selected_date = datetime.strptime(selected_date_str, "%d/%m/%Y").date()
        
        # Filter by date
        date_df = df[df['date'].dt.date == selected_date]
        
        if selected_team == "Wszystkie Drużyny":
            # Show all groups for selected date
            groups = sorted(date_df['group'].unique())
            
            if not groups:
                st.warning(f"Brak meczów w dniu {selected_date_str}")
            else:
                for group in groups:
                    group_df = date_df[date_df['group'] == group]
                    league_table = calculate_league_table(group_df)
                    st.subheader(f"Grupa {group} - Tabela Dnia - {selected_date_str}")
                    st.markdown(league_table.to_html(escape=False), unsafe_allow_html=True)
                    st.write("")
        else:
            # Find which group the selected team is in for this date
            team_groups = date_df[(date_df['home_team'] == selected_team) | 
                                (date_df['away_team'] == selected_team)]['group'].unique()
            
            if len(team_groups) == 0:
                st.warning(f"Wybrana drużyna ({selected_team}) nie grała w dniu {selected_date_str}")
            else:
                # Should only be one group per team per date
                group = team_groups[0]
                group_df = date_df[date_df['group'] == group]
                league_table = calculate_league_table(group_df)
                st.subheader(f"Grupa {group} - Tabela Dnia - {selected_date_str}")
                st.markdown(league_table.to_html(escape=False), unsafe_allow_html=True)

    else:  # Wyniki Meczu
        # Date selection using selectbox with actual match dates
        selected_date_str = st.selectbox(
            "Wybierz datę",
            options=["Wszystkie daty"] + [d.strftime("%d/%m/%Y") for d in unique_dates],
            index=0  # Default to most recent date
        )
        
        # Filter by date
        if selected_date_str == "Wszystkie daty":
            results_df = df.copy()
        else:
            selected_date = datetime.strptime(selected_date_str, "%d/%m/%Y").date()
            results_df = df[df['date'].dt.date == selected_date]
        
        # Filter by team if needed
        if selected_team != "Wszystkie Drużyny":
            results_df = results_df[
                (results_df["home_team"] == selected_team) | 
                (results_df["away_team"] == selected_team)
            ]
        
        # Format and display results with index starting at 1
        results_df = results_df.sort_values(['date', 'group'])
        results_df["date"] = results_df['date'].dt.strftime('%d/%m/%Y')
        
        results_display = results_df[["round", "date", "pitch", "group", "home_team", "home_goals", "away_team", "away_goals"]]
        results_display = results_display.rename(columns={
            "round": "Kolejna", "date": "Data", "pitch": "Boisko", "group": "Grupa",
            "home_team": "Drużyna Gospodarzy", "away_team": "Zespół Gości",
            "home_goals": "\u2003", "away_goals": "\u2800"
        })
        
        # Reset index to start at 1
        results_display.index = range(1, len(results_display)+1)
        
        if len(results_display) == 0:
            st.warning("Brak meczów dla wybranych kryteriów")
        else:
            if selected_team == "Wszystkie Drużyny":
                # Apply group-based coloring
                results_display["style"] = results_display["Grupa"].apply(
                    lambda g: "background-color: #2E4E6F;" if ord(g) % 2 else "background-color: #1C2E4A;"
                )
                html_table = (results_display.style
                             .apply(lambda x: [x["style"]] * len(x), axis=1)
                             .hide(axis="columns", subset=["style"])
                             .to_html(escape=False))
                st.markdown(html_table, unsafe_allow_html=True)
            else:
                # Custom CSS for alternating every three rows when a specific team is selected
                st.markdown(
                    """
                    <style>
                    /* Alternating every three rows */
                    .stMarkdown table tr:nth-child(6n+1),
                    .stMarkdown table tr:nth-child(6n+2),
                    .stMarkdown table tr:nth-child(6n+3) {         
                        background-color: #2E4E6F; /* Darker blue for the first three rows */
                    }
                    .stMarkdown table tr:nth-child(6n+4),
                    .stMarkdown table tr:nth-child(6n+5),
                    .stMarkdown table tr:nth-child(6n+6) {
                        background-color: #1C2E4A; /* Lighter blue for the next three rows */
                    }
                    .stMarkdown table th { background-color: #00172B; color: white; }
                    .stMarkdown table td { color: white; }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown(results_display.to_html(escape=False), unsafe_allow_html=True)

if __name__ == "__main__":
    main()

import pandas as pd
import os

def calculate_league_table(city, category):

    df = pd.read_csv(f"data/silver/{city}/{city}_silver_data.csv")
    
    # Filter the DataFrame based on the provided category and group
    if category is not None:
        df = df[df["category"] == category]
       
    # Initialize standings for each team
    teams = set(df["home_team"]).union(set(df["away_team"]))
    standings = {team: {"Games": 0, "Wins": 0, "Draws": 0, "Losses": 0,
                        "Goals Scored": 0, "Goals Conceded": 0, "Goal Difference": 0, "Points": 0} for team in teams}
    
    # Calculate standings
    for _, row in df.iterrows():
        home, away = row["home_team"], row["away_team"]
        home_goals, away_goals = row["home_goals"], row["away_goals"]
        standings[home]["Games"] += 1
        standings[away]["Games"] += 1
        standings[home]["Goals Scored"] += home_goals
        standings[home]["Goals Conceded"] += away_goals
        standings[away]["Goals Scored"] += away_goals
        standings[away]["Goals Conceded"] += home_goals

        if home_goals > away_goals:  
            standings[home]["Wins"] += 1
            standings[away]["Losses"] += 1
            standings[home]["Points"] += 3
        elif home_goals < away_goals:  
            standings[away]["Wins"] += 1
            standings[home]["Losses"] += 1
            standings[away]["Points"] += 3
        else:  
            standings[home]["Draws"] += 1
            standings[away]["Draws"] += 1
            standings[home]["Points"] += 1
            standings[away]["Points"] += 1

        standings[home]["Goal Difference"] = standings[home]["Goals Scored"] - standings[home]["Goals Conceded"]
        standings[away]["Goal Difference"] = standings[away]["Goals Scored"] - standings[away]["Goals Conceded"]

    # Convert standings to a DataFrame and sort
    league_table = pd.DataFrame.from_dict(standings, orient="index").reset_index()
    league_table.rename(columns={"index": "Team"}, inplace=True)
    
    league_table = league_table.sort_values(by=["Points", "Goal Difference", "Goals Scored"], ascending=[False, False, False]) 

    # Ensure directory exists
    output_dir = f"data/gold/{city}"
    os.makedirs(output_dir, exist_ok=True)

    # Fix invalid characters in the file name
    safe_category = category.replace("/", "_").replace(":", "_")

    # Save file
    output_path = f"{output_dir}/{city}_league_table_{safe_category}.csv"
    league_table.to_csv(output_path, index=False) 

# List of cities and categories to process
cities = ["gdansk", "warsaw", "wroclaw", "krakow", "poznan", "slask"]
categories = ["2010/2011", "2012/2013", "2012/2014", "2014/2015", "2016/2017", "2018/2019"]

# Process all cities and categories dynamically
for city in cities:
    for category in categories:
        calculate_league_table(city, category)

print("League standings for all cities have been collated and saved locally as CSV files.")
   

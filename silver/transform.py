import pandas as pd
import numpy as np

def unique_team_names(city, category):
    
    silver_data = pd.read_csv('data/bronze/{city}/{city}_bronze_data.csv').copy()

    ## Add a Calculated RESULT column
    silver_data['result'] = silver_data.apply(
    lambda row: 'HOME WIN' if row['home_goals'] > row['away_goals'] else (
        'AWAY WIN' if row['home_goals'] < row['away_goals'] else 'DRAW'
    ), axis=1    )

    # Get the number of unique teams per Age Category to check for inconsistent naming / duplicates
    category_silver_data = silver_data[silver_data["category"] == category]
    
    unique_home_teams = set(category_silver_data["home_team"].unique())
    unique_away_teams = set(category_silver_data["away_team"].unique())
    team_names = unique_home_teams.union(unique_away_teams)
    
    print(f"There are {len(team_names)} unique team names in the {city.capitalize()} {category} league.")
    return silver_data, team_names     

cities = ["gdansk", "warsaw", "wroclaw", "krakow", "poznan", "slask"]
categories = ["2010/2011", "2012/2013", "2012/2014", "2014/2015", "2016/2017", "2018/2019"]

# Process all cities
for city in cities:
    for category in categories:
        unique_team_names(city, category)
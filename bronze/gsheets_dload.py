import pandas as pd
import numpy as np
import re


def google_sheets_download(city):

     # Create a dictionary of League Google Sheet URLs
    city_urls = {
        "gdansk": "1EEMR48O2JlyPd3ZjJFnL1SWcnSK4Ait0m3uNrBx9vjo",
        "warsaw": "1vEThuBu_0Wd2HiJwh7h1nyiFmjAL280ePZbZEcsIZgM",
        "wroclaw": "1KUIqvcKVvebcanrz68wwT2-wpUaBEjlL4Arni2i1oSs",
        "krakow": "1PlA4FRYJC4NSyO8bZXin8DaKgwua8K7ruYV_LBznmis",                
        "poznan": "1JjHTxYtK1hfu2_2vAQH2u9SrpMzgDAw_GsWQl0f1J0s",
        "slask": "1KgNyrIiz4RNDBN7qZZOLTlBJjT5NC7H8Q3qPwPjuilI"        
    }

    # Parse the Google Sheets URL from https://ligamt.pl/liga/
    gid="422946955"
    

    # Convert url into pandas readable csv format
    url = f"https://docs.google.com/spreadsheets/d/{city_urls.get(city, 'url')}/export?format=csv&gid={gid}"

    # Read data into DataFrame
    raw_data = pd.read_csv(url, header=None)
    raw_data.to_csv(f"data/bronze/{city}/{city}_raw_data.csv", index=False)

    print(f"The raw results for the {city.capitalize()} league have been downloaded.")






### Clean the data
def clean_data(city):

    raw_df = pd.read_csv(f"data/bronze/{city}/{city}_raw_data.csv", header=None)

     # Initialize an empty list to store the transformed data
    transformed_data = []

    # Define the columns where "czas" appears
    czas_columns = [1, 8, 15, 22, 29, 36]

    # Iterate through the rows to extract headers and match data
    for i in range(len(raw_df)-1, -1, -1):
        # Search for "KOLEJKA" in any column (case-insensitive and flexible regex)
        for col in range(len(raw_df.columns)):
            cell_value = str(raw_df.iloc[i, col]).strip().lower()  # Normalize whitespace and casing
            if re.search(r'kolejka\s*\d+', cell_value):  # Flexible regex for "KOLEJKA" followed by optional spaces and digits
                round_value = raw_df.iloc[i, col]  # KOLEJKA is in the current column
                #print(f"Found {round_value} at row {i}, column {col}")  # Debugging output

                # Search for "czas" in the predefined columns (1, 8, 15, 22)
                for czas_col in czas_columns:
                    if czas_col < len(raw_df.columns):  # Ensure column exists
                        for j in range(i + 1, min(i + 10, len(raw_df))):  # Search within the next 10 rows
                            if str(raw_df.iloc[j, czas_col]).strip().lower() == 'czas':
                                #print(f"Found 'czas' at row {j}, column {czas_col}")  # Debugging output

                                # Extract "KATEGORIA" and "date" from the rows above "czas"
                                category_value = raw_df.iloc[j - 1, czas_col]  # KATEGORIA is one row above "czas"
                                date_value = raw_df.iloc[j - 2, czas_col]  # Date is two rows above "czas"
                                #print(f"Found KATEGORIA: {category_value}, Date: {date_value} at row {j - 1}, column {czas_col}")  # Debugging output

                                # Iterate through the rows below "czas" to extract match data
                                for k in range(j + 1, len(raw_df)):
                                    # Skip rows with the "czas" header
                                    if str(raw_df.iloc[k, czas_col]).strip().lower() == 'czas':
                                        break  # Stop processing this column range if we encounter another "czas"

                                    # Check if the row has data in the current column range
                                    if pd.notna(raw_df.iloc[k, czas_col]):
                                        match_data = {
                                            'match_id': len(transformed_data) + 1,
                                            'round': int(round_value.split()[1]),  # Extract round number
                                            'date': date_value,
                                            'category': category_value.replace("KATEGORIA", "").strip().replace(" ", ""),  # Clean category
                                            'group': raw_df.iloc[k, czas_col + 5],  # Group is the sixth column
                                            'pitch': raw_df.iloc[k, czas_col + 6],  # Pitch is the seventh column
                                            'time': raw_df.iloc[k, czas_col],  # Time is the first column in the block
                                            'home_team': raw_df.iloc[k, czas_col + 1].rstrip(),  # Home team is the second column
                                            'away_team': raw_df.iloc[k, czas_col + 2].rstrip(),  # Away team is the third column
                                            'home_goals': raw_df.iloc[k, czas_col + 3],  # Home goals is the fourth column
                                            'away_goals': raw_df.iloc[k, czas_col + 4],  # Away goals is the fifth column                                       
                                        }
                                        transformed_data.append(match_data)
                                    else:
                                        # Stop processing this column range if we encounter an empty row
                                        break
                                break  # Stop searching for "czas" once found

    # Convert the list to a DataFrame
    transformed_data_df = pd.DataFrame(transformed_data)

    current_year = 2025
        
    def parse_date(date_str):
        # Try extracting various date formats
        match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_str)  # Match YYYY-MM-DD
        if match:
            return f"{match.group(3)}/{match.group(2)}/{match.group(1)}"  # Convert to DD/MM/YYYY

        match = re.search(r'-(\s*\d{1,2}\.\d{1,2})\s*/', date_str)  # Match -DD.MM/
        if match:
            date_part = match.group(1).strip()
        else:
            match = re.search(r'-(.*)', date_str)  # Match -<everything after>
            if match:
                date_part = match.group(1).strip()
            else:
                match = re.search(r'\b\w+\s+(\d{1,2}\.\d{1,2})', date_str)  # Match "Niedziela DD.MM"
                if match:
                    date_part = match.group(1)
                else:
                    return None  # No valid date found

        # Convert to datetime format if it's a valid date
        try:
            return pd.to_datetime(f"{date_part}.{current_year}", format='%d.%m.%Y').strftime('%d/%m/%Y')
        except ValueError:
            return date_part  # If it's not a date, return raw text

    # Apply the function to the date_string column and create a new ingestion_date column
    transformed_data_df['date'] = transformed_data_df['date'].apply(parse_date)

     # Add missing result flag
    transformed_data_df["missing_result_flag"] = (
        transformed_data_df["home_goals"].isna() | 
        transformed_data_df["away_goals"].isna() | 
        (transformed_data_df["home_goals"] == "x") | 
        (transformed_data_df["away_goals"] == "x")    
    )
    
    missing_results_df = transformed_data_df[transformed_data_df["missing_result_flag"]]
    missing_results_df.to_csv(f"data/bronze/{city}/{city}_missing_results_followup.csv", index=False)

    # Filter out missing results and clean the data
    df_bronze_data = transformed_data_df[~transformed_data_df["missing_result_flag"]].drop(columns=["missing_result_flag"])

    # Cast to integers
    df_bronze_data["home_goals"] = df_bronze_data["home_goals"].astype(int)
    df_bronze_data["away_goals"] = df_bronze_data["away_goals"].astype(int)
    #df_bronze_data["pitch"] = df_bronze_data["pitch"].astype(int)
    df_bronze_data["ingestion_date"] = pd.Timestamp.now()

    if len(df_bronze_data) % 6 == 0:
        print(f"The {city.capitalize()} data has been cleaned and includes a total of {len(df_bronze_data)} records.")
    else:
        print(f"The {city.capitalize()} data has been cleaned and includes a total of {len(df_bronze_data)} records. There appears to be some missing or duplicate records. Please refer to the missing results file.")

    # Save the transformed data to a CSV file
    df_bronze_data.to_csv(f"data/bronze/{city}/{city}_bronze_data.csv", index=False)

cities = ["gdansk", "warsaw", "wroclaw", "krakow", "poznan", "slask"]

# Process all cities
for city in cities:
    clean_data(city)

print("All city data has been cleaned and written to a local csv file.")
     

    
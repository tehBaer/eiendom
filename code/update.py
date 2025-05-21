import pandas as pd
from code.googleUtils import download_sheet_as_csv, get_credentials, SPREADSHEET_ID
from code.extract import extract_ad_data
from googleapiclient.discovery import build


def FindNewUnavailable(sheet_name: str):
    creds = get_credentials()
    service = build("sheets", "v4", credentials=creds)
    download_sheet_as_csv(service, sheet_name, "leie/saved_all.csv", "A:Z")

    # Load the downloaded data into a DataFrame
    df_saved = pd.read_csv("leie/saved_all.csv")

    updated_rows = []

    for index, row in df_saved.iterrows():
        # if (index < 50):
        #     continue
        # If Tilgjengelighet is already marked as Utleid or Slettet, skip the row
        if (row["Tilgjengelighet"] == 'Utleid' or row["Tilgjengelighet"] == "Slettet"):
            print(f"Skipping Finnkode {row['Finnkode']} as it is {row[4]}")
            continue
        try:
            # Extract data for the URL
            updated_data = extract_ad_data(row["URL"], index, "leie")
            updated_rows.append(updated_data)
        except Exception as e:
            print(f"Error processing URL at index {index}: {row['Finnkode']} - {e}")
            updated_rows.append({
                "Finnkode": row["Finnkode"],
                "Tilgjengelighet": "Slettet",
            })

    data = pd.DataFrame(updated_rows)
    dfdata = data[["Finnkode", "Tilgjengelighet"]]
    dfdata.to_csv("leie/saved_availability.csv", index=False)
    return dfdata


def PasteNewAvailability(data, sheet_name):
    # Initialize the service
    creds = get_credentials()
    service = build("sheets", "v4", credentials=creds)

    # Define spreadsheet ID and range name
    range_name = f"{sheet_name}!D2"  # Adjust the range as needed
    # Replace NaN values with an empty string
    data = data.fillna("")

    # Convert the DataFrame to a list of lists
    body = {
        "values": data.values.tolist()
    }

    # Update the Google Sheet
    result = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=range_name,
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()

    print(f"{result.get('updatedCells')} cells updated.")


if __name__ == "__main__":
    sheetName = "Main"
    data = FindNewUnavailable(sheetName)
    # data = pd.read_csv("leie/saved_availability.csv")
    PasteNewAvailability(data, sheetName)

﻿import pandas as pd
from pandas import DataFrame


import pandas as pd
from pandas import DataFrame


def cleanData(df: DataFrame, projectName: str, outputFileName: str):
    # Fill AREAL column
    df['AREAL'] = df['Primærrom'].fillna(df['Internt bruksareal (BRA-i)']).fillna(df['Bruksareal'])

    # Convert AREAL to numeric, coercing errors to NaN
    df['AREAL'] = pd.to_numeric(df['AREAL'], errors='coerce')

    # Drop rows where AREAL or Leiepris is NaN
    df = df.dropna(subset=['AREAL', 'Leiepris'])

    # Calculate and add 'PRIS KVM' column
    df['PRIS KVM'] = (df['Leiepris'].astype(float) / df['AREAL'].astype(float)).astype(int)

    # Format capitalization
    df['Adresse'] = df['Adresse'].str.title()

    # Convert AREAL and Depositum to integers
    df['AREAL'] = df['AREAL'].astype(int)
    df['Depositum'] = df['Depositum'].fillna(0).astype(int)

    # Drop unnecessary columns
    df = df.drop(columns=['Primærrom',
                          'Internt bruksareal (BRA-i)',
                          'Bruksareal',
                          'Eksternt bruksareal (BRA-e)',
                          'Balkong/Terrasse (TBA)',
                          'Bruttoareal'
                          ])

    # Save to analyze.csv
    df.to_csv(f'{projectName}/{outputFileName}', index=False)

    return df

# if main
if __name__ == "__main__":
    file_path = 'leie/extracted.csv'
    df = pd.read_csv(file_path)
    cleanData(df)
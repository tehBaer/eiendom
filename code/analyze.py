import pandas as pd


def analyze():
    # Read the CSV file into a DataFrame
    file_path = 'leie/extracted.csv'
    df = pd.read_csv(file_path)

    df['AREAL'] = df['Primærrom'].fillna(df['Internt bruksareal (BRA-i)']).fillna(df['Bruksareal'])

    # Calculate and add 'PRIS KVM' column
    df['PRIS KVM'] = (df['Leiepris'].astype(float) / df['AREAL'].astype(float)).astype(int)

    #  Format capitalization
    df['Adresse'] = df['Adresse'].str.title()

    # Drop columns that are completely empty
    df = df.drop(columns=['Primærrom',
                          'Internt bruksareal (BRA-i)',
                          'Bruksareal',
                          'Eksternt bruksareal (BRA-e)',
                          'Balkong/Terrasse (TBA)',
                          'Bruttoareal'
                          ])

    # Save to analyze.csv
    df.to_csv('leie/analyzed.csv', index=False)

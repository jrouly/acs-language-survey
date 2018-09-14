import pandas as pd
import re
from tabulate import tabulate

# 0 = US
# 1-52 = all states and territories
indices = range(1, 53)

def read_labeled_csv(i):
    filename = 'csvs/detailed-lang-tables.csv_{}'.format(i)
    with open(filename, 'r') as f:
        next(f)
        label = next(f)
        state_name_pattern = re.compile('Over for (.*):')
        label = state_name_pattern.search(label).group(1)
    df = pd.read_csv(filename, header=3)
    return label, df

dataframes = [read_labeled_csv(i) for i in indices]

dataframes = {
    label: df
    for (label, df) in dataframes
}

for (label, df) in dataframes.items():
    # Isolate and rename interesting columns
    df = df[['Unnamed: 0', 'Number of speakers']]
    df = df.rename(index=str, columns={
        'Unnamed: 0': 'Language',
        'Number of speakers': 'Speakers',
    })

    # Convert number of speakers to numeric
    df['Speakers'] = df['Speakers'].apply(pd.to_numeric, errors='coerce')

    # Number of speakers
    n = int(df['Speakers'].iloc[0])

    # Skip to after English and Spanish.
    df = df[6:]

    # Compute percentage of total
    df['Percent'] = (df['Speakers'] / n) * 100

    # Sort by highest percentage.
    df = df.sort_values('Percent', ascending=False)

    # Get the top 20 entries because some are aggregates.
    # We ultimately want the top 10.
    df = df[['Language', 'Speakers', 'Percent']].head(20)

    # Most aggregates are over 18 characters.
    # Most languages are under 18 characters.
    # This is kind of a hack.
    df = df[df['Language'].str.len() < 18]

    # Drop duplicates.
    df = df.drop_duplicates('Language')

    # Narrow down to top 10.
    df = df.head(10)

    # Pretty print percentage.
    df['Percent'] = df['Percent'].map('{:,.2f}%'.format)

    print("### {}".format(label))
    print("{} adult speakers".format(n))
    print()
    report = tabulate(df, df.columns, "pipe")
    print(report)
    print()

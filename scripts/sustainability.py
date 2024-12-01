# -*- coding: utf-8 -*-
"""Sustainability.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1OYNjbbHl0oPClG2jLXTgTxO53AisPLYC
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Importing Libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load Datasets
df_sector = pd.read_csv('/content/co-emissions-by-sector.csv')
df_country = pd.read_csv('/content/annual-co2-emissions-per-country.csv')

# Inspect Datasets
print("Sector Data Overview")
print(df_sector.head())
print(df_sector.info())

print("\nCountry Data Overview")
print(df_country.head())
print(df_country.info())

# Drop 'Code' Column
df_sector = df_sector.drop('Code', axis=1)
df_country = df_country.drop('Code', axis=1)

# Handle Missing Values
df_sector.dropna(inplace=True)
df_country.dropna(inplace=True)

# Standardize Column Names
df_sector.columns = df_sector.columns.str.strip().str.lower().str.replace(' ', '_')
df_country.columns = df_country.columns.str.strip().str.lower().str.replace(' ', '_')

# Rename 'entity' to 'country'
df_sector = df_sector.rename(columns={'entity': 'country'})
df_country = df_country.rename(columns={'entity': 'country'})

# Filter Data for Years 2000 and Beyond
df_sector_filtered = df_sector[df_sector['year'] >= 2000]
df_country_filtered = df_country[(df_country['year'] >= 2000) & (df_country['year'] <= 2020)]

# Merge Sector and Country Data
merged_df = pd.merge(df_sector_filtered, df_country_filtered, on=['year', 'country'], how='inner')

# Remove Duplicates
merged_df = merged_df.drop_duplicates(subset=['year', 'country'], keep='first')

# Remove Non-Country Entries
countries_to_remove = ['Upper-middle-income countries', 'Lower-middle-income countries', 'Low-income countries']
merged_df = merged_df[~merged_df['country'].isin(countries_to_remove)]

# Select Relevant Supply Chain Sectors
supply_chain_sectors = [
    'carbon_dioxide_emissions_from_transport',
    'carbon_dioxide_emissions_from_manufacturing_and_construction',
    'carbon_dioxide_emissions_from_electricity_and_heat',
    'carbon_dioxide_emissions_from_bunker_fuels'
]
filtered_merged_df = merged_df[['country', 'year'] + supply_chain_sectors]

# Emission Factors
emission_factors_values = {
    'carbon_dioxide_emissions_from_transport': {'CO2_factor': 2.31, 'CH4_factor': 0.06, 'N2O_factor': 0.02},
    'carbon_dioxide_emissions_from_manufacturing_and_construction': {'CO2_factor': 1.83, 'CH4_factor': 0.015, 'N2O_factor': 0.005},
    'carbon_dioxide_emissions_from_electricity_and_heat': {'CO2_factor': 0.72, 'CH4_factor': 0.012, 'N2O_factor': 0.002},
    'carbon_dioxide_emissions_from_bunker_fuels': {'CO2_factor': 3.02, 'CH4_factor': 0.04, 'N2O_factor': 0.012}
}

# Global Warming Potential (GWP) Factors
GWP_CH4 = 25
GWP_N2O = 298

# Calculate CO₂e for Each Sector
def calculate_co2e(emission_value, co2_factor, ch4_factor, n2o_factor, gwp_ch4, gwp_n2o):
    co2_emissions = emission_value * co2_factor
    ch4_emissions = emission_value * ch4_factor * gwp_ch4
    n2o_emissions = emission_value * n2o_factor * gwp_n2o
    total_co2e = co2_emissions + ch4_emissions + n2o_emissions
    return total_co2e

refined_df = filtered_merged_df.copy()
for sector, factors in emission_factors_values.items():
    co2_factor = factors['CO2_factor']
    ch4_factor = factors['CH4_factor']
    n2o_factor = factors['N2O_factor']
    refined_df[f'{sector}_co2e'] = refined_df[sector].apply(
        calculate_co2e, args=(co2_factor, ch4_factor, n2o_factor, GWP_CH4, GWP_N2O)
    )

# Convert CO₂e to Metric Tons
co2e_columns = [
    'carbon_dioxide_emissions_from_transport_co2e',
    'carbon_dioxide_emissions_from_manufacturing_and_construction_co2e',
    'carbon_dioxide_emissions_from_electricity_and_heat_co2e',
    'carbon_dioxide_emissions_from_bunker_fuels_co2e'
]
for column in co2e_columns:
    refined_df[column] = refined_df[column] / 1000

# Load Freight and Container Datasets
freight_df = pd.read_csv('/content/Transport_Freight.csv')
container_df = pd.read_csv('/content/Container Transporty.csv')

# Drop Unnecessary Columns
columns_to_drop = ['STRUCTURE','STRUCTURE_ID', 'STRUCTURE_NAME', 'ACTION','OBS_STATUS','UNIT_MULT','DECIMALS', 'REF_AREA']
freight_df = freight_df.drop(columns=columns_to_drop, errors='ignore')
container_df = container_df.drop(columns=columns_to_drop, errors='ignore')

# Rename Columns
freight_df.rename(columns={'Reference area': 'country'}, inplace=True)
container_df.rename(columns={'Reference area': 'country'}, inplace=True)

# Select Relevant Columns
freight_df_selected = freight_df[['country', 'Transport mode', 'OBS_VALUE', 'TIME_PERIOD', 'Unit of measure']]
container_df_selected = container_df[['country', 'Transport mode', 'OBS_VALUE', 'TIME_PERIOD', 'Unit of measure']]

# Standardize Country Names
freight_df_selected['country'] = freight_df_selected['country'].str.title().str.strip()
container_df_selected['country'] = container_df_selected['country'].str.title().str.strip()

# Merging Freight and Container Data
merged_data = pd.merge(freight_df_selected, container_df_selected,
                        on=['country', 'TIME_PERIOD'],
                        how='inner',
                        suffixes=('_freight', '_container'))

# Visualize Data
sns.barplot(x='Transport mode_freight', y='total_co2e', data=merged_data)
plt.title('CO₂e Emissions by Freight Transport Mode')
plt.show()
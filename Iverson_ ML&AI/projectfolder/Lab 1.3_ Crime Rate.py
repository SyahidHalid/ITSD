# import pandas as pd

# df = pd.read_csv('pandas\\data.csv')

# df.head()
# df.tail()
# df.info()
# df.describe()

# #data cleaning

# df.isna().sum()

# new_df = df.dropna()

# new_df.info()

# df.dropna(inplace=True)

# df.dropna(subset=['Calories'], inplace=True)

# df[df['Calories'].isnull()]

# df["Calories"].fillna(df["Calories"].mean(), inplace=True)

# #df.loc[7,'Duration'] = 45
# df.loc[df['Duration'] > 120, 'Duration'] = 120

# df.corr()

#============================================================

# Lab3

import numpy as np
import pandas as pd
import plotly.express as px

df = pd.read_csv('pandas\\crime_district.csv')

# o
# Display the first 5 rows of the DataFrame.
df.head(5)

# o
# Print the summary statistics for numerical columns.
df.describe()

# o
# Check for missing values and data types of each column.
df.info()

df.columns = df.columns.str.replace(' ', '_')
df.columns = df.columns.str.title()
df1_1 = df.apply(lambda x: x.str.title() if x.dtype == "object" else x)

#check duplicates
df.duplicated().any()
df.duplicated().sum()

df1 = df1_1.drop_duplicates()

df2 = df1[(df1['State'] != "Malaysia")&
          (df1['District'] != "All")&
          (df1['Category'] != "All")&
          (df1['Type'] != "All")]


#Calculate the total number of crimes for each district In.

df_group = df2.groupby('District')['Crimes'].sum().reset_index()

#Calculate the total number of crimes for each state.

df_group_state = df2.groupby('State')['Crimes'].sum().reset_index()

#Find the top 5 districts with the highest number of crimes.

df_top5_districts = df_group.sort_values(by='Crimes', ascending=False).head(5)

#Identify the trend of crime counts over the years for a specific category (e.g., "assault")

df2.Date = df2.Date.astype('datetime64[ns]')
df2['Year'] = df2['Date'].dt.year

df_assault_trend = df2[df2['Category'] == "Assault"].groupby('Year')['Crimes'].sum().reset_index()

#Analyze the distribution of crime types for a given year (e.g., 2020).

df_2020 = df2[df2['Year'] == 2020]
df_crime_distribution = df_2020.groupby('Type')['Crimes'].sum().reset_index().sort_values(by='Crimes', ascending=False)


# Data Analyst
# - Reporting & Analysis
# - SQL
# - Excel
# - Power BI
# - Tableau
# - Python

# Business Analyst
# - Business Process and Requirements
# - Documentation
# - Communication

# Data Scientist
# - Machine Learning
# - Predictive Modeling
# - Statistical Analysis
# - Deep Learning
# - Python & R

# Data Engineer
# - Data Pipeline Development Infrastructure
# - SQL
# - Python
# - Spark
# - Airflow
# - Hadoop
# - Cloud and Big Data

# Machine Learning Engineer
# - Prodcutionizing Machine Learning Models
# - Python
# - MLOp
# - Docker
# - Kubernetes

#==========================================================
# 
# LAB 4

# Task 1: Bar Chart - Total Crimes by State

import matplotlib.pyplot  as plt

x = df_group_state['State']
y = df_group_state['Crimes']

plt.figure(figsize=(10, 6))
plt.bar(x, y, color='skyblue')

plt.title('Crimes by State')
plt.xlabel('State')
plt.ylabel('Number of Crimes')
plt.xticks(rotation=45)
plt.tight_layout()

plt.show()

# Task 2: Bar Chart - Top 5 Districts with the highest crimes

x1 = df_top5_districts['District']
y1 = df_top5_districts['Crimes']

plt.figure(figsize=(10, 6))
plt.bar(x1, y1, color='red')

plt.title('Top 5 District')
plt.xlabel('District')
plt.ylabel('Number of Crimes')
#plt.xticks(rotation=45)
plt.tight_layout()

plt.show()

# combine

import matplotlib.pyplot as plt

# Data for first chart
x = df_group_state['State']
y = df_group_state['Crimes']

# Data for second chart
x1 = df_top5_districts['District']
y1 = df_top5_districts['Crimes']

# Create one figure with 2 subplots
plt.figure(figsize=(16, 6))

# Subplot 1: Crimes by State
plt.subplot(1, 2, 1)   # 1 row, 2 columns, first chart
plt.bar(x, y, color='skyblue')
plt.title('Crimes by State')
plt.xlabel('State')
plt.ylabel('Number of Crimes')
plt.xticks(rotation=45)

# Subplot 2: Top 5 Districts
plt.subplot(1, 2, 2)   # 1 row, 2 columns, second chart
plt.bar(x1, y1, color='red')
plt.title('Top 5 Districts')
plt.xlabel('District')
plt.ylabel('Number of Crimes')

# Adjust layout
plt.tight_layout()
plt.show()

# combine 2

import matplotlib.pyplot as plt

# Task 1 data: Bar chart - Total Crimes by State
x = df_group_state['State']
y = df_group_state['Crimes']

# Task 3 data: Line chart - Crime Trend for Assault Category
x2 = df_assault_trend['Year']
y2 = df_assault_trend['Crimes']

# Create 1 figure with 2 subplots
fig, ax = plt.subplots(1, 2, figsize=(16, 6))

# Subplot 1: Bar chart
ax[0].bar(x, y, color='skyblue')
ax[0].set_title('Crimes by State')
ax[0].set_xlabel('State')
ax[0].set_ylabel('Number of Crimes')
ax[0].tick_params(axis='x', rotation=45)

# Subplot 2: Line chart
ax[1].plot(x2, y2, color='green', marker='o')
ax[1].set_title('Crime Trend for Assault')
ax[1].set_xlabel('Year')
ax[1].set_ylabel('Number of Crimes')

# Adjust layout
plt.tight_layout()
plt.show()


# Task 3: Line Chart - Crime Trend for Assault Category

x2 = df_assault_trend['Year']
y2 = df_assault_trend['Crimes']

plt.figure(figsize=(10, 6))
plt.plot(x2, y2, color='green')

plt.title('Crime Trend')
plt.xlabel('Year')
plt.ylabel('Number of Crimes')
#plt.xticks(rotation=45)
plt.tight_layout()

plt.show()

# Task 4: Pie Chart - Crime Type

import matplotlib.pyplot as plt

x3 = df_crime_distribution['Type']      # labels
y3 = df_crime_distribution['Crimes']    # values

plt.figure(figsize=(10, 6))


plt.pie(
    y3,
    labels=x3,
    autopct='%1.0f%%',
    startangle=90,
    labeldistance=1.1
)

plt.title('Crime Type')
plt.axis('equal')

plt.show()



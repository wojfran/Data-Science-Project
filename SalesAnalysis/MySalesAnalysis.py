import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# changing print options of the console so that I can print the full dataframe and not just 3 columns
desired_width=320
pd.set_option('display.width', desired_width)
np.set_printoptions(linewidth=desired_width)
pd.set_option('display.max_columns', 10)

# Merging 12 months of sale data into one file
files = [file for file in os.listdir('./Sales_Data')]
df = None
for file in files:
    temp = pd.read_csv(f'./Sales_Data/{file}')
    df = pd.concat([df, temp], axis=0)

df.to_csv('all_data.csv', index=False)

# what was the best month for sales?
# adding a new colum containing the month and year of sale only
df['Order Month'] = df['Order Date'].str[0:3] + df['Order Date'].str[6:8]

# I noticed that some rows where filled with column names (side effect from concatenation of the files)
# this meant that for them the column 'Order Month' showed 'OrdDa' instead of the actual month and year
# below I cut all of them out as they are redundant
df = df[df['Order Month'] != 'OrdDa']

# since I am cleaning the data already, I might as well drop all the NaN rows if there are any
df = df.dropna()

# Here I created a grouped list showing the number of sales in each month
print(df.groupby('Order Month').count()['Order ID'])

# Now I will sort them to see which one was the best
monthly_sales = df.groupby('Order Month').count()['Order ID'].sort_values(ascending=False)
print(monthly_sales)

# trying to determine the monthly earnings now
# first I'll create a new column showing the total earnings from each row (amount of product times its price),
# values had to be converted to numeric type for the multiplication
df['Total Earnings'] = round((df['Quantity Ordered'].astype('int32') * df['Price Each'].astype('float32')), 2)

# now I can use the sum method with groupby to basically sum all the earnings from each row
# corresponding to a chosen month
monthly_earnings = df.groupby('Order Month')['Total Earnings'].sum().sort_values(ascending=False)
print(monthly_earnings)

# here I have created a list of  distinct months that could be found in the Dataframe
# I had to convert their type into datetime so that they would sort properly
months = list(set(df['Order Date'].str[0:3] + df['Order Date'].str[6:8]))
months.sort(key=lambda month: datetime.strptime(month, '%m/%y'))
print(months)

# Here I realized that the whole column's type (Order Month) had to be converted to datetime either way,
# as without it the total earnings for each month wouldn't align with the sorted months list
df['Order Month'] = pd.to_datetime(df['Order Month'], format='%m/%y')
sales = df.groupby('Order Month')['Total Earnings'].sum()

# Here I am just checking out the Matplotlib library by presenting the manufactured data on a graph
# The graph does not show a bar for month 01/20 but that is simply because of the low amount of products
# sold in that month, presumably the sales data was provided at the beginning of 01/20
plt.bar(months, sales)
plt.xticks(months)
plt.ylabel('Total earnings for each month in USD ($)')
plt.xlabel('Months')
# plt.show()

# What city had the highest number of sales?
# Here I used the pandas Series.str.split() function to break up the purchase address and then used the second value in
# the created list to create a new column called city
df['City'] = (df['Purchase Address'].str.split(', ')).str[1]
# Now by using a simple groupby combination with sum we can see how much money the company has earned in each city
print(df.groupby('City')['Total Earnings'].sum())


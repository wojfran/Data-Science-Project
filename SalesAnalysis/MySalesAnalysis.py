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
# first I'll create a new column showing the total earnings from each row,
# values had to be converted to numeric type for the multiplication
df['Total Earnings'] = round((df['Quantity Ordered'].astype('int32') * df['Price Each'].astype('float32')), 2)

# now I can use the sum method with groupby
monthly_earnings = df.groupby('Order Month')['Total Earnings'].sum().sort_values(ascending=False)
print(monthly_earnings)
months = list(set(df['Order Date'].str[0:3] + df['Order Date'].str[6:8]))
months.sort(key=lambda month: datetime.strptime(month, '%m/%y'))
print(months)
sales = df.groupby('Order Month')['Total Earnings'].sum()
# print(sales)
plt.bar(months, sales)
plt.show()


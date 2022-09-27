import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from itertools import combinations
from collections import Counter

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
plt.figure(0)
plt.bar(months, sales)
plt.xticks(months, rotation='vertical', size=12)
plt.ylabel('Total earnings for each month in USD ($)')
plt.xlabel('Months')
plt.tight_layout()
# Plot commented out, bcs it slowed me down while testing
# plt.show()

# What city had the highest number of sales?
# Here I used the pandas Series.str.split() function to break up the purchase address and then used the second value in
# the created list to create a new column called city, I also included the state that the city is
# because there are 2 Portlands
df['City'] = (df['Purchase Address'].str.split(', ')).str[1] + ', ' \
             + ((df['Purchase Address'].str.split(', ')).str[2]).str[0:2]

# Now by using a simple groupby combination with sum we can see how much money the company has earned in each city
print(df.groupby('City')['Total Earnings'].sum())

# I want to depict the data on a graph, for that purpose I created a new dataframe consisting only of the list of cities
# and their respective total earnings, the list of cities is sorted as to match the output of the groupby + sum methods
# (they are sorted alphabetically by default)
data = {'Cities': sorted(list(set(df['City']))),
        'Total Earnings': list(df.groupby('City')['Total Earnings'].sum())
        }

city_stats = pd.DataFrame(data, columns=['Cities', 'Total Earnings'])

# Now we can view the effects of my search in a neat dataframe which I will transform into a graph next
print(city_stats)

# I added plt.figure() so that this graph wouldn't be merged with the previous one
plt.figure(1)
plt.bar(city_stats['Cities'], city_stats['Total Earnings'])
plt.xticks(city_stats['Cities'], rotation='vertical', size=9)
plt.ylabel('Total earnings for each city')
plt.xlabel('Cities')
plt.tight_layout()
# plt.show()

# The next task is to determine when is the best time to air advertisements to maximize profits,
# in order to do that I will try to determine in which hours most purchases are made
# I decided to use the apply + lambda combination here to familiarize myself with it
df['Purchase Hour'] = df['Order Date'].apply(lambda x: x.split(' ')[1])

# this only gives us a separate column with the precise hour and minute when the product was bought,
# which doesn't really help us much. I think the simplest way of achieving our goal is to further split it and register
# only the hour when the product was bought. By doing so we get 24 distinct sets of time
df['Purchase Hour'] = df['Purchase Hour'].apply(lambda x: x.split(':')[0])
print(df.groupby('Purchase Hour').count()['Order ID'])
purchases_per_hour = list(df.groupby('Purchase Hour').count()['Order ID'])
hours = range(0, 24)
plt.figure(2)
plt.bar(hours, purchases_per_hour)
plt.ylabel('Amount of purchases during each hour')
plt.xlabel('Hours')
plt.xticks(hours)
# plt.show()

# Searching for which products are most often sold together
# to be revised ! couldn't do it on my own
together_df = df[df['Order ID'].duplicated(keep=False)]
together_df['Products Grouped'] = together_df.groupby('Order ID')['Product'].transform(lambda x: ', '.join(x))
together_df = together_df[['Order ID', 'Products Grouped']].drop_duplicates()
print(together_df)

count = Counter()

for row in together_df['Products Grouped']:
    row_list = row.split(',')
    count.update(Counter(combinations(row_list, 2)))

for key, value in count.most_common(10):
    print(key, value)

# Searching what product sold the most
# Pretty much exactly the same steps I did before, a simple group by + count combination,
# I then converted values into lists to make it easier to plot
products = sorted(list(df['Product'].unique()))
amount_sold = list(df.groupby('Product').count()['Order ID'])
prices = df.groupby('Product').mean()
print(prices)
plt.figure(3)
fig, ax1 = plt.subplots()

ax2 = ax1.twinx()
ax1.bar(products, amount_sold, color='g')
ax2.plot(products, prices, 'b-')

ax1.set_xlabel('Products')
ax1.set_ylabel('Amount of product sold', color='g')
ax2.set_ylabel('Price', color='b')
ax1.set_xticklabels(products, rotation='vertical')
plt.tight_layout()
plt.show()

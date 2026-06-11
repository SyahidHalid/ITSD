import numpy as np

daily_sales = np.array([150.50, 200.75, 180.00, 220.25, 300.50, 250.00, 275.75])

week2_sales = np.array([160.00, 210.50, 190.25, 230.00, 310.75, 260.50, 280.00])

print("Daily Sales Data for the Week:")

print(daily_sales)


# 1. Calculate Total Sales:

# Use NumPy to calculate the total sales for the week using sum.

print(sum(daily_sales))


# 2. Calculate Average Daily Sales:

# Find the average daily sales using mean.

print(np.mean(daily_sales))


# 3. Identify Best and Worst Sales Days:

# Determine the best and worst sales days using min and max.

print("Best Sales Day:", np.max(daily_sales))

print("Worst Sales Day:", np.min(daily_sales))


# 4. Calculate the Standard Deviation:

# Analyze the variability in daily sales by calculating the standard deviation.

print("Standard Deviation:", np.std(daily_sales))


# 5. Sales Comparison with Weekend Data:

# Create a new array for sales during a promotional weekend. [400.00, 450.00]

# Concatenate the daily sales array with the weekend sales array.

weekend_sales = np.array([400.00, 450.00])

newsales = daily_sales[-2:] + weekend_sales

daily_sales[-2:] = newsales

# total_sales = np.concatenate((daily_sales, weekend_sales))

print("Total Sales including Weekend:", sum(daily_sales))


# 6. Recalculate Total and Average Sales:

# Recalculate the total and average sales including the weekend data.

print("New Total Sales:", np.sum(daily_sales))

print("New Average Sales:", np.mean(daily_sales))


# 7. Visualize Sales Trends:

# Create an array representing the days of the week and calculate sales trends.

days = np.array(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])

sales_trends = np.diff(daily_sales)

print("Sales Trends (Day-to-Day Changes):", sales_trends)

import matplotlib.pyplot as plt

plt.plot(days, daily_sales, marker='x', linestyle='-', color='red')
plt.plot(days, week2_sales, marker='s', linestyle='-', color='blue')
plt.title("Daily Sales Data")
plt.xlabel("Days of the Week")
plt.ylabel("Sales ($)")
plt.grid(True)
plt.show()

# 8. continous lab:

# calculate difference week 1 and week 2

sales_difference = week2_sales - daily_sales

best_sales_improvements = np.max(sales_difference)

best_day_improvements = np.argmax(sales_difference)

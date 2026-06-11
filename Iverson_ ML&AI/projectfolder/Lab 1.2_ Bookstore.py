#1. Create a DataFrame:

#Manually create a DataFrame representing a bookstore’s inventory. Include columns such as "Title", Author", "Genre", "Price", and "Quantity".


# Step 1: Set Up Your Workspace 
import pandas as pd 

# Step 2: Create a DataFrame
data = {
    "Title": ["Book A", "Book B", "Book C"],
    "Author": ["Author 1", "Author 2", "Author 3"],
    "Genre": ["Fiction", "Non-Fiction", "Fiction"],
    "Price": [15.99, 22.50, 12.99],
    "Quantity": [10, 5, 8]
}

df = pd.DataFrame(data)

type(df)

df.dtypes

df[["Title", "Price"]]

df["Total Value"] = df["Price"] * df["Quantity"]

df[df["Price"] > 15]

df[df["Genre"] == "Fiction"]

df.sort_values(by="Price", ascending=False)

df.groupby("Genre")["Quantity"].sum().reset_index()

df["Price"].mean()


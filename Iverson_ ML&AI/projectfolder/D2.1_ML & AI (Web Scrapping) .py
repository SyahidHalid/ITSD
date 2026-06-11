# Matplotlib
# Seaborn
# Dash.Plotly (2D & 3D)
# Streamlit



# Selenium
# - Automate and interact with a web browser
#     - can click button
#     - can fill form

# Beautiful Soup
# - Parse and extract data from HTML/XML
#     - Cannot click button

#pip install selenium --trusted-host pypi.org --trusted-host files.pythonhosted.org

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import time

#create browser instance
driver = webdriver.Chrome()

#Open a webpage
driver.get("https://google.com")

search_box = driver.find_element(By.NAME, "q")
search_box.send_keys("Python Programming")
search_box.send_keys(Keys.RETURN)

time.sleep(10)

print(driver.title)

#google.com/robot.txt

driver.quit()



#Scrapper
import pandas as pd

df = pd.read_html("https://www.mudah.my/")
print(df)


# BeautifulSoup
from bs4 import BeautifulSoup
import requests
import certifi

url = "https://quotes.toscrape.com/"

response = requests.get(url, verify=False)

soup = BeautifulSoup(response.content, "html.parser")

for item in soup.find_all("div", class_="quote"):
    quote = item.find("span", class_="text").get_text()
    author = item.find("small", class_="author").get_text()
    print(f"{quote} - {author}")
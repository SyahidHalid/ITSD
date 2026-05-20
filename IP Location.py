#   !pip install phonenumbers --trusted-host pypi.org --trusted-host files.pythonhosted.org

number = "+60193035652"

import phonenumbers
#from myphone import number
from phonenumbers import geocoder

pepnumber = phonenumbers.parse(number)
location = geocoder.description_for_number(pepnumber, "en")
print(location)

from phonenumbers import carrier
service_pro = phonenumbers.parse(number)
print(carrier.name_for_number(service_pro, "en"))

#   !pip install opencage --trusted-host pypi.org --trusted-host files.pythonhosted.org
#   !pip show opencage

import opencage
from opencage.geocoder import OpenCageGeocode
#   OpenCagedate.com

key  ""

geocoder = OpenCageGeocode(key)
query = str(location)
result = geocoder.geocode(query)
print(result)

lat = result[0]['geometry']['lat']
lng = result[0]['geometry']['lng']

print(lat, lng)

#   !pip install folium --trusted-host pypi.org --trusted-host files.pythonhosted.org

import folium

myMap = folium.Map(location=[lat,lng], zoom_start=9)
folium.Marker([lag,lng], popup=location).add_to(myMap)

myMap.save("location.html")

#===============================================================================================================================

#   !python update certifi
import requests,certifi

res=requests.get("https://ipinfo.io", verify=False)
print(res.text)

data = res.json()

print(data)

city = data['city']
print(city)

location = data['loc'].split(',')
print(location)

latitude = location[0]
longitude = location[1]

print("Latitude : ", latitude)
print("Longitude : ", longitude)
print("City : ", city)




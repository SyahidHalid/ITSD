#umu.com kode wi8618

# python institute cert

#https://www.umu.com/course/?groupId=177176&sKey=ef5f#

a = 3 + 4 * 2

len("Python")

bool(0)

mylist = [3,1,-2]
print(mylist[mylist[-1]])

# Jython Java to Python

#   cmd --python version
import sys
print(sys.version)

#   (Get-Command python).Source
import sys
print(sys.executable)


# check venv ad x
import sys
print("Python executable:", sys.executable)
print("Prefix:", sys.prefix)
print("Base prefix:", sys.base_prefix)
print("In venv:", sys.prefix != sys.base_prefix)

# pip install -r requirements.txt

# cd "D:\00. Git Repository\ITSD\Iverson_ ML & AI"

# python -m venv venv
# .\venv\Scripts\activate
# pip install pandas numpy scikit-learn


#===========================================================


# cd "D:\00. Git Repository\ITSD\Iverson_ ML&AI"
# cd "projectfolder"

#create venv
# PS D:\00. Git Repository\ITSD\Iverson_ ML&AI\projectfolder> python -m venv .venv

#activate
# PS D:\00. Git Repository\ITSD\Iverson_ ML&AI\projectfolder> .venv\Scripts\activate 
# (.venv) PS D:\00. Git Repository\ITSD\Iverson_ ML&AI\projectfolder> pip list
#.venv\Scripts\activate


#===========================================================


print("Hello World")
print("Machine","Learning","Best") 

list1 = [1,2,3,4]
list1.sort(reverse=True)

Output = "Programming***Essentials***in...python"
print(Output)
print("Programming","Essential","in",sep="***",end="...")
print("Syahid\nPower")


#===========================================================


#Datype 
name = "Syahid" #str
age = 28 #int
height = 161.2 #Flot
student = True #Bool
print(type(name))

#operator
print(10 + 2)
print(10 - 2)
print(10 * 2)
print(10 / 2)
print(10 // 2)
print(10 % 2)
print(10 ** 2)

num1 = 4
num1 += 7 #shortcut operator


#===========================================================


#input user
name = input("Please enter your name:" )

addtion1 = int(input("Please enter no:"))
addtion2 = int(input("Please enter no:"))
add = int(addtion1) + int(addtion2)
print(add)
print(addtion1-addtion2)

#lab 6
hour = int(input("time :"))
minit = int(input("minit :"))
duration = int(input("duration :"))

total_minit = ((hour*60)+minit+duration)

print((total_minit//60),(total_minit%60),sep=':')

#xlebih 24hours
print(f"End Time = {(total_minit//60)%24}:{total_minit%60:02.0f}")


#===========================================================


#conditional statements
print(1==1) #True 
# != > >= < <= False False True False True

#if else
age = int(input("age"))
haveIC = False

if haveIC:
    if age >= 18:
        print("Adult")
    elif age >= 12:
        print("Teenager")
    else:
        print("Minor")
else:
    print("Foreigner")


# boolean 0 je false lain sume true
if 2:
    print("run")
else:
    print("dont")

name ="lala"
if name:
    print("run")
else:
    print("dont")


#looping (Repeat as long as true)
while True:
    print("Stuck")


password = 77
while True:
    mypass=int(input("pass"))
    if mypass == password:
        print("correct")
        break #to shutdown loop
    else:
        print("Wrong")


for i in range(5):
    print(i)

for sufi in range(5):
    print(i)

for i in range(5,2,-1):
    print(i)

for i in range(2,6,2):
    print(i)


#===========================================================


import time

a = int(input("pukul brp datuk harimau"))

for i in range(a,0,-1):
    print(f"pukul brp datuk harimau {i}")
    time.sleep(3)
print("waktu buru")


#===========================================================


# Collection (Store multiple data)

#list
mylist = ["Sufi", 21, 1.9, True]
print(type(mylist))
print(mylist[-4])

mylist[1] = 23

del mylist[-1]

print(len(mylist))

#method vs #function
mylist.append("Putrajaya")
mylist.insert(0,"Male")

mylist2 = [8,10,6,2,4]
mylist2.sort()
mylist2.sort(reverse=True)

#slicing
print(mylist2[2:])

my_list = [1,2,4,4,1,4,2,6,2,9]
unique_list = list(set(my_list))

#set
mySet = {"apple","banana","orange","papaya"}
print(mySet)

#dictionary (key : value)
cust1 = {"name":"sufi",
         "age":21,
         "occupation":"trainer",
         "address":"putrajaya"}
print(cust1["name"])

cust1["name"] = "syahid"
cust1["phone"] = 12345

for k,v in cust1.items():
    print(f"{k} -> {v}")

#tuple
mytuple = (1,2,3,4,5)
print(type(mytuple))

mytuple[0] = 10

#string
name = "Sufi Firdaus"
name.isspace()

print("A">"a")


#Built in sqeuence function

#1. len() - number of element
print(len(my_list))

#2. min() - smallest element
print(min(my_list))
print(max(my_list))

#3. sum() - total of numeric sequence
print(sum(my_list))

#4. enumerate() - index + value
for index, num in enumerate(my_list, start=1):
    print(index, num)

#5. sorted()
print(sorted(my_list))



#===========================================================

#FUNCTION


# parameterised function
def greetings(fname,lname,middle="bin"):
    print(f"Heloo {fname} {middle} {lname}")

greetings("syahid","halid")


def add(a,b):
    return(a+b)

add(1,3) + 6


#1. input weight and height
#2. create function to calculate BMI
#3. Return back bmi value

a = float(input("a"))
b = float(input("b"))

def BMI(a,b):
    answer = a/(b**2)
    return answer

print(f"{BMI(a,b):.2f}")

def Category(bmi_rounded):
    if bmi_rounded < 18.5:
        print("Category: Underweight")
    elif 18.5 <= bmi_rounded < 25.0:
        print("Category: Normal weight")
    elif 25.0 <= bmi_rounded < 30.0:
        print("Category: Overweight")
    else:
        print("Category: Obesity")

Category(BMI(a,b))


#===========================================================

#SPLIT


myList = [1,2,3,4,5,6]

def popmiddle(ml):
    middle_index = len(ml)//2
    item = ml[middle_index]
    del ml[middle_index]
    return item

popmiddle(myList)
print(myList)

name = "Sufi Firdaus Bin Fakrurrazey"
print(name.split())


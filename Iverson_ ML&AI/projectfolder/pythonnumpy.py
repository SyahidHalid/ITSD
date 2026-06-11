
# ===================================================Array
import numpy as np

print(np.__version__)

list1 = [1, 2, 3, 4, 5]

# for i in list1:
#     print(i+3)

a = np.array([1, 2, 3, 4, 5])
b = np.array([[[1, 2, 3], [4, 5, 6], [7, 8, 9]]])

# print(a*3)
# print(b)


# #Statistic
# print(np.std(a))
# print(np.mean(a))
# print(np.median(a))


arr1 = np.array([1, 2, 3, 4, 5,6])

arr2 = np.array([[1,2,3],
                 [4,5,6]])

# arr3 = np.array([[1,2,3],
#                  [4,5,6]],
#                  [[7,8,9],
#                  [10,11,12]])

arrZeros = np.zeros((3,4)) # 3 row 4 column

arrOnes = np.ones((3,4))

# print(arrZeros)

# print(arr1.dtype)

# print(arr2.size)
# print(arr2.ndim)


### ===================================================Array Indexing and Slicing


# print(arr1[0])

# print(arr2[:,1:])


# ### ===================================================booelan Indexing
# #selecting an elements based on condition

# print(arr1>2)

# print(arr1[arr1>2])

# print(arr2[arr2%2==0]) # select even number

# #Array Operation (element wise operation)
# print(arr1+3)
# print(arr1*2)
# print(arr1/2) 

#Operation aking axes (axis=0, axis=1)
#row axis 1
#column axis 0

# print(np.sum(arr2, axis=0)) # sum of column
# print(np.sum(arr2, axis=1)) # sum of row


### ===================================================reshape


newarr = arr1.reshape(2,3) # reshape to 2 row and 3 column
print(newarr)
print(newarr.T) # transpose of array


### ===================================================concantenation

newestarr = np.concatenate((arr2,newarr))

newestarr = np.concatenate((arr2,newarr), axis=1)

#pip install -r requirement.txt



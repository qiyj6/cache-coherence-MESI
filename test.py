import copy

list_1=[0,1,2]
list_2=list_1
list_3=copy.deepcopy(list_1)
list_3[0]=5
print(list_3[0])
list_3[0]=0
print(id(list_1[0]),id(list_2[0]),id(list_3[0]))
print(id(list_1[0])==id(list_3[0]))
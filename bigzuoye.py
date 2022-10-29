INVALID=0
EXCLUSIVE=1
SHARED=2
MODIFIED=3

addr=[]
for i in range(0xff+1):
    addr.append(str(hex(i)))

cache_a=dict.fromkeys(addr,0)
cache_b=dict.fromkeys(addr,0)
print(cache_a)
# print(cache_a["0xffff"])
file_path='C:/Users/quark/Desktop/bigzuoye/trace0.txt'
with open(file_path,'r') as f0:
    line=f0.read()
    while line:
        print(line,end='')#避免换行输出
        op_data=line.split()
        op_a=int(op_data[0])
        op_address_a=op_data[1]
        line=f0.readline()

op_a=0
op_b=0
op_address_a=0
op_address_b=0


i=0


while(i==2):
    i=i+1
    if(cache_a[op_address_a]==INVALID):     #b可能是M，E，I中的任意一种
        if(op_a==1):    #Lw2a,Rw2b
            cache_a[op_address_a]=EXCLUSIVE
            cache_b[op_address_a]=INVALID
        else:           #Lr2a,Rr2b
            if(cache_b[op_address_a]==INVALID):
                cache_a[op_address_a]=EXCLUSIVE
            else:
                cache_a[op_address_a]=SHARED
                cache_b[op_address_a]=SHARED
    elif((cache_a[op_address_a]==SHARED)):      #a，b此时都是SHARED状态
        if(op_a==1):
            cache_a[op_address_a]=EXCLUSIVE
            cache_b[op_address_a]=INVALID
        else:  
            cache_a[op_address_a]=SHARED
    elif((cache_a[op_address_a])==EXCLUSIVE):   #b此时是INVALID状态，无论a本地读还是本地写，对b来说是远程读和远程写，它的状态不会变
        if(op_a==1):
            cache_a[op_address_a]=MODIFIED
            cache_b[op_address_a]=INVALID   
        else:
            cache_a[op_address_a]=EXCLUSIVE
            cache_b[op_address_a]=INVALID
    else:
        cache_a[op_address_a]=MODIFIED
        cache_b[op_address_a]=INVALID


    if(cache_b[op_address_b]==INVALID):     #a可能是M，E，I中的任意一种
        if(op_b==1):    #Lw2a,Rw2b
            cache_b[op_address_b]=EXCLUSIVE
            cache_a[op_address_b]=INVALID
        else:           #Lr2a,Rr2b
            if(cache_a[op_address_b]==INVALID):
                cache_b[op_address_b]=EXCLUSIVE
            else:
                cache_b[op_address_b]=SHARED
                cache_a[op_address_b]=SHARED
    elif((cache_b[op_address_b]==SHARED)):      #a，b此时都是SHARED状态
        if(op_b==1):
            cache_b[op_address_b]=EXCLUSIVE
            cache_a[op_address_b]=INVALID
        else:  
            cache_b[op_address_b]=SHARED
    elif((cache_b[op_address_b])==EXCLUSIVE):   #a此时是INVALID状态，无论b本地读还是本地写，对a来说是远程读和远程写，它的状态不会变
        if(op_b==1):
            cache_b[op_address_b]=MODIFIED
            cache_a[op_address_b]=INVALID   
        else:
            cache_b[op_address_b]=EXCLUSIVE
            cache_a[op_address_b]=INVALID
    else:
        cache_b[op_address_b]=MODIFIED
        cache_a[op_address_b]=INVALID
    
    



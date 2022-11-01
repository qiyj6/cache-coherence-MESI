
I='INVALID'
E='EXCLUSIVE'
S='SHARED'
M='MODIFIED'
NONE=0

def read_file(file_path,op_n,op_address_n):
    with open(file_path,'r') as f0:
        line=f0.read()
        i=0
        while line:
            print(end='')#避免换行输出
            op_data=line.split()
            line=f0.readline()
            i=i+1
            op_n.append(int(op_data[0],2))
            op_address_n.append(int(op_data[1],16))
    return op_n,op_address_n

def decode_address(op_address_n):
    op_address_n_str=bin(op_address_n) #转16进制字符串
    op_address_n_str=op_address_n_str[2:].rjust(32,'0')
    print(op_address_n_str)
    offset=op_address_n_str[26:32]
    index=op_address_n_str[20:26]
    tag = op_address_n_str[0:20]
    print('offset',offset)
    print('tag', tag)
    print('index',index)

def cache_op(cache_op_d,cache_op_id,address,op):
    if(cache_op_d[address]==INVALID):     #b可能是M，E，I中的任意一种
        if(op=='1'):    #Lw2a,Rw2b
            cache_op_d[address]=EXCLUSIVE
            cache_op_id[address]=INVALID
        else:           #Lr2a,Rr2b
            if(cache_op_id[address]==INVALID):
                cache_op_d[address]=EXCLUSIVE
            else:
                cache_op_d[address]=SHARED
                cache_op_id[address]=SHARED
    elif((cache_op_d[address]==SHARED)):      #a，b此时都是SHARED状态
        if(op=='1'):
            cache_op_d[address]=EXCLUSIVE
            cache_op_id[address]=INVALID
        else:  
            cache_op_d[address]=SHARED
    elif((cache_op_d[address])==EXCLUSIVE):   #b此时是INVALID状态，无论a本地读还是本地写，对b来说是远程读和远程写，它的状态不会变
        if(op=='1'):
            cache_op_d[address]=MODIFIED
            cache_op_id[address]=INVALID   
        else:
            cache_op_d[address]=EXCLUSIVE
            cache_op_id[address]=INVALID
    else:
        cache_op_d[address]=MODIFIED
        cache_op_id[address]=INVALID

    return cache_op_d,cache_op_id

file_path_t0='C:/Users/quark/Desktop/bigzuoye/trace0.txt'
file_path_t1='C:/Users/quark/Desktop/bigzuoye/trace1.txt'
op_0=[]
op_address_0=[]
op_1=[]
op_address_1=[]

# op_0,op_address_0=read_file(file_path_t0,op_0,op_address_0)
# op_1,op_address_1=read_file(file_path_t1,op_1,op_address_1)
# decode_address(op_address_0[0])
# op_address_all=(list(set(op_address_0) | set(op_address_1))) #取cache0，cache1操作地址的并集，用于cache初始化
# cache_0=dict.fromkeys(op_address_all,INVALID) 
# cache_1=dict.fromkeys(op_address_all,INVALID)

# for i in range(len(op_1)):
#     cache_0,cache_1=cache_op(cache_0,cache_1,op_address_0[i],op_0[i])
#     cache_1,cache_0=cache_op(cache_1,cache_0,op_address_1[i],op_1[i])
#     print('第%d次cache_0操作'%(i+1), op_0[i],'地址0x%08x'%op_address_0[i])
#     print('第%d次cache_1操作'%(i+1), op_1[i],'地址0x%08x'%op_address_1[i])
#     print('第%d次cache_0状态'%(i+1),cache_0)
#     print('第%d次cache_1状态'%(i+1),cache_1,'\n')







################################################


class cache_line:
    def __init__(self, state=I,tag=0x0000f,data=0):
        self.state = state
        self.tag = tag
        self.data = data

    def print_cache_line(self):
        print("tag : ", self.tag, ", state: ", self.state)

# class cache(list):
#     #     super(cache,self).__init__(256)
#     # cache_list=[]
#     def __init__(self):
#         cache_list=[]
#     @staticmethod
#     def create_cache_list():
#         cache_list=[]
#         set_num=64
#         cache_line_num=256
#         for i in range(cache_line_num):
#             cache_list.append(cache_line())
#             # print(cache_list[i].tag)
#         return cache_list
#     @staticmethod
#     def test():
#         print('test')
#         print(cache_list[0])
def cache_init():
    cache_list=[]
    for i in range(cache_line_num):
        cache_list.append(cache_line())
    return cache_list

cache_line_num=256
cache_0=cache_init()



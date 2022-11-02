
from base64 import decode


INVALID='INVALID'
EXCLUSIVE='EXCLUSIVE'
SHARED='SHARED'
MODIFIED='MODIFIED'
NONE=0

cache_line_num=256
set_num=64
cache_line_per_set=4

class cache_line:
    def __init__(self, state=INVALID,tag=0x00000,data=0):
        self.state = state
        self.tag = tag
        self.data = data

    def print_cache_line(self):
        print("tag : ", self.tag, ", state: ", self.state)

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
    op_address_n_str=bin(op_address_n)                      #将10进制数转2进制字符串
    op_address_n_str=op_address_n_str[2:].rjust(32,'0')     #左侧用0补齐至32位
    offset=int(op_address_n_str[26:32],2)                   #完成切片后，转10进制数
    index=int(op_address_n_str[20:26],2)
    tag = int(op_address_n_str[0:20],2)
    return index,tag,offset,

def cache_set_init():
    cache_set_list=[]
    for i in range(set_num):
        one_set=[]
        cache_set_list.append(one_set)
        for j in range(cache_line_per_set):
            one_set.append(cache_line()) 
    return cache_set_list

def cache_HorM(cache_num,index,tag):
    for i in range(cache_line_per_set):         #遍历对应组的所有cache line 查看tag是否一致
        if (cache_num[index][i].tag==tag):
            if(cache_num[index][i].state!=INVALID):   #若tag一致，且状态不是无效，则命中,返回组中哪个位置的cache line命中 
                return i
            else:                               #tag一致，状态无效，则不命中
                return False
        else:                                   #tag 不相同继续遍历
            continue
    return False                                    #tag 全部不相同，不命中

def cache_op_hit(cache_op_d,cache_op_id,index,tag,op):
    if(op==1):
        if(cache_op_d[index][tag].state==EXCLUSIVE):
            cache_op_d[index][tag].state=MODIFIED
        elif(cache_op_d[index][tag].state==SHARED):
            cache_op_d[index][tag].state=EXCLUSIVE
            if(cache_HorM(cache_op_id,index,tag)):
                cache_op_id[index][tag].state=INVALID


# def cache_op_miss(cache_op_d,cache_op_id,index,tag,op):
#     if(op==0):
#         if(cache_HorM(cache_op_id,index,tag)==0):
#             cache

op_0=[]
op_address_0=[]
op_1=[]
op_address_1=[]
file_path_t0='C:/Users/zbl/Desktop/bigzuoye/trace0.txt'
file_path_t1='C:/Users/zbl/Desktop/bigzuoye/trace1.txt'

op_0,op_address_0=read_file(file_path_t0,op_0,op_address_0)
op_1,op_address_1=read_file(file_path_t1,op_1,op_address_1)

cache_0=cache_set_init()
cache_1=cache_set_init()
print(cache_0[63][3].data)

for i in range(max(len(op_1),len(op_0))):
    index_0,tag_0,offset_0=decode_address(op_address_0[i])
    index_1,tag_1,offset_1=decode_address(op_address_1[i])
    cache_0_hit=cache_HorM(cache_num=cache_0,index=index_0,tag=tag_0);
    cache_1_hit=cache_HorM(cache_num=cache_1,index=index_1,tag=tag_1);




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

#####################


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






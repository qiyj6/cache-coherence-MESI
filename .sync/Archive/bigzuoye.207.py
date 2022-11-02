import random
from prettytable import PrettyTable as PT

INVALID=0
EXCLUSIVE=1
SHARED=2
MODIFIED=3
NONE=0

cache_line_num=256
set_num=64
cache_line_per_set=4
cache_line_databyte=64
mem_line_num=65536

class cache_line:
    def __init__(self, state=INVALID,tag=0x00000):
        self.state = state
        self.tag = tag
        self.data = []
    def cache_data_init(self):
        for i in range(cache_line_databyte):
            self.data.append(str(i))


def read_file(file_path,op_n,op_address_n):
    with open(file_path,'r') as f0:
        line=f0.read()
        while line:
            print(end='')#避免换行输出
            op_data=line.split()
            line=f0.readline()
    for i in range(int(len(op_data)/2)):
        op_n.append(int(op_data[2*i],2))
        op_address_n.append(int(op_data[2*i+1],16))
    return op_n,op_address_n


def cache_set_print(cache_num,index,data_offset):
    cache_set_title = PT(['set num', 'cache line num', 'tag', 'state','data[%d]'%data_offset])
    for i in range(cache_line_per_set):
        cache_set_title.add_row([index,i,cache_num[index][i].tag,cache_num[index][i].state,cache_num[index][i].data[data_offset]])
    return cache_set_title

def decode_address(op_address_n):
    op_address_n_str=bin(op_address_n)                      #将10进制数转2进制字符串
    op_address_n_str=op_address_n_str[2:].rjust(32,'0')     #左侧用0补齐至32位
    offset=int(op_address_n_str[26:32],2)                   #完成切片后，转10进制数
    index=int(op_address_n_str[20:26],2)
    tag = int(op_address_n_str[0:20],2)
    return index,tag,offset

def cache_set_init():
    cache_set_list=[]
    for i in range(set_num):
        one_set=[]
        cache_set_list.append(one_set)
        for j in range(cache_line_per_set):
            one_set.append(cache_line())
            cache_set_list[i][j].cache_data_init() 
    return cache_set_list

def mem_init():
    mem_list=[]
    for i in range(mem_line_num):
        x=bin(i)
        x=x[2:].rjust(16,'0')
        mem_list.append(x[8:16])
    return mem_list

def mem_write(source,mem_list,tag,index):
    mem_addr_high=tag*4096+index*64
    for i in range(cache_line_databyte):
        mem_addr=mem_addr_high+i
        mem_list[mem_addr]=source[i]
    return mem_list

def mem_print(addr,mem_list):
    cache_set_title = PT(['mem address', 'data'])
    for i in range(cache_line_per_set):
        cache_set_title.add_row([addr,mem_list[addr]])
    return cache_set_title

def cache_HorM(cache_num,index,tag):    #返回命中cache组内偏移
    for i in range(cache_line_per_set):         #遍历对应组的所有cache line 查看tag是否一致
        if (cache_num[index][i].tag==tag):
            if(cache_num[index][i].state!=INVALID):   #若tag一致，且状态不是无效，则命中,返回组中哪个位置的cache line命中 
                return i
            else:                               #tag一致，状态无效，则不命中
                return -1
        else:                                   #tag 不相同继续遍历
            continue
    return -1                                    #tag 全部不相同，不命中

def set_avail(cache_set):
    for i in range(cache_line_per_set):
        if(cache_set[i].state==0):
            return i    #cache组不满，返回不满位置的offset_in_set
        else:
            continue
    return -1

def apply_cache_line(cache_set,tag,index):
    num=set_avail(cache_set)
    if(num==-1): #满,则随机替换
        num=random.randint(0,3)
        if(cache_set[num].state==MODIFIED):
            print('write back to mem')
        cache_set[num].tag=tag
        # cache_set[num].data='wait load from other place'
    else:
        cache_set[num].tag=tag
        # cache_set[num].data='wait load from other place'
    return cache_set,num

def cache_op_hit(cache_op_d,cache_op_id,index,tag,offset_in_set_d,op,offset_num):
    if(op==1):
        if(cache_op_d[index][offset_in_set_d].state==EXCLUSIVE):
            cache_op_d[index][offset_in_set_d].data[offset_num]='10011001'
            cache_op_d[index][offset_in_set_d].state=MODIFIED
        elif(cache_op_d[index][offset_in_set_d].state==SHARED):
            cache_op_d[index][offset_in_set_d].data[offset_num]='10011001'
            print('write back to mem')
            cache_op_d[index][offset_in_set_d].state=EXCLUSIVE
            offset_in_set_id=cache_HorM(cache_op_id,index,tag)  
            if(offset_in_set_id!=-1):    #其他cache命中
                cache_op_id[index][offset_in_set_id].state=INVALID
        else:   #处于M状态，改数据，状态不变
            cache_op_d[index][offset_in_set_d].data[offset_num]='10011001'
        
    return cache_op_d,cache_op_id


def cache_op_miss(cache_op_d,cache_op_id,index,tag,op,offset_num):
    cache_op_id_hit=cache_HorM(cache_op_id,index,tag) #值为其他cache命中的cache line组内偏移
    if(op==0):
        if(cache_op_id_hit==-1): #其他cache line也不命中
            cache_op_d[index],offset_in_set=apply_cache_line(cache_op_d[index],tag) #在组内申请cache line，若满则随机替换，返回组内偏移
            cache_op_d[index][offset_in_set].state=EXCLUSIVE
        else:   #其他cache line命中
            if(cache_op_id[index][cache_op_id_hit].state==EXCLUSIVE or SHARED):   #其他cache 是E，将其他cache的数据装入当前cache，cache状态都变为S
                cache_op_d[index],offset_in_set=apply_cache_line(cache_op_d[index],tag)
                cache_op_d[index][offset_in_set].data[offset_num]=cache_op_id[index][cache_op_id_hit].data[offset_num] 
                cache_op_d[index][offset_in_set].state=SHARED
                cache_op_id[index][cache_op_id_hit].state=SHARED
            elif(cache_op_id[index][cache_op_id_hit].state==MODIFIED):   #其他cache 是M，将其他cache的数据装入当前cache，写入主存，cache状态都变为S
                cache_op_d[index],offset_in_set=apply_cache_line(cache_op_d[index],tag)
                cache_op_d[index][offset_in_set].data[offset_num]=cache_op_id[index][cache_op_id_hit].data[offset_num]
                print('write back to mem') 
                cache_op_d[index][offset_in_set].state=SHARED
                cache_op_id[index][cache_op_id_hit].state=SHARED   
    else: #写不命中
        # print('leng=',len(cache_op_d[index][2].data))
        if(cache_op_id_hit==-1): #其他cache不命中
            cache_op_d[index],offset_in_set=apply_cache_line(cache_op_d[index],tag)
            cache_op_d[index][offset_in_set].data[offset_num]='10011001'
            print('write back to mem')
            cache_op_d[index][offset_in_set].state=EXCLUSIVE
        else: #其他cache命中
            if(cache_op_id[index][cache_op_id_hit].state==EXCLUSIVE or SHARED):
                cache_op_id[index][cache_op_id_hit].state=INVALID
                cache_op_d[index],offset_in_set=apply_cache_line(cache_op_d[index],tag)
                cache_op_d[index][offset_in_set].data[offset_num]='10011001'
                print('write back to mem')
                cache_op_d[index][offset_in_set].state=EXCLUSIVE
            else:
                print('write cache_id back to mem')
                cache_op_id[index][cache_op_id_hit].state=INVALID
                cache_op_d[index],offset_in_set=apply_cache_line(cache_op_d[index],tag) #从主存中加载数据
                cache_op_d[index][offset_in_set].data[offset_num]='10011001'
                print('write back to mem')
                cache_op_d[index][offset_in_set].data=EXCLUSIVE

    return cache_op_d,cache_op_id


op_0=[]
op_address_0=[]
op_1=[]
op_address_1=[]
file_path_t0='C:/Users/zbl/Desktop/bigzuoye/trace0.txt'
file_path_t1='C:/Users/zbl/Desktop/bigzuoye/trace1.txt'

op_0,op_address_0=read_file(file_path_t0,op_0,op_address_0)
op_1,op_address_1=read_file(file_path_t1,op_1,op_address_1)

cache_0=cache_set_init()
# cache_0.cache_data_init()
cache_1=cache_set_init()
# cache_1.cache_data_init()
print(len(cache_1[1][0].data))

for i in range(max(len(op_1),len(op_0))):
    index_0,tag_0,offset_0=decode_address(op_address_0[i])
    index_1,tag_1,offset_1=decode_address(op_address_1[i])
    cache_0_hit=cache_HorM(cache_num=cache_0,index=index_0,tag=tag_0);
    cache_1_hit=cache_HorM(cache_num=cache_1,index=index_1,tag=tag_1);
    print('第%d次cache_0操作'%(i+1), op_0[i],'地址0x%08x'%op_address_0[i])
    print('第%d次cache_1操作'%(i+1), op_1[i],'地址0x%08x'%op_address_1[i])
    print('第%d次cache_0操作前cache set如下'%(i+1))
    print(cache_set_print(cache_0,index_0,offset_0))
    print('第%d次cache_1操作前cache set如下'%(i+1))
    print(cache_set_print(cache_1,index_1,offset_1))
    if(cache_0_hit!=-1):
        cache_0,cache_1=cache_op_hit(cache_0,cache_1,index_0,tag_0,cache_0_hit,op_0[i],offset_0)
    else:
        cache_0,cache_1=cache_op_miss(cache_0,cache_1,index_0,tag_0,op_0[i],offset_0)
        
    if(cache_1_hit!=-1):
        cache_1,cache_0=cache_op_hit(cache_1,cache_0,index_1,tag_1,cache_1_hit,op_1[i],offset_1)
    else:
        cache_1,cache_0=cache_op_miss(cache_1,cache_0,index_1,tag_1,op_1[i],offset_1)
    
    print('第%d次cache_0操作后cache set如下'%(i+1))
    print(cache_set_print(cache_0,index_0,offset_0))
    print('第%d次cache_1操作后cache set如下'%(i+1))
    print(cache_set_print(cache_1,index_1,offset_1))
    print('#################################################### 操作分割线 ####################################################' )
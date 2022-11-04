import random
from prettytable import PrettyTable as PT

INVALID='I'
EXCLUSIVE='E'
SHARED='S'
MODIFIED='M'
mem_id=2
the_other_cache_id=1
all_device=3

cache_line_num=8
set_num=4
cache_line_per_set=2
cache_line_databyte=64

mem_line_num=128
mem_set_num=4 
data_num=64

class cache_line:
    def __init__(self, state=INVALID,tag=0x00000):
        self.state = state
        self.tag = tag
        self.data = []
    def cache_data_init(self):
        for i in range(cache_line_databyte):
            # self.data.append(bin(i)[2:].rjust(8,'0'))
            self.data.append('00000000')

class bus(): #地址信号，数据信号，数据有效信号,状态信号(总线是否被占用)，读写广播信号，读写广播响应
    def __init__(self):
        self.state = 0
        self.tag = -1
        self.index = -1
        self.data = []
        self.data_valid=0
        self.broadcast=-1
        self.response=0
        self.state_response = []
        self.device_id=-1
    def available(self):
        self.state = 0
        self.tag = -1
        self.index = -1
        self.data = []
        self.broadcast=-1
        self.response=0
        self.state_response = []
        self.device_id=-1
        self.data_valid=0
    def occuied(self,tag,index,broadcast,device_id,data_valid=0,data=[]):
        self.tag = tag
        self.index = index
        self.data=data
        self.state=1
        self.broadcast=broadcast
        self.device_id=device_id
        self.data_valid=data_valid


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
    cache_set_title = PT(['index', 'cache line num', 'tag', 'state','data[%d]'%data_offset])
    for i in range(cache_line_per_set):
        cache_set_title.add_row([index,i,hex(cache_num[index][i].tag),cache_num[index][i].state,cache_num[index][i].data[data_offset]])
    return cache_set_title

def decode_address(op_address_n):
    op_address_n_str=bin(op_address_n)                      #将10进制数转2进制字符串
    op_address_n_str=op_address_n_str[2:].rjust(15,'0')     #左侧用0补齐至32位
    offset=int(op_address_n_str[9:15],2)                   #完成切片后，转10进制数
    index=int(op_address_n_str[7:9],2)
    tag = int(op_address_n_str[0:7],2)
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
        mem_set=[]
        mem_list.append(mem_set)
        for j in range(mem_set_num):
            data_list=[]
            mem_set.append(data_list)
            for k in range(data_num):            
                data_list.append('10000001')
    return mem_list

def mem_print(mem_data,tag,index,offset):
    mem_addr_high=tag*256+index*64
    cache_set_title = PT(['mem address', 'data'])
    if(offset==-1):
        for i in range(data_num):
            cache_set_title.add_row([str(hex(mem_addr_high+i)).rjust(4,'0'),mem_data[i]])
    else:
        cache_set_title.add_row([str(hex(mem_addr_high+offset)).rjust(4,'0'),mem_data[offset]])
    return cache_set_title

def cache_HorM(cache_set,tag):    #返回命中cache组内偏移
    for i in range(cache_line_per_set):         #遍历对应组的所有cache line 查看tag是否一致
        if (cache_set[i].tag==tag):
            if(cache_set[i].state!=INVALID):   #若tag一致，且状态不是无效，则命中,返回组中哪个位置的cache line命中 
                return i,cache_set[i].state
            else:                               #tag一致，状态无效，则不命中
                return -1,cache_set[i].state
        else:                                   #tag 不相同继续遍历
            continue
    return -1,INVALID                             #tag 全部不相同，不命中

def apply_line_in_set(cache_set,mem_list,tag,index,bus=bus()):
    set_avail_offset=-1

    for i in range(cache_line_per_set):
        if(cache_set[i].state==INVALID):
            set_avail_offset=i
            break    #cache组不满
        else:
            continue

    if(set_avail_offset==-1): #set full
        num=random.randint(0,cache_line_per_set-1)
        set_avail_offset=num
        old_tag=cache_set[num].tag
        old_data=cache_set[num].data
        if(cache_set[num].state==MODIFIED):
            bus.occuied(tag=old_tag,index=index,data=old_data,broadcast=1,device_id=mem_id,data_valid=1)
    
    if(bus.device_id==mem_id and bus.data_valid==1):
        mem_list[bus.tag][bus.index]=bus.data
        bus.available()

    cache_set[set_avail_offset].tag=tag

    return cache_set,mem_list,set_avail_offset


def RW(cache_num,tag):
    none=0
    offset_in_set,none=cache_HorM(cache_num,tag)
    if(offset_in_set!=-1):
        cache_num[offset_in_set].state=INVALID
    else: 
        pass
    return cache_num

def state_I_mem_fresh(cache_num,mem_list,bus=bus()):
    if(bus.device_id==all_device and bus.data_valid==1):
        cache_num[bus.index]=RW(cache_num[bus.index],bus.tag)
        mem_list[bus.tag][bus.index]=bus.data
    else:
        pass  

    bus.available()

    return cache_num,mem_list


def cache_op_hit(cache_op_d,cache_op_id,mem_list,index,tag,offset_in_set_d,op,offset_num,data_i,bus=bus()):
    #进入该函数的前提是cache_d命中
    data=bin(data_i)[2:].rjust(8,'0')
    if(op==1):  
        if(cache_op_d[index][offset_in_set_d].state==(EXCLUSIVE or MODIFIED)):
            cache_op_d[index][offset_in_set_d].data[offset_num]=data
            cache_op_d[index][offset_in_set_d].state=MODIFIED
        else:
            cache_op_d[index][offset_in_set_d].data[offset_num]=data
            cache_op_d[index][offset_in_set_d].state=EXCLUSIVE
            bus.occuied(tag,index,data=cache_op_d[index][offset_in_set_d].data,broadcast=op,device_id=all_device,data_valid=1) 

    cache_op_id,mem_list=state_I_mem_fresh(cache_op_id,mem_list,bus)

    return cache_op_d,cache_op_id,mem_list

def read_from_bus(cache_op_d,cache_op_id,mem_list,tag,index,offset_in_set_d):
    bus_0=bus()
    bus_0.occuied(tag=tag,index=index,broadcast=0,device_id=the_other_cache_id)
    if(bus_0.broadcast==0 and bus_0.device_id==the_other_cache_id):
        id_set_offset,id_offset_state=cache_HorM(cache_op_id[index],tag)
        bus_0.response=id_set_offset
        if(id_set_offset!=-1):
            bus_0.state_response=id_offset_state
            if(id_offset_state==MODIFIED):
                bus_0.data_valid=1
                bus_0.data=cache_op_id[index][id_set_offset].data
                cache_op_id[index][id_set_offset].state=SHARED
            else: #cache_id 处于E或S
                cache_op_id[index][id_set_offset].state=SHARED
    else:
        pass

    if(bus_0.response==-1 or bus_0.state_response==(SHARED or EXCLUSIVE)):
        bus_0.data=mem_list[tag][index]
        bus_0.data_valid=1
    elif(bus_0.state_response==MODIFIED):
        mem_list[tag][index]=bus_0.data
    else:
        pass

    cache_op_d[index][offset_in_set_d].data=bus_0.data

    if(bus_0.response==-1):
        cache_op_d[index][offset_in_set_d].state=EXCLUSIVE
    else:
        cache_op_d[index][offset_in_set_d].state=SHARED

    bus_0.available()

    return cache_op_d,cache_op_id,mem_list

def cache_op_miss(cache_op_d,cache_op_id,mem_list,index,tag,op,offset_num,data_i):
    bus_1=bus()
    data=bin(data_i)[2:].rjust(8,'0')
    #进入该函数的前提是cache_d不命中
    cache_op_d[index],mem_list,offset_in_set=apply_line_in_set(cache_set=cache_op_d[index],mem_list=mem_list,tag=tag,index=index)
    cache_op_d,cache_op_id,mem_list=read_from_bus(cache_op_d,cache_op_id,mem_list,tag,index,offset_in_set)

    if(op==1): #写不命中
        # bus.occuied(tag,index,offset_num,data,broadcast=op,de)
        # if(cache_op_d[index][offset_in_set].state==EXCLUSIVE):
        #     cache_op_d[index][offset_in_set].state=MODIFIED
        #     cache_op_d[index][offset_in_set].data[offset_num]=data
        # else: #cache_d 处于 S
        cache_op_d[index][offset_in_set].state=EXCLUSIVE
        cache_op_d[index][offset_in_set].data[offset_num]=data
        bus_1.occuied(tag,index,offset_num,data=cache_op_d[index][offset_in_set].data,broadcast=op,data_valid=1,device_id=all_device)
    else: 
        pass

    cache_op_id,mem_list=state_I_mem_fresh(cache_op_id,mem_list,bus_1)

    return cache_op_d,cache_op_id,mem_list


op_0=[]
op_address_0=[]
op_1=[]
op_address_1=[]
file_path_t0='C:/Users/quark/Desktop/bigzuoye/trace0.txt'
file_path_t1='C:/Users/quark/Desktop/bigzuoye/trace1.txt'

op_0,op_address_0=read_file(file_path_t0,op_0,op_address_0)
op_1,op_address_1=read_file(file_path_t1,op_1,op_address_1)

cache_0=cache_set_init()
cache_1=cache_set_init()
mem_list=mem_init()


for i in range(max(len(op_1),len(op_0))):
    none=0
    index_0,tag_0,offset_0=decode_address(op_address_0[i])
    index_1,tag_1,offset_1=decode_address(op_address_1[i])
    cache_0_hit,none=cache_HorM(cache_set=cache_0[index_0],tag=tag_0)
    cache_1_hit,none=cache_HorM(cache_set=cache_1[index_1],tag=tag_1)
    print("cache_0_hit==",cache_0_hit)
    print("cache_1_hit==",cache_1_hit)
    print('第%d次cache_0操作'%(i+1), op_0[i],'地址0x%08x'%op_address_0[i])
    print('第%d次cache_1操作'%(i+1), op_1[i],'地址0x%08x\n'%op_address_1[i])
    print('第%d次cache_0操作前cache set如下'%(i+1))
    print(cache_set_print(cache_0,index_0,offset_0))
    print('第%d次cache_1操作前cache set如下'%(i+1))
    print(cache_set_print(cache_1,index_1,offset_1),'\n')
    if(op_1[i]==1 and op_0[i]==0 and op_address_0[i]==op_address_1[i]):
        if(cache_1_hit!=-1):
            cache_1,cache_0,mem_list=cache_op_hit(cache_1,cache_0,mem_list,index_1,tag_1,cache_1_hit,op_1[i],offset_1,i+1)
        else:
            cache_1,cache_0,mem_list=cache_op_miss(cache_1,cache_0,mem_list,index_1,tag_1,op_1[i],offset_1,i+1)


        cache_0_hit,none=cache_HorM(cache_set=cache_0[index_0],tag=tag_0)

        if(cache_0_hit!=-1):
            cache_0,cache_1,mem_list=cache_op_hit(cache_0,cache_1,mem_list,index_0,tag_0,cache_0_hit,op_0[i],offset_0,i+1)
        else:
            cache_0,cache_1,mem_list=cache_op_miss(cache_0,cache_1,mem_list,index_0,tag_0,op_0[i],offset_0,i+1)
        
    else:
        if(cache_0_hit!=-1):
            cache_0,cache_1,mem_list=cache_op_hit(cache_0,cache_1,mem_list,index_0,tag_0,cache_0_hit,op_0[i],offset_0,i+1)
        else:
            cache_0,cache_1,mem_list=cache_op_miss(cache_0,cache_1,mem_list,index_0,tag_0,op_0[i],offset_0,i+1)

        cache_1_hit,none=cache_HorM(cache_set=cache_1[index_1],tag=tag_1)
        
        print("cache_1_hit==",cache_1_hit)

        if(cache_1_hit!=-1):
            cache_1,cache_0,mem_list=cache_op_hit(cache_1,cache_0,mem_list,index_1,tag_1,cache_1_hit,op_1[i],offset_1,i+1)
        else:
            cache_1,cache_0,mem_list=cache_op_miss(cache_1,cache_0,mem_list,index_1,tag_1,op_1[i],offset_1,i+1)
    
        

    print('第%d次cache_0操作后cache set如下'%(i+1))
    print(cache_set_print(cache_0,index_0,offset_0))
    print('第%d次cache_1操作后cache set如下'%(i+1))
    print(cache_set_print(cache_1,index_1,offset_1))
    print(mem_print(mem_list[tag_0][index_0],tag_0,index_0,offset_0))
    print('#################################################### 第%d次操作分割线 ####################################################'%(i+1) )

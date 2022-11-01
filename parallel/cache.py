'''
based on python 3.7
need prettytable
if you don't have run :pip install prettytable
'''
###read instruction for every core###
from os import read
from random import randint
from prettytable import PrettyTable

cacheline_num = 2   #each core has 2 cachelines
cacheline_size = 64
memory_line_num = 9 #9 memory lines
DO_Nothing = 4096-1 # addr = 4095(0xfff) means do nothing
NOT_Used = 4096-1   # 4095  means cacheline is not used

core0 = []  #core0 instruction list
core1 = []
core2 = []
core3 = []
class Instruction:
    def __init__(self):
        self.r_w = 0    #0 means read,1 means write
        self.addr:int = DO_Nothing # addr = 4095(0xfff) means do nothing
        self.block_addr = DO_Nothing # 64byte block addr
        self.data = "None"

print("Please input test name (base/test1/test2):")
print("\tbase:basic test required in homework.")
print("\ttest1:test for cache miss when cacheline is full(cacheline's state is M).")
print("\ttest2:test for cache miss when cacheline is full(Only cacheline's state is S and memory's is S).")
filename = input()

for temp in range(0,4):                             #deal with each core
    with open('trace'+str(temp)+"_"+filename+'.txt','r') as f:   #open each instruction file
        for line in f:                              #read each line(instruction) in list
            line = line.rstrip('\n')                #remove the \n in the last of string
            string = line.split(" ",-1)
            #append one instruction: [0/1 addr]
            instruction_temp = Instruction()
            instruction_temp.r_w = int(string[0])
            instruction_temp.addr = int(string[1],16)
            instruction_temp.data = string[2]
            eval('core'+str(temp)).append(instruction_temp)

###data define and initial of cache and memory###

#cacheline has four state: M S I(1,2,3)
class Cacheline:
    def __init__(self):
        self.addr = NOT_Used  # 4095  means cacheline is not used
        self.state = 'I'    # 'I'   means cacheline is not used
        self.data = "None"
#initial four core-caches,which has two cachelines
core0_cache = [Cacheline(), Cacheline()] #the item number here should be same with cacheline_num  
core1_cache = [Cacheline(), Cacheline()]
core2_cache = [Cacheline(), Cacheline()]
core3_cache = [Cacheline(), Cacheline()]
cores_cache = [core0_cache, core1_cache, core2_cache, core3_cache]
#each memoryline has one addr,four flags to cores and one statement 
class Memory_line:
    def __init__(self):
        self.addr = 0
        self.core0 = 0
        self.core1 = 0
        self.core2 = 0
        self.core3 = 0
        self.state = 'M'
        self.data = "None"
#initial one memory, which has 9 memorylines
memory = []
for i in range(0,memory_line_num):
    temp = Memory_line()
    temp.addr = i*cacheline_size
    temp.data = str(i*cacheline_size)
    memory.append(temp)



def hit_M(hit_cacheline_index,core_k,instruction:Instruction):
    #function deal with hit cacheline and it's state is M
    '''write data to cache or read from cache here'''
    pass
    return 0
def hit_S(hit_cacheline_index,core_k,instruction:Instruction):
    #function deal with hit cacheline and it's state is S
    if instruction.r_w == 0:
        ###Read###
        '''read data from cache here'''
        pass
    else:
        ###Write###
        memory_line:Memory_line =  memory[instruction.block_addr//cacheline_size]
        for i in range(0,4):
            if i == core_k:
                #WI       
                # no need to deal with address
                #write data(if need)
                '''write data to cache here'''
                cores_cache[i][hit_cacheline_index].data = instruction.data
                cores_cache[i][hit_cacheline_index].state = 'M' # cacheline state change
                exec("memory_line.core"+str(i)+" = 1")             # memory flag change(unnecessary) 
            else:
                #Wr
                if eval('memory_line.core'+str(i)+"== 1") :
                    #corei has cacheline and must be state 'S'
                    for line in range(0,cacheline_num):
                        if cores_cache[i][line].addr == instruction.block_addr:
                            cores_cache[i][line].state = 'I'
                            cores_cache[i][line].addr = NOT_Used
                            exec("memory_line.core"+str(i)+" = 0")
                            break
                else:
                    #corei has no cacheline
                    pass
        #Wr for mem
        if memory_line.state == 'S':
            memory_line.state = 'I'
        else:
            # memory_line.state must be 'I' and no change
            pass
    return 0

def miss_I(I_cacheline_index,core_k,instruction:Instruction):
    #function deal with miss cacheline but find one cacheline with state 'I'(not used)
    memory_line:Memory_line =  memory[instruction.block_addr//cacheline_size]
    if instruction.r_w == 0:
        ###Read##
        
        for i in range(0,4):
            if i == core_k:
                #RI
                #copy address from memory
                cores_cache[i][I_cacheline_index].addr = instruction.block_addr
                ##read data(if need)
                '''read data to cache here(from M of S)'''  
                if eval("memory_line.state == 'S'") or eval("memory_line.state == 'M'"):
                    #copy data from memory
                    cores_cache[i][I_cacheline_index].data = memory_line.data
                else:
                    #copy data from other cache
                    for x in range(0,4):
                        if eval('memory_line.core'+str(x)+" == 1"):
                            for line in range(0,cacheline_num):
                                if cores_cache[x][line].addr == instruction.block_addr:
                                    cores_cache[i][I_cacheline_index].data = cores_cache[x][line].data #copy data from M/S
                cores_cache[i][I_cacheline_index].state = 'S' # cacheline state change
                exec("memory_line.core"+str(i)+" = 1")             # memory flag change(unnecessary) 
            else:
                #Rr
                if eval('memory_line.core'+str(i)+" == 1"):
                    #corei has cacheline and can be state 'M'/'S'
                    for line in range(0,cacheline_num):
                        if cores_cache[i][line].addr == instruction.block_addr:
                            if cores_cache[i][line].state == 'M':
                                cores_cache[i][line].state = 'S'
                                ##no need to change addr and memory flag
                                break #only one M(no S)
                            else:
                                ##no need to change addr state and memory flag
                                pass #not only one S 
                else:
                    #corei has no cacheline
                    pass
        #Rr for mem (can be M S)
        if memory_line.state == 'M':
            memory_line.state = 'S'
        else:
            # memory_line.state must be 'S' and no change
            pass
    else:
        ###Write
        for i in range(0,4):
            if i == core_k:
                #WI
                #copy address from memory
                cores_cache[i][I_cacheline_index].addr = instruction.block_addr
                ##write data(if need)
                '''write data to cache here''' 
                cores_cache[i][I_cacheline_index].data = instruction.data
                cores_cache[i][I_cacheline_index].state = 'M' # cacheline state change
                exec("memory_line.core"+str(i)+" = 1")             # memory flag change(unnecessary) 
            else:
                #Wr
                if eval('memory_line.core'+str(i)+" == 1"):
                    #corei has cacheline and can be state 'M'/'S'
                    for line in range(0,cacheline_num):
                        if cores_cache[i][line].addr == instruction.block_addr:
                            cores_cache[i][line].state = 'I'
                            cores_cache[i][line].addr = NOT_Used
                            exec("memory_line.core"+str(i)+" = 0") 
                else:
                    #corei has no cacheline
                    pass
        #Rr for mem (can be M S)
        memory_line.state = 'I'
    return 0
def miss(core_k,instruction:Instruction):
    #function deal with miss cacheline
    cache_line_index = randint(0,cacheline_num-1) #random int to define which cacheline to be replaced
    #this memory_line is according to the cache need to write back
    memory_line:Memory_line =  memory[cores_cache[core_k][cache_line_index].addr//cacheline_size]
    if cores_cache[core_k][cache_line_index].state == 'M':
        #write back this cacheline ---WB policy---
        '''write back data to memory here'''
        memory_line.data = cores_cache[core_k][cache_line_index].data
        cores_cache[core_k][cache_line_index].addr = NOT_Used
        cores_cache[core_k][cache_line_index].state = 'I'
        exec("memory_line.core"+str(core_k)+" = 0")
        memory_line.state = 'M'
        #now can use miss_I to deal with
        miss_I(cache_line_index, core_k, instruction)

    else:
        # state must be 'S' and there will be other 'S'
        S_num = 0 # S number in cache and memory
        if memory_line.state == 'S':
            S_num = S_num + 1
        for i in range(0,4):
            S_num = S_num + eval('memory_line.core'+str(i))
        #if S_num >= 3 we need do nothing 
        #but if S_num = 2 we need change another S to M
        if S_num >= 3:
            '''invalid this cache here'''
            cores_cache[core_k][cache_line_index].addr = NOT_Used
            cores_cache[core_k][cache_line_index].state = 'I'
            exec("memory_line.core"+str(core_k)+" = 0")
            #now can use miss_I to deal with
            miss_I(cache_line_index, core_k, instruction)
        else:
            #S_num must be 2 
            memory_S = 1
            for i in range(0,4):
                if i != core_k and eval('memory_line.core'+str(i)+"== 1") :
                    #find another core i which has cache state S need change to M
                    for line in range(0,cacheline_num):
                        if cores_cache[i][line].addr == memory_line.addr:
                            #find cacheline is 'line'
                            #only change state to M
                            cores_cache[i][cache_line_index].state = 'M'
                            memory_S = 0
                            break
                    break
                else:
                    pass
            if memory_S == 1:
                #another S is memory(need change to M) 
                memory_line.state = 'M'
            '''invalid this cache here'''
            cores_cache[core_k][cache_line_index].addr = NOT_Used
            cores_cache[core_k][cache_line_index].state = 'I'
            exec("memory_line.core"+str(core_k)+" = 0")
            #now can use miss_I to deal with
            miss_I(cache_line_index, core_k, instruction)
    return 0
###deal with each instruction###
def dealwith(instruction:Instruction, core_k:int):
    #calculate the 64byte block address
    addr_block:int = instruction.addr - instruction.addr%cacheline_size
    instruction.block_addr = addr_block 

    #find if hit cache(S and M state)
    hit = 0 #miss
    hit_cacheline_index = 0
    for i in range(0,cacheline_num):
        if cores_cache[core_k][i].addr == addr_block:
            hit = 1
            hit_cacheline_index = i
            break

    if hit == 1:
        #hit cacheline
        if cores_cache[core_k][hit_cacheline_index].state == 'M':
            hit_M(hit_cacheline_index, core_k, instruction)
        else:
            hit_S(hit_cacheline_index, core_k, instruction)
    else :
        #miss cacheline
        have_I = 0 #no cacheline's state is 'I'
        I_cacheline_index = 0
        for i in range(0,cacheline_num):# find one cacheline's state is 'I' and replace it
            if cores_cache[core_k][i].state == 'I':
                have_I = 1
                I_cacheline_index = i
                break
        if have_I == 1:
            miss_I(I_cacheline_index, core_k, instruction)
        else:
            miss(core_k, instruction)
    return 0

###print the statement of cache and memory
def print_state():
    #print 4 caches
    table_cache = PrettyTable()
    for core in range(0,4):
        table_cache.title = "cache of core"+str(core)
        table_cache.field_names = ["address", "state", "data"]
        for i in range(0, cacheline_num):
            table_cache.add_row([hex(cores_cache[core][i].addr), cores_cache[core][i].state, cores_cache[core][i].data])
        print(table_cache)
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        table_cache.clear()
    #print memory
    table_memory = PrettyTable()
    table_memory.title = "Memory state"
    table_memory.field_names = ["address", "core0_flag", "core1_flag", "core2_flag", "core3_flag", "state", "data"]
    for line in range(0, memory_line_num):
        table_memory.add_row([ hex(memory[line].addr), memory[line].core0, memory[line].core1, memory[line].core2, memory[line].core3, memory[line].state, memory[line].data ])
    print(table_memory)
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")
    return 0

###Cpu takes turns to get Interconnect access
maxnumber = max([len(core0), len(core1), len(core2), len(core3)]) #find max instruction-list length
for i in range(0,maxnumber):
    if i < len(core0) and core0[i].addr != DO_Nothing:
        # core0 still has instruction & the instruction is not do nothing 
        dealwith(instruction = core0[i], core_k = 0)
        #print_state()
    if i< len(core1) and core1[i].addr != DO_Nothing:
        dealwith(instruction = core1[i], core_k = 1)
        #print_state()
    if i < len(core2) and core2[i].addr != DO_Nothing: 
        dealwith(instruction = core2[i], core_k = 2)
        #print_state()
    if i< len(core3) and core3[i].addr != DO_Nothing:
        dealwith(instruction = core3[i], core_k = 3)
        #print_state()
    print("After "+str(i+1)+" round:")
    print_state()






import networkx as nx
from collections import defaultdict
from graph_gen2 import *
import random as rand
from gossips import *

# import random
# random.seed(1)

rand.seed()
from mpi4py import MPI
comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()
g_algo =FixedProb()
G = read_sfn("facebook.txt")
Nodes=[]
for i in xrange(len(G)):
    if G.node[i]['part']==rank:
        gnode = GossipNode(i, G, g_algo)
        Nodes.append(gnode)
# Nodes = gen_gsfn(100, 4, comm)
Loc_gos = defaultdict(list)
Comm_gos = defaultdict(lambda : defaultdict(list))
# for 

def gen_gossips(G, rank, Loc_gos, num_per_proc):
    #print rank
    loc_nodes = []
    for i in range(len(G)):
        if G.node[i]['part'] == rank:
            loc_nodes.append(i)
    
    for i in range(num_per_proc):
        gnode = loc_nodes.pop(rand.randint(0, len(loc_nodes)-1))
        data = rand.randint(1, 10)
        goss = Gossip(100*rank+i,data,0,gnode)
        Loc_gos[gnode].append(goss)
        #print str(rank) + ':' + str(gnode) + ' ' + str(goss)

time =0
end_time=300
dt=1
# if rank == 1:
#     goss = Gossip(1,2,0)
#     Loc_gos[4].append(goss)
gen_gossips(G, rank, Loc_gos, 3)
while(time < end_time):
        # print str(rank) + ' ' + str(time) + '\n',
        received_gossips = defaultdict(list)
        for Node in Nodes:
            gossips = Loc_gos[Node.id]
            Node.send_gossip(Loc_gos,Comm_gos,time,G,Node.id)
        # res = [len(Loc_gos[Node.id]) for Node in Nodes]
        # fres = sum(int(i) for i in res)
        # print fres
        for i in range(size):
            if rank!=i:
                comm.gather(Comm_gos[i],root=i)
            else:
                received_gossips =comm.gather(None,root=i)
        if rank==0:
            # print received_gossips
            for processor in received_gossips:
               if(processor!=None and len(processor)>0):
                      for node in processor.keys():
                            Loc_gos[node] = Loc_gos[node] + processor[node]                                           
        Comm_gos.clear()
        time = comm.bcast(time+dt, root=0)

#gen_gossips(G, rank, Loc_gos, 5)
"""
if simx.get_rank() == 1:
    goss = Gossip(1,2,0)
    Loc_gos[1].append(goss)
"""




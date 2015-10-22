import networkx as nx


# from random as rand
import simx
from collections import defaultdict
#from graph_gen2 import *
import random as rand



#position info for nodes created on this process
#setting the seed below ensures that all simulation
#generate the same graph
import random
# random.seed(1)
random.seed(1)

class GossipNode:
    def __init__(self, id, G, g_algo):
        self.id = id
        self.part = G.node[id]['part']
        self.neighbors = G.node[id]['neighbors']
        self.neighbor_list= self.neighbors.keys()
        self.sent_gossips = set()
        self.gAlgo = g_algo
        # self.gAlgo = DistProb()
        
    def send_gossip(self, Loc_gos, Comm_gos, time, G,id):
        gossips = Loc_gos[id]
        self.gAlgo.do_gossip(self, gossips, Loc_gos, Comm_gos, time, G)
    

class Gossip:
    def __init__(self, id, data, time,source):
        self.id = id
        self.data = data
        self.time = time
        self.source = source
    def __str__(self):
        return ' Gossip(' + str(self.id) + ', ' + str(round(self.data, 2)) + ', ' + str(self.time) + ') '

class LocListMsg:
    def __init__(self, pos_info):
        self.pos_info = pos_info


class GossipAlgos:
    def __init__(self):
        self.thres = 1
    def do_gossip(self,node,gossips,Loc_gos,Comm_gos,cur_time,G):
        raise NotImplementedError()


class FixedProb(GossipAlgos):
    def __init__(self,p=.5):
        self.p = p
        self.thres = 1

    def do_gossip(self,node,gossips,Loc_gos,Comm_gos,cur_time,G):
        #print str(node.gnode_id) + ' ' + str(node.sent_gossips)
        for gos in gossips:
            # print gos
            if(cur_time>=gos.time):
                if gos.id not in node.sent_gossips:
                    for neighbor in node.neighbor_list:
                        if node.id != neighbor:
                        #print '@ ' + str(simx.get_now()) + ': ' + str(neighbor)
                            if rand.random() < .5 and gos.data>self.thres:

                                newgos = Gossip(gos.id, gos.data - rand.random(), gos.time+node.neighbors[neighbor], gos.source)
                              
                                # newgos.time += node.neighbors[neighbor]
                                neighbor_part = G.node[neighbor]['part']
                                if neighbor_part == node.part:
                                        Loc_gos[neighbor].append(newgos)
                                else:
                                    Comm_gos[neighbor_part][neighbor].append(newgos)
                                #print str(cur_time) + ' ' + str(newgos.id)+ ' ' + str(node.id)+ ' ' + str(neighbor)+ ' ' + str(newgos.source)
                                print '[Time: ' + str(cur_time) + '] Sent' + str(newgos) + 'from (' + str(node.id) + ', ' + str(node.part) + ') to (' + str(neighbor) + ', ' + str(neighbor_part) + ')' 
                    node.sent_gossips.add(gos.id)
                Loc_gos[node.id].remove(gos)
       

class DistProb(GossipAlgos):
    def __init__(self):
        None
        self.thres = 1

    def do_gossip(self,node,gossips,Loc_gos,Comm_gos,cur_time,G):
        for gos in gossips:
                # print gos
            if gos.id not in node.sent_gossips:
                if(cur_time>=gos.time):
                    for neighbor in node.neighbor_list:
                        if node.id != neighbor:
                        #print '@ ' + str(simx.get_now()) + ': ' + str(neighbor)
                            if rand.random() < 3/node.neighbors[neighbor]and gos.data>self.thres:

                                newgos = Gossip(gos.id, gos.data- rand.random(), gos.time+node.neighbors[neighbor],gos.source)
                                # newgos.time += node.neighbors[neighbor]
                                neighbor_part = G.node[neighbor]['part']
                                if neighbor_part == node.part:
                                        Loc_gos[neighbor].append(newgos)
                                else:
                                    Comm_gos[neighbor_part][neighbor].append(newgos)
                                print str(cur_time) + ' ' + str(newgos.id)+ ' ' + str(node.id)+ ' ' + str(neighbor)+ ' ' + str(newgos.source)
                                # print '[Time: ' + str(cur_time) + '] Sent' + str(newgos) + 'from (' + str(node.id) + ', ' + str(node.part) + ') to (' + str(neighbor) + ', ' + str(neighbor_part) + ')' 
                    node.sent_gossips.add(gos.id)
                    Loc_gos[node.id].remove(gos)
        

class FixedFan(GossipAlgos):
    def __init__(self,k=4):
        self.k = k
        self.thres = 1

    def do_gossip(self,node,gossips,Loc_gos,Comm_gos,cur_time,G):
        for gos in gossips:
                # print gos
            if gos.id not in node.sent_gossips:
                if(cur_time>=gos.time):
                    new_rng = min(self.k, len(node.neighbor_list))
                    for i in range(new_rng):
                        rand_int = random.randint(0,len(node.neighbor_list)-1)
                        neighbor = node.neighbor_list[rand_int]
                        if node.id != neighbor and gos.data>self.thres:
                        #print '@ ' + str(simx.get_now()) + ': ' + str(neighbor)
                                newgos = Gossip(gos.id, gos.data- rand.random(), gos.time+node.neighbors[neighbor], gos.source)
                                # newgos.time += node.neighbors[neighbor]
                                neighbor_part = G.node[neighbor]['part']
                                if neighbor_part == node.part:
                                        Loc_gos[neighbor].append(newgos)
                                else:
                                    Comm_gos[neighbor_part][neighbor].append(newgos)
                                print str(cur_time) + ' ' + str(newgos.id)+ ' ' + str(node.id)+ ' ' + str(neighbor)+ ' ' + str(newgos.source)    
                                # print '[Time: ' + str(cur_time) + '] Sent' + str(newgos) + 'from (' + str(node.id) + ', ' + str(node.part) + ') to (' + str(neighbor) + ', ' + str(neighbor_part) + ')' 
                    node.sent_gossips.add(gos.id)
                    Loc_gos[node.id].remove(gos)


class HighDegree(GossipAlgos):
    def __init__(self,p=.5):
        self.p = p
        self.thres = 1

    def do_gossip(self,node,gossips,Loc_gos,Comm_gos,cur_time,G):
        p= len(node.neighbor_list)/6
        for gos in gossips:
                # print gos
            if gos.id not in node.sent_gossips:
                if(cur_time>=gos.time):
                    for neighbor in node.neighbor_list:
                        if node.id != neighbor:
                        #print '@ ' + str(simx.get_now()) + ': ' + str(neighbor)
                            if rand.random() < p and gos.data>self.thres:

                                newgos = Gossip(gos.id, gos.data- rand.random(), gos.time+node.neighbors[neighbor],gos.source)
                                # newgos.time += node.neighbors[neighbor]
                                neighbor_part = G.node[neighbor]['part']
                                if neighbor_part == node.part:
                                        Loc_gos[neighbor].append(newgos)
                                else:
                                    Comm_gos[neighbor_part][neighbor].append(newgos)
                                print str(cur_time) + ' ' + str(newgos.id)+ ' ' + str(node.id)+ ' ' + str(neighbor)+ ' ' + str(newgos.source)
                                # print '[Time: ' + str(cur_time) + '] Sent' + str(newgos) + 'from (' + str(node.id) + ', ' + str(node.part) + ') to (' + str(neighbor) + ', ' + str(neighbor_part) + ')' 
                    node.sent_gossips.add(gos.id)
                    Loc_gos[node.id].remove(gos)

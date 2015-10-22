import networkx as nx
from pymetis import part_graph
from random import randint
from mpi4py import MPI
from gossips import *
import numpy as np
import matplotlib.pyplot as plt

def gen_sfn(n, num_parts=4, min_edge=1, max_edge=10, alpha=0.5, beta=0.45, gamma=0.05, delta_in=0.2, delta_out=0, create_using=None, seed=None):
    G = nx.scale_free_graph(n=n, alpha=alpha, beta=beta, gamma=gamma, delta_in=delta_in, delta_out=delta_out, create_using=create_using, seed=seed)
    adjacency = {}
    neighbors = {}
    for i in range(len(G)):
        adjacency[i] = []
        nbrs = {}
        for j in G.neighbors(i):
            adjacency[i].append(j)
            nbrs[j] = randint(min_edge, max_edge)
        neighbors[i] = nbrs
        
    cuts, part_vert = part_graph(num_parts, adjacency)
    nx.set_node_attributes(G, 'neighbors', neighbors)
    
    parts = {}
    for i in range(len(part_vert)):
        parts[i] = part_vert[i]
        
    nx.set_node_attributes(G, 'part', parts)
    
    return G

def gen_social_sfn(filename,num_parts,min_edge=1, max_edge=10, alpha=0.5, beta=0.45, gamma=0.05, delta_in=0.2, delta_out=0, create_using=None, seed=None):
    f = open(filename, 'r')
    if(f):
        neighbors = {}
        parts = {}
        G = nx.Graph()
        for line in f:
            elems = line.split(' ')
            i = int(elems[0].strip())-1
            j= int(elems[1].strip())-1
            G.add_edge(i,j)
           
        # nx.set_node_attributes(G, 'part', parts)
        # nx.set_node_attributes(G, 'neighbors', neighbors)
        adjacency = {}
        neighbors = {}
        for i in range(len(G)):
            adjacency[i] = []
            nbrs = {}
            for j in G.neighbors(i):
                adjacency[i].append(j)
                nbrs[j] = randint(min_edge, max_edge)
            neighbors[i] = nbrs
            
        cuts, part_vert = part_graph(num_parts, adjacency)
        nx.set_node_attributes(G, 'neighbors', neighbors)
        
        parts = {}
        for i in range(len(part_vert)):
            parts[i] = part_vert[i]
            
        nx.set_node_attributes(G, 'part', parts)
        
        f.close()
        return G

def gen_write_sfn(n, num_parts, comm, g_algo=FixedProb(), min_edge=1, max_edge=10, alpha=0.5, beta=0.45, gamma=0.05, delta_in=0.2, delta_out=0, create_using=None, seed=None):
    rank = comm.Get_rank()
    size = comm.Get_size()
    if rank == 0:
        G = gen_sfn(n, num_parts)
        write_sfn(G, 'graph_' + str(n) + '.txt')
        
        gnode_parts = [[] for i in range(size)]
        for i in range(n):
            gnode = GossipNode(i, G, g_algo)
            gnode_parts[gnode.part].append(gnode)
    else:
        gnode_parts = None
              
    gnodes = comm.scatter(gnode_parts, root=0)
    G = comm.bcast(G, root=0)
    #assert data == (rank+1)**2
    
    return gnodes, G

def write_sfn(G, filename):
    f = open(filename, 'w')
    if(f):
        for i in range(len(G)):
            line = str(i) + ' : ' + str(G.node[i]['part']) + ' : '
            nnbrs = len(G.node[i]['neighbors'])
            n = 1
            for nbr in G.node[i]['neighbors']:
                line += str(nbr) + ' ' + str(G.node[i]['neighbors'][nbr])
                if n < nnbrs:
                    line += ', '
                n += 1
            line += '\n'
            f.write(line)
    f.close()

def write_sfn_nopart(G, filename):
    f = open(filename, 'w')
    if(f):
        for i in range(len(G)):
            line = str(i) + ' : '
            nnbrs = len(G.node[i]['neighbors'])
            n = 1
            for nbr in G.node[i]['neighbors']:
                line += str(nbr) + ' ' + str(G.node[i]['neighbors'][nbr])
                if n < nnbrs:
                    line += ', '
                n += 1
            line += '\n'
            f.write(line)
    f.close()

def read_sfn(filename):
    f = open(filename, 'r')
    if(f):
        neighbors = {}
        parts = {}
        G = nx.Graph()
        for line in f:
            elems = line.split(':')
            i = int(elems[0].strip())
            G.add_node(i)
            parts[i] = int(elems[1].strip())
            nbrs_str = elems[2].split(',')
            nbrs = {}
            for nbr_str in nbrs_str:
                edge = nbr_str.split()
                if len(edge) == 2:
                    node = int(edge[0].strip())
                    wt = int(edge[1].strip())
                    nbrs[node] = wt
            neighbors[i] = nbrs
            
        f.close()
        nx.set_node_attributes(G, 'part', parts)
        nx.set_node_attributes(G, 'neighbors', neighbors)
        
        return G
        
def read_sfn_addparts(filename, num_parts, comm, g_algo=FixedProb()):
    f = open(filename, 'r')
    if(f):
        neighbors = {}
        parts = {}
        adjacency = {}
        G = nx.Graph()
        for line in f:
            elems = line.split(':')
            #print elems[0].strip()
            i = int(elems[0].strip())
            G.add_node(i)
            nbrs_str = elems[1].split(',')
            nbrs = {}
            adjacency[i] = []
            for nbr_str in nbrs_str:
                edge = nbr_str.split()
                if len(edge) == 2:
                    node = int(edge[0].strip())
                    wt = int(edge[1].strip())
                    adjacency[i].append(node)
                    nbrs[node] = wt
            neighbors[i] = nbrs
            
        f.close()
        
        cuts, part_vert = part_graph(num_parts, adjacency)
        for i in range(len(part_vert)):
            parts[i] = part_vert[i]
        
        nx.set_node_attributes(G, 'part', parts)
        nx.set_node_attributes(G, 'neighbors', neighbors)
        
        rank = comm.Get_rank()
        gnodes = []
        for i in range(len(G)):
            if G.node[i]['part'] == rank:
                gnode = GossipNode(i, G, g_algo)
                gnodes.append(gnode)
        
        return gnodes, G
    
if __name__ == "__main__":
    #G = gen_social_sfn("facebook.out",4)
    
    #G = gen_sfn(10000, 4)
    #write_sfn(G, "graph_10000.txt")
    """
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    if rank == 0:
        G = gen_sfn(100000)
        write_sfn_nopart(G, "graph_100000_np.txt")
    #gnodes, G1 = read_sfn_addparts("graph_10_np.txt", 4, comm)
    #print str(comm.Get_rank()) + ' ' + str(gnodes)
    """
    G = gen_sfn(100000)
    write_sfn_nopart(G, "graph_100000_np.txt")
    """
    for i in range(len(G)):
        print i, G.node[i]['part'], G.node[i]['neighbors']
    
    #write_sfn(G, "temp_graph.txt")
    G1 = read_sfn("temp_graph.txt")
    print "###########################################"
    for i in range(len(G1)):
        print i, G1.node[i]['part'], G1.node[i]['neighbors']
    """
    """
    G = read_sfn("graph_10000.txt")
    degree = []
    for i in range(len(G)):
        degree.append(len(G.node[i]['neighbors']))
        
    n, bins, patches = plt.hist(degree, 50, normed=1, facecolor='blue', alpha=0.75)
    """    

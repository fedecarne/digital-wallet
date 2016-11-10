import Queue
from collections import deque
import time
import csv
import numpy
from collections import defaultdict
from scipy import stats
from math import sqrt
  
def breadth_first_search(adjlist,node1,node2,degree_limit):
  """
  Use a modified bidirectional bfs to test whether the distance between two nodes is greater than a given value.
     
    arguments: 
          adjlist: (dict) adjacency list of the graph
          node 1: (int) node 1 to test
          node 2: (int) node 2 to test
          degree_limit: (int) reference degree to test 
    
    output: 
          1 if degree of separation of nodes 1 and 2 is greater than degree_limit    
          0 if degree of separation of nodes 1 and 2 is equal or less than degree_limit
  """
  
  
  # Handle equal node case
  if node1==node2: return 0
  
  # Handle nodes not in the graph
  # This means the user is new (is not in the batch payment file)
  # therefore his degree of friendship is infinite (greater than anything degree_limit)
  if node1 not in adjlist: return 1
  if node2 not in adjlist: return 1    
  
  queue1 = deque([node1])
  queue2 = deque([node2])
  
  discovered1 = set([node1]) # set of nodes already discovered going forward
  discovered2 = set([node2]) # set of nodes already discovered going backwards
  
  successors1 = set([node1]) # set of successors of a given node
  successors2 = set([node2]) # set of successors of a given node
      
  d=0

  while queue1 and queue2:
         
    # Forward search step, covering entire breadth
    # this is a loop over the successors discovered in the previous forward iteration
    for i in range(len(successors1)):
      
      current_node = queue1.popleft()
      successors1 = adjlist[current_node]     
      
      # Discover and enqueue successors
      for nbr in successors1:
        if nbr not in discovered1:
          discovered1.add(nbr)
          queue1.extend([nbr])
      
      # Check if current successors intersec with backward frontier 
      if set.intersection(successors1,discovered2):
        return 0
          
    d=d+1 # Increment depth
        
    # Check degree limit
    if d>degree_limit-1:
      return 1 # Quit if current depth is higher than degree_limit
      
    # Backward search step, covering entire breadth 
    # this is a loop over the successors discovered in the previous back iteration
    for i in range(len(successors2)):

      current_node = queue2.popleft()
      successors2 = adjlist[current_node]

      # Discover and enqueue successors
      for nbr in successors2:        
        if nbr not in discovered2:
          discovered2.add(nbr)
          queue2.extend([nbr])
      
      # Check if current successors intersec with forward frontier 
      if set.intersection(successors2,discovered1):        
        return 0
          
    d=d+1 # Increment depth


    # Check degree limit
    if d>degree_limit-1:      
      return 1 # Quit if current depth is higher than degree_limit

  return 1
  
  
def edge_to_adj(edgelist_u,edgelist_v):
  """
  Builds adjacency list from list of edges
  
    arguments: 
          edgelist_u: (list) list of node1 in edge
          edgelist_u: (list) list of node2 in edge
    
    output: 
          adj_list: (dict) adjacency list

  """
  
  adj_list = defaultdict(set)
    
  # Creates a dictionary of nodes (users) with a set of edges for each one
  for i in range(len(edgelist_u)):
    u = edgelist_u[i]
    v = edgelist_v[i]
    adj_list[u].add(v)
    adj_list[v].add(u)
  
  return adj_list
    
    
def extract_users(filename):
  """
  Extracts user's id from batch_payment file
  
    arguments: 
          filename: (str) batch payment file name
              
    output: 
          user1: (list) list of users 1
          user2: (list) list of users 2
  """
    
  user1=[]
  user2=[]
  with open(filename, 'rU') as csvfile:
    reader = csv.DictReader(csvfile,fieldnames = ( "time","user1","user2","amount","message" ), delimiter=',', skipinitialspace=True, quoting=csv.QUOTE_NONE)
    reader.next() # Skip file header
    for row in reader:
      if valid_row(row):
        user1.append(row['user1'])
        user2.append(row['user2'])
  
  return user1, user2
  
  
def process_feature_1to3(stream_filename,output_filename,adj_list,degree_limit):
  """
  Processes each transaction from stream payment file, checking for trusted or unverified
  
    arguments: 
          stream_filename: (str) stream payment file name
          output_filename: (str) output file name
          adj_list: (dict) adjacency list of payment network
          degree_limit: (int) degree limit with which to compare the degree of friendship
              
    output: 
        (none)
          
  """

  with open(stream_filename, 'rU') as csvfile:
    reader = csv.DictReader(csvfile,fieldnames = ( "time","user1","user2","amount","message" ), delimiter=',', skipinitialspace=True, quoting=csv.QUOTE_NONE)
    reader.next() # Skip file header 
    for row in reader:
      # Check if payment is trusted or unverified
      r = breadth_first_search(adj_list,row['user1'],row['user2'],degree_limit)

      # Writes result for each payment in output file
      write_output(output_filename,r)
  
  
def write_output(filename,r):
  """
  Writes trusted or unverified in output file
  
    arguments: 
          filename: (str) output file name
          r: (int) 1: unverified, else trusted
          
    output: 
          (none)
          
  """
  with open(filename, "a") as text_file:
    if r==1:
      text_file.write("unverified\n")      
    elif r==0:
      text_file.write("trusted\n")
    else:
      text_file.write("unknown\n")
      
      
          
def process_feature_4(stream_filename,output_filename,w_adjlist,distance_limit):
  """
  Processes each transaction from stream payment file, checking for trusted or unverified
  by ccomputing shortest path in weighted graph
  
    arguments: 
          stream_filename: (str) stream payment file name
          output_filename: (str) output file name
          user_stats: (dict) user statistics
              
    output: 
          (none)
  """
  
  with open(stream_filename, 'rU') as csvfile:
    reader = csv.DictReader(csvfile,fieldnames = ( "time","user1","user2","amount","message" ), delimiter=',', skipinitialspace=True, quoting=csv.QUOTE_NONE)
    reader.next() # Skip file header 
    for row in reader:
      # Computes the shortes distances between users in the weightd graph
      r = dijkstra(w_adjlist,row['user1'],row['user2'],distance_limit)
      # Writes result for each payment in output file      
      write_output(output_filename,r)                            


def dijkstra(w_adjlist,node1,node2,distance_limit):
  """
  Use Dijkstra algorithm to find shortest distance between two nodes
     
    arguments: 
          adjlist: (dict) adjacency list of the graph
          node 1: (int) node 1 to test
          node 2: (int) node 2 to test
    
    output: 
          1 if degree of separation of nodes 1 and 2 is greater than degree_limit    
          0 if degree of separation of nodes 1 and 2 is equal or less than degree_limit
  """

  # Handle equal node case
  if node1==node2: return 0
    
  # Handle nodes not in the graph
  # This means the user is new (is not in the batch payment file)
  # therefore his degree of friendship is infinite (greater than anything degree_limit)
  if node1 not in w_adjlist: return 1
  if node2 not in w_adjlist: return 1 

  #Initialize
  queue = Queue.PriorityQueue()
    
  distances={}
  distances[node1] = 0
        
  queue.put(([0, node1]))
  frontier = set([(node1)]) 
        
  while not queue.empty():

    # check for distance threshold
    a = []
    for element in frontier:
      if distances[element]<distance_limit:
        break # Continue search only if at least one nodes in the frontier is less that threshols
    else:
      return 1
      
    current_tuple = queue.get()
    current_node = current_tuple[1]

    frontier.remove(current_node)
    
    if current_node == node2:
      return 0 # node 1 met node2!
      
    for nbr in w_adjlist[current_node]:
    
      tentative_distance = distances[current_node] + w_adjlist[current_node][nbr]
      if nbr not in distances.keys() or distances[nbr] > tentative_distance:
        distances[nbr] = tentative_distance
        queue.put(([distances[nbr], nbr]))
        frontier.add(nbr)
        
  return 1 # not found


def generate_w_adj_list(filename):
  """
  Builds weighted adjacency list from bath_payment file. 
  Weights are inversely proportional to the amount of transactions between users.
  
    arguments: 
          filename: (str) batch_payment file name
    
    output: 
          adj_list: (dict) adjacency list

  """
  adj_list = {}

  with open(filename, 'rU') as csvfile:
    reader = csv.DictReader(csvfile,fieldnames = ( "time","user1","user2","amount","message" ), delimiter=',', skipinitialspace=True, quoting=csv.QUOTE_NONE)
    reader.next() # Skip file header
    for row in reader:
      if valid_row(row):
        if row['user1'] in adj_list:
          if row['user2'] in adj_list[row['user1']]:
            adj_list[row['user1']][row['user2']] +=1
          else:
            adj_list[row['user1']][row['user2']] = 1 
        else:
          adj_list[row['user1']] = {row['user2']:1}
        if row['user2'] in adj_list:
          if row['user1'] in adj_list[row['user2']]:
            adj_list[row['user2']][row['user1']] +=1
          else:
            adj_list[row['user2']][row['user1']] = 1
        else:
          adj_list[row['user2']] = {row['user1']:1}
  
  for key1, value1 in adj_list.iteritems():    
    for key2, value2 in value1.iteritems():   
      adj_list[key1][key2] = 100/float(value2)      
            
  return adj_list
            
            
def compute_stats(filename):
  """
  Computes user statistics from payment history to model user behavior. 
  This is then used to compare new transactions with the model and detect fraud events
          
    arguments: 
          filename: (str) batch payment file name
            
    output:
          user_stat: (dict) dict of user with relevant statistics
  """

  user_amount = defaultdict(list)
  user_stat = defaultdict(list)
  

  with open(filename, 'rU') as csvfile:
    reader = csv.DictReader(csvfile,fieldnames = ( "time","user1","user2","amount","message" ), delimiter=',', skipinitialspace=True, quoting=csv.QUOTE_NONE)
    reader.next() # Skip file header
    for row in reader:
      if valid_row(row):
        user1 = row['user1']
        amount = float(row['amount'])        
        user_amount[user1].append(amount)

    # Compute statistics for each user
    for user1, amount in user_amount.iteritems():    
      n = len(user_amount[user1]) # number of transactions
      mu = numpy.mean(amount) # mean amount
      s = numpy.std(amount) # sdev of amount
      t = stats.t.isf(0.05/n, n-2) # 0.05 significant
      g_critic = ((n-1) / sqrt(n)) * (sqrt(t**2 / (n-2 + t**2))) #critical value to pass the test
      user_stat[user1] = [n, mu, s, g_critic]

  return user_stat     
  
  
def process_feature_5(stream_filename,output_filename,user_stats):
  """
  Processes each transaction from stream payment file, checking for trusted or unverified by comparing the payment amount with the statistics of previous payments
  
    arguments: 
          stream_filename: (str) stream payment file name
          output_filename: (str) output file name
          user_stats: (dict) user statistics
              
    output: 
  """

 
  with open(stream_filename, 'rU') as csvfile:
    reader = csv.DictReader(csvfile,fieldnames = ( "time","user1","user2","amount","message" ), delimiter=',', skipinitialspace=True, quoting=csv.QUOTE_NONE)
    reader.next() # Skip file header
    for row in reader:

         if valid_row(row):
          user1 = row['user1']
          r=0
          amount = float(row['amount'])
          if user_stats.has_key(user1): # if user has history (otherwise there is no model for him)
            if user_stats[user1][0]>2 and user_stats[user1][2]>0: # only if user has done more than one payment and std>0
              g = (amount-user_stats[user1][1])/user_stats[user1][2]
              if g>user_stats[user1][3]:
                r = 1 # unverified
          # Writes result for each payment in output file
          write_output(output_filename,r)           
                        
# Usefeul functions          
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
        
def valid_row(row):
  """
  Add row validation code here
  """    
  r=0    
  if row['user1']!=None and row['user2']!=None:
    if is_number(row['user1']) and is_number(row['user2']):
      r=1
  return r 

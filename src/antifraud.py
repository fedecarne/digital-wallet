#!/usr/bin/python -tt

"""
Solution to the Insight Data Engineering coding challenge digital-wallet

  Args:
      param1: (str) batch_payment filename
      param2: (str) stream_payment filename
      param3: (str) output 1 filename
      param4: (str) output 2 filename
      param5: (str) output 3 filename
      param6: (str) output 4 filename
      param7: (str) output 5 filename
      
To run this program:

python ./src/antifraud.py ./paymo_input/batch_payment.txt ./paymo_input/stream_payment.txt ./paymo_output/output1.txt ./paymo_output/output2.txt ./paymo_output/output3.txt ./paymo_output/output4.txt ./paymo_output/output4.txt ./paymo_output/output6.txt
  
Written by Fede Carnevale, 11/2016.


"""



import sys
import os
import csv
import time
import dwallet

def main():

  # 1. Extracts list of users from batch_payment file
  # 2. Creates adjacency list from list of users
  # 3. Read each payment from stream payment file
  # 4. Check if payment is trusted or unverified
  # 5. Writes result for each payment in output file
  
  batch_filename = sys.argv[1]
  stream_filename = sys.argv[2]
  output1_filename = sys.argv[3]
  output2_filename = sys.argv[4]
  output3_filename = sys.argv[5]
  output4_filename = sys.argv[6]
  output5_filename = sys.argv[7]

  # Remove previous result files if exist
  try:
    os.remove(output1_filename)
    os.remove(output2_filename)
    os.remove(output3_filename)
    os.remove(output4_filename)
    os.remove(output5_filename)
  except OSError:
    pass

  # Counts the number of rows in stream_payment file to compute time per transaction
  with open(stream_filename, 'rU') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', skipinitialspace=True, quoting=csv.QUOTE_NONE) 
    row_count = sum(1 for row in reader)-1 
    print 'nr of stream payments: %d' %row_count

  # 1. Extracts list of users from batch_payment.csv
  start = time.time()
  user1, user2 = dwallet.extract_users(batch_filename)
  end = time.time()
  print 'extract_users: %1.3fs' %((end - start)) 

  # 2. Creates adjacency list from list of users
  start = time.time()
  adj_list = dwallet.edge_to_adj(user1,user2)
  end = time.time()
  print 'edge_to_adj: %1.3fs' %((end - start)) 
    
  #Feature 1
  degree_limit = 1
  
  start = time.time() 
  dwallet.process_feature_1to3(stream_filename,output1_filename,adj_list,degree_limit)  
  end = time.time()
  print 'feature1: %1.3fs (%3.1fus per transaction)' %((end - start),(end - start)*1000000/row_count) 

  #Feature 2
  degree_limit = 2
  
  start = time.time()  
  dwallet.process_feature_1to3(stream_filename,output2_filename,adj_list,degree_limit)
  end = time.time()
  print 'feature2: %1.3fs (%3.1fus per transaction)' %((end - start),(end - start)*1000000/row_count)
  
  #Feature 3
  degree_limit = 4
  
  start = time.time()
  dwallet.process_feature_1to3(stream_filename,output3_filename,adj_list,degree_limit)
  end = time.time()
  print 'feature3: %1.3fs (%3.1fus per transaction)' %((end - start),(end - start)*1000000/row_count)
  
  #Feature 4
  distance_limit = 2
  
  start = time.time()  
  w_adjlist = dwallet.generate_w_adj_list(batch_filename)
  end = time.time()
  print 'generate weighted adjlist %000.2f s ' %((end - start))

  start = time.time()  
  dwallet.process_feature_4(stream_filename,output4_filename,w_adjlist,distance_limit)
  end = time.time()
  print 'feature 4: %1.3fs (%3.1fus per transaction)' %((end - start),(end - start)*1000000/row_count)

  #Feature 5
  start = time.time()
  user_stats = dwallet.compute_stats(batch_filename)
  end = time.time()
  print 'compute stats: %000.2fs' %((end - start))

  start = time.time()  
  dwallet.process_feature_5(stream_filename,output5_filename,user_stats)
  end = time.time()
  print 'feature 5: %1.3fs (%3.1fus per transaction)' %((end - start),(end - start)*1000000/row_count)

  
if __name__ == '__main__':
  main()

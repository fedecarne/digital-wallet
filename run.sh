#!/usr/bin/env bash

#Solution to the Insight Data Engineering coding challenge digital-wallet
#  Args:
#      param1: batch_payment filename
#      param2: stream_payment filename
#      param3: output 1 filename
#      param4: output 2 filename
#      param5: output 3 filename
# Written by Fede Carnevale, 11/2016.

python ./src/antifraud.py ./paymo_input/batch_payment.txt ./paymo_input/stream_payment.txt ./paymo_output/output1.txt ./paymo_output/output2.txt ./paymo_output/output3.txt ./paymo_output/output4.txt ./paymo_output/output5.txt

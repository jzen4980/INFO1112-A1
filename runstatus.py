#!/usr/bin/env python3
# -*- coding: ascii -*-

import sys, os, signal

pidfile = ".runner-pid"
statusfilename = ".runner-status"

#print(open(statusfilename,'r').read())

f = open(pidfile, 'r')
try:
    pid = int(f.read())
except FileNotFoundError:
    print('File not found')
except:
    print('Error encountered')

os.kill(pid, signal.SIGUSR1)
#print(pid)
while True:
    file_size = os.stat(statusfilename).st_size
    # print(file_size)
    read_flag = file_size > 0
    if read_flag:
        print(read_flag)
        print(open(statusfilename, 'r').read())


        break


#
# open the pidfile and read the process id
#    give an error message if file not found or bad pid
# send the USR1 signal to runner.py
# open the status file for reading and check the size
# wait until it is non zero size, then read contents and copy to output, then quit.
#
# give error messages as necessary



#!/usr/bin/env python3
# -*- coding: ascii -*-

import sys, os, signal, time

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


#print(pid)
while True:
    os.kill(pid, signal.SIGUSR1)
    time.sleep(2)
    file_size = os.stat(statusfilename).st_size
    print(file_size)

    if file_size > 0:
        statusfile = open(statusfilename, 'r')
        statusfile.read()
        statusfile.close()
        break


#
# open the pidfile and read the process id
#    give an error message if file not found or bad pid
# send the USR1 signal to runner.py
# open the status file for reading and check the size
# wait until it is non zero size, then read contents and copy to output, then quit.
#
# give error messages as necessary



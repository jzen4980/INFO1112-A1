#!/usr/bin/env python3
# -*- coding: ascii -*-

import sys, os, signal, time

pidfile = ".runner-pid"
statusfilename = ".runner-status"

# print(open(statusfilename,'r').read())

f = open(pidfile, 'r')
try:
    pid = int(f.read())
except FileNotFoundError:
    print('File not found')
except:
    print('Error encountered')


os.kill(pid, signal.SIGUSR1)
f.close()
# print(pid)

while True:
    time.sleep(1)
    file_size = os.stat(statusfilename).st_size
    # print(file_size)
    if file_size > 0:
        break
status_file = open(statusfilename, 'r')
print(status_file.read())
status_file.close()


#
# open the pidfile and read the process id
#    give an error message if file not found or bad pid
# send the USR1 signal to runner.py
# open the status file for reading and check the size
# wait until it is non zero size, then read contents and copy to output, then quit.
#
# give error messages as necessary

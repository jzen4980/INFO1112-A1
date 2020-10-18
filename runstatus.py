#!/usr/bin/env python3
# -*- coding: ascii -*-

import sys, os

pidfile = ".runner-pid"
statusfilename = ".runner-status"

file = 'tester'
f = open(pidfile, "r")
#f.write("hello world")

print(f.read())

#
# open the pidfile and read the process id
#    give an error message if file not found or bad pid
# send the USR1 signal to runner.py
# open the status file for reading and check the size
# wait until it is non zero size, then read contents and copy to output, then quit.
#
# give error messages as necessary



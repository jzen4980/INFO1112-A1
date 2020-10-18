#!/usr/bin/env python3
# -*- coding: ascii -*-

import sys, os, time, datetime, signal, re

# from datetime import datetime, timedelta

# write pid to .runner-pid
pid = os.getpid()
f = open('.runner-pid', '+w')
f.write(str(pid))
f.close()


# create class for our commands
class Command:
    def __init__(self, day, runtime, path, args, recurring=False):
        self.day = day
        self.runtime = runtime
        self.path = path
        self.args = args
        self.recurring = recurring


# reading configuration file
conf_file = 'runner.conf'
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

# list from config file
config_arr = []

# split config commands from test example
for i in open(os.path.join(__location__, conf_file)):
    if i == '\n':
        break
    else:
        config_arr.append(i.strip())

#extracts important info out of config commands
def extract(input):
    recurring = False
    days = []
    # extracts timespec
    timespec = input.partition('at')[0].split()
    recurring = False
    if timespec:
        if timespec[0] == 'every':
            recurring = True
        days = timespec[1].strip().split(',')
    # extracts runtime
    runtime = input.partition('at')[2].partition('run')[0].strip().split(',')
    #extracts path
    path = input.partition('run')[2].strip().split()[0]
    #extracts args
    args = input.partition(path)[2].strip()
    return days, runtime, path, args, recurring

test_arr = []
for i in config_arr:
    #print(i)
    raw = extract(i)
    print(extract(i))





# #split config commands into 3 categories
# at_list = []
# on_list = []
# every_list = []
#
# for i in config_arr:
#     if i.split()[0] == 'at':
#         at_list.append(i)
#     elif i.split()[0] == 'every':
#         every_list.append(i)
#     elif i.split()[0] == 'on':
#         on_list.append(i)
#     else:
#         print('Grammar error.')
#
# print(config_arr)
# print(at_list)
# print(on_list)
# print(every_list)
#
# # datetime, command, args, recurring flag?
#
# today = datetime.now()
#
# #print('today is', today)
# #print(datetime.date())
#
# #array of commands - schedule to run
# command_arr = []
#
# def at_converter(input):
#     split_input = input.split()
#     date = datetime.date()
#     time = split_input[1]
#     path = split_input[3]
#     args = split_input[4:]
#     for i in args:
#         command = Command(time, path, i)
#         command_arr.append(command)
#
#     print(date, time, path, args)
#
#
# at_converter(at_list[1])
# print(command_arr[0].runtime)

# signal.setitimer()

##while timedelta > 0: wait, else execute, pop


##TODO take difference between schedule time and current time, and sleep, when time is up, run the program. start timing next program
## to do this, we need to make list of datetimes, recurring, program
"""
The configuration file for runner.py will contain one line for each program that is to be run.   Each line has the following parts: 

timespec program-path parameters

where program-path is a full path name of a program to run and the specified time(s), parameters are the parameters for the program,
timespec is the specification of the time that the program should be run.

The timespec has the following format:

[every|on day[,day...]] at HHMM[,HHMM] run

Square brackets mean the term is optional, vertical bar means alternative, three dots means repeated.

Examples:

every Tuesday at 1100 run /bin/echo hello
	every tuesday at 11am run "echo hello"
on Tuesday at 1100 run /bin/echo hello
	on the next tuesday only, at 11am run "echo hello"
every Monday,Wednesday,Friday at 0900,1200,1500 run /home/bob/myscript.sh
	every monday, wednesday and friday at 9am, noon and 3pm run myscript.sh
at 0900,1200 run /home/bob/myprog
	runs /home/bob/myprog every day at 9am and noon


"""

#
# open the configuration file and read the lines, 
#    check for errors
#    build a list of "run" records that specifies a time and program to run
#

#
# define up the function to catch the USR1 signal and print run records
#

#
# sort run records by time
# take the next record off the list and wait for the time, then run the program
# add a record to the "result" list
# if this was an "every" record", add an adjusted record to the "run" list 
#
# repeat until no more to records on the "run" list, then exit
#

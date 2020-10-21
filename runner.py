#!/usr/bin/env python3
# -*- coding: ascii -*-

import sys, os, time, datetime, signal, re

from datetime import datetime as dt
from datetime import date, timedelta

# write pid to .runner-pid
pid = os.getpid()
f = open('.runner-pid', '+w')
f.write(str(pid))
f.close()


# create class for our commands - this holds all important information we need to run our processes
class Command:
    def __init__(self, scheduleDatetime, path, args, recurring, atFlag, ranFlag=False):
        # time process is scheduled to run
        self.scheduleDatetime = scheduleDatetime
        # path of process to be run
        self.path = path
        # args of process to be run
        self.args = args
        # flag for whether process should recur?
        self.recurring = recurring
        # flag for whether a command starts with 'at' - this impacts how we handle time pass cases
        self.atFlag = atFlag
        # flag for whether process has run
        self.ranFlag = ranFlag


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


# extracts important info out of config commands
def extract(input):
    days = []
    # extracts timespec
    timespec = input.partition('at')[0].split()
    recurring = False
    atFlag = False
    if timespec:
        if timespec[0] == 'every':
            recurring = True
        days = timespec[1].strip().split(',')
    else:
        atFlag = True
    # extracts runtime
    times = input.partition('at')[2].partition('run')[0].strip().split(',')
    # extracts path
    path = input.partition('run')[2].strip().split()[0]
    # extracts args
    args = input.partition(path)[2].strip()
    return days, times, path, args, recurring, atFlag


##TODO outputs in form of 'will run at Tue Oct 20 ... (datetime) path args

todayDateTime = datetime.datetime.now()
todayDate = todayDateTime.date()

#print('Todays date:', todayDate)

day_name2num = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6}
day_num2name = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
todayName = day_num2name[date.today().weekday()]
todayNum = day_name2num[todayName]


# converts raw days and times into datetime value
def convertDatetime(rawDays, rawTimes):
    times = []
    dates = []
    datetimes = []
    # extract days
    if rawDays:
        for i in rawDays:
            dayNum = int(day_name2num[i])
            diff = dayNum - todayNum
            runDate = todayDate + datetime.timedelta(days=diff)
            dates.append(runDate)
    # default to today
    else:
        dates.append(todayDate)
    # print(dates)
    for i in rawTimes:
        hr = int(i[:2])
        min = int(i[2:])
        times.append(datetime.time(hr, min))
    for i in dates:
        for j in times:
            datetimes.append(dt.combine(i, j))
    return datetimes


# this will store list of command objects
command_list = []

for i in config_arr:
    days, times, path, args, recurring, atFlag = extract(i)
    scheduleDatetime = convertDatetime(days, times)
    # creating command for each schedule datetime - stores in command_list
    for j in scheduleDatetime:
        command_list.append(Command(j, path, args, recurring, atFlag))

# sorting command list
command_list.sort(key=lambda x: x.scheduleDatetime)

# runs os.fork
def runProcess(path, args):
    # print(path,args)
    newpid = os.fork()
    if newpid == 0:
        # print('hi im the child')
        os.execl(path, args)
        sys.exit(99)
    elif newpid == -1:
        print('error has occurred')
        sys.exit(1)
    else:
        # print('im the parent')
        os.wait()
        # pids = (os.getpid(), newpid)
        # print("parent: %d, child: %d\n" % pids)
    return



def runCommand(commands):
    for i in commands:
        today = todayDateTime
        # find next process that hasnt been run
        if i.ranFlag == True:
            continue
        # 'at' time pass condition - reschedule for tomorrow
        if i.atFlag == True and today > i.scheduleDatetime:
            i.scheduleDatetime += datetime.timedelta(days=1)
            # print('at flag time pass')
            break
        # 'on/every' time pass condition - reschedule for next week
        elif i.atFlag == False and today > i.scheduleDatetime:
            i.scheduleDatetime += datetime.timedelta(weeks=1)
            # print('time pass')
            break
        # schedules recurring process for next week
        if i.recurring == True:
            newScheduleDatetime = i.scheduleDatetime + datetime.timedelta(weeks=1)
            command_list.append(Command(newScheduleDatetime, i.path, i.args, i.recurring, i.atFlag, i.ranFlag))

        # print('command tb run:',i.scheduleDatetime, i.path, i.args, i.recurring, i.atFlag, i.ranFlag)
        # sleep program until it's time to run next program
        time.sleep((i.scheduleDatetime - today).total_seconds())
        # do something
        #print(i.scheduleDatetime)

        runProcess(i.path, i.args)
        # print('command ran:',i.scheduleDatetime, i.path,i.args)
        # mark process as done
        i.ranFlag = True
        break


def run():
    while True:
        command_list.sort(key=lambda x: x.scheduleDatetime)
        num_finished = 0
        for i in command_list:
            if i.ranFlag ==True:
                num_finished +=1
                #print('already ran',i.scheduleDatetime, i.path, i.args)
        if num_finished == len(command_list):
            break
        else:
            runCommand(command_list)



def main():
    run()

if __name__ == "__main__":
    main()





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

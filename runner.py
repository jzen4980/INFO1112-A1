#!/usr/bin/env python3
# -*- coding: ascii -*-

import sys, os, time, datetime, signal, re

from datetime import datetime as dt
from datetime import date, timedelta


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

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

# extracts important info out of config commands
def extract(input):
    if 'run' not in input:
        eprint("no run keyword")
        sys.exit()
    days = []
    # extracts timespec
    datespec = input.partition('at ')[0].split()
    recurring = False
    atFlag = False
    if datespec:
        if datespec[0] == 'every':
            recurring = True
        days = datespec[1].strip().split(',')
    else:
        atFlag = True
    # extracts runtime
    times = input.partition('at ')[2].partition('run')[0].strip().split(',')
    # extracts path
    try:
        path = input.partition(' run ')[2].strip().split()[0]
    except:
        eprint("program path missing")
        sys.exit()
    # extracts args
    args = input.partition(path)[2].strip().split()
    #print(days, times)
    return days, times, path, args, recurring, atFlag


# converts raw days and times into datetime value
def convertDatetime(rawDays, rawTimes):
    times = []
    dates = []
    datetimes = []
    # extract days
    #print(rawDays)
    #print(rawTimes)
    if rawDays:
        seen = []
        # check for bad syntax
        if 'every' in rawDays or ' on ' in rawDays:
            eprint('bad syntax')
            sys.exit()
        for i in rawDays:
            # check for repeated days
            if i in seen:
                eprint('repeated day')
                sys.exit()
            seen.append(i)
            # check for case
            correct_case = i[0].upper() + i[1:].lower()
            if i not in day_name2num and correct_case in day_name2num:
                eprint('incorrect dayname (case is wrong)')
                sys.exit()

            # check for valid day
            try:
                dayNum = int(day_name2num[i])
            except:
                eprint("incorrect dayname")
                sys.exit()
            diff = dayNum - todayNum
            runDate = todayDate + datetime.timedelta(days=diff)
            dates.append(runDate)
    # default to today
    else:
        dates.append(todayDate)
    # splits hrs and mins
    for i in rawTimes:
        # check time length
        if len(i) != 4:
            eprint('incorrect time')
            sys.exit()

        # check time boundary
        if int(i) > 2359:
            eprint('times range from 0000 to 2359')
            sys.exit()

        hr = int(i[:2])
        min = int(i[2:])

        #check time format
        if hr > 23 or min > 59:
            eprint('incorrect time')
            sys.exit()
        times.append(datetime.time(hr, min))
    # creates list of all date and time combos
    for i in dates:
        for j in times:
            datetimes.append(dt.combine(i, j))
    return datetimes


# runs os.fork
def runProcess(path, args, datetime):
    # print(path,args)
    eprint("error", datetime, args)
    try:
        newpid = os.fork()
        if newpid == 0:
            # print('hi im the child')
            os.execv(path, args)
            sys.exit(99)
        elif newpid == -1:
            eprint('error has occurred')
            sys.exit(1)
        else:
            # print('im the parent')
            os.wait()
            pids = (os.getpid(), newpid)
            # print("parent: %d, child: %d\n" % pids)
        return
    except:
        arg_string = ''
        for i in args:
            arg_string += i + ' '
        eprint("error", time.ctime(datetime.timestamp()), arg_string)
        sys.exit()


# runs the next command in the list
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

        runProcess(i.path, i.args, i.scheduleDatetime)
        # mark process as done
        i.ranFlag = True
        break

# signal catcher
def signal_handler(sig, frame):
    # print('Caught runstatus signal')
    f = open(".runner-status", "w+")
    for i in command_list:
        argstring = ''
        for j in i.args:
            argstring += j + ' '
        if i.ranFlag == True:
            f.write('ran ' + time.ctime(i.scheduleDatetime.timestamp()) + argstring + '\n')
        else:
            f.write('will run at ' + time.ctime(i.scheduleDatetime.timestamp()) + argstring + '\n')
    f.close()

# this is the runner function
def run():
    while True:
        command_list.sort(key=lambda x: x.scheduleDatetime)
        num_finished = 0
        # count how many have been run
        for i in command_list:
            if i.ranFlag == True:
                num_finished += 1
                # print('already ran',i.scheduleDatetime, i.path, i.args)
        # finished iterating through the list
        if num_finished == len(command_list):
            print("nothing left to run")
            sys.exit()
        else:
            # run next command
            runCommand(command_list)


# write pid to .runner-pid
pid = os.getpid()
f = open('.runner-pid', '+w')
f.write(str(pid))
f.close()

# list from config file
config_arr = []

# reading configuration file
conf_file = 'runner.conf'
try:
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))

    # split config commands from test example
    for i in open(os.path.join(__location__, conf_file)):
        if i == '\n':
            break
        else:
            config_arr.append(i.strip())

except:
    # cant find config file
    eprint("configuration file not found")
    sys.exit()

if len(config_arr) == 0:
    # empty config
    eprint("configuration file empty")
    sys.exit()


todayDateTime = datetime.datetime.now()
todayDate = todayDateTime.date()

# Constructing dictionaries for days of the week
day_name2num = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6}
day_num2name = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
todayName = day_num2name[date.today().weekday()]
todayNum = day_name2num[todayName]

# this will store list of command objects
command_list = []

# list of seen inputs for error handling
seen_inputs = []

# extract important info from config file and convert them into commands
for i in config_arr:
    if i in seen_inputs:
        eprint("duplicate run time")
        # continue - if we want to skip it and keep going
        sys.exit()
    seen_inputs.append(i)

    days, times, path, args, recurring, atFlag = extract(i)
    scheduleDatetime = convertDatetime(days, times)
    command_args = [path] + args

    # creating command for each schedule datetime - stores in command_list
    for j in scheduleDatetime:
        command_list.append(Command(j, path, command_args, recurring, atFlag))

# sorting command list
command_list.sort(key=lambda x: x.scheduleDatetime)


if __name__ == "__main__":
    signal.signal(signal.SIGUSR1, signal_handler)
    run()

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
	runs /home/bob/myprog once  at 9am and noon


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
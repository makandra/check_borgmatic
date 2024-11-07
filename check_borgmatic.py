#!/usr/bin/python3
#
# Python3 Nagios/Icinga2 plugin for borgmatic to check the last successful backup
#
# ./check_borgmatic.py -c <seconds> -w <seconds>
#

version = "0.7"

# Imports
import subprocess
import json
import datetime
import sys
import argparse
import os

# default crit, warn
warn_sec = 86400 # 1 day
crit_sec = 86400*3 # 3 days
# the following settings must fit with your sudoers entry:
command_default = ["sudo", "borgmatic", "list", "--last 1", "--json"]
command_borgmatic = ["sudo","HOME=foo borgmatic", "-nc" ] # -nc ensures no ANSI codes in the JSON
command_borg = ["borg", "list", "--last 1", "--json", "--bypass-lock"]
# We need to overwrite HOME to avoid running into the local locked cache

# init the parser
parser = argparse.ArgumentParser(description='nagios/icinga2 plugin for borgmatic to check the last successful backup.')
parser.add_argument("-V", "--version", help="show program version", action="store_true")
parser.add_argument("-c", "--critical", type=int, metavar='seconds', help="critical time since last backup (in seconds)")
parser.add_argument("-w", "--warning", type=int, metavar='seconds', help="warning time since last backup (in seconds)")
parser.add_argument("-C", "--config", help="path to configuration file")
parser.add_argument("-d", "--debug", default=False, action='store_true')
parser.add_argument("-p", "--prefix")
parser.add_argument("-B", "--bypass-lock", action="store_true")
# read arguments from the cmd line
args = parser.parse_args()
# check for --version
if args.version:
  print("check_borgmatic.py - Version:", version)
  sys.exit(0)
# check for --critical
if args.critical:
  crit_sec = int(args.critical)
# check for --warning
if args.warning:
  warn_sec = int(args.warning)

def append_parameter(string):
  command_default.append(string)
  command_borgmatic.append(string)

if args.config:
  append_parameter("--config " + args.config)

if args.prefix:
  command_default.append("--prefix " + args.prefix)
  command_borg.append("--prefix " + args.prefix)

append_parameter("--log-file /dev/null")

# Plugin start
# Try to get Data from borgmatic
if args.bypass_lock:
  command = command_borgmatic + command_borg
else:
  command = command_default

try:
  result = subprocess.run(
                        " ".join(command),
                        capture_output=True,
                        text=True,
                        shell=True,
                        check=True # returns an exception if the command errorcode isn't 0
                        )
  output = result.stdout
except:
  print("UNKNOWN - cannot get data from borgmatic!")
  sys.exit(3)

try:
  data = json.loads(output) if isinstance(json.loads(output), list) else [json.loads(output)] # load json
except:
  print("UNKNOWN - cannot decode borgmatic data!")
  sys.exit(3)

if args.debug:
  from pprint import pp
  pp(data)

if not data[0]['archives']:
  print("CRITICAL - no successful backup found!")
  sys.exit(2)

last_backup_name = data[0]['archives'][0]['name']
last_backup_time_str = data[0]['archives'][0]['time']

last_backup_time = datetime.datetime.strptime(last_backup_time_str, '%Y-%m-%dT%H:%M:%S.%f')

time_now = datetime.datetime.now()

# calculate delta
time_past = time_now - last_backup_time
time_past_sec = round(time_past.total_seconds())

# Check data: seconds
if time_past_sec < warn_sec:
  print("OK - last borgmatic backup: %s (age: %s) with name %s | 'lastbackup_s'=%s" % (last_backup_time, time_past, last_backup_name, time_past_sec))
  sys.exit(0)
elif time_past_sec > warn_sec and time_past_sec < crit_sec:
  print("WARNING - last borgmatic backup: %s (age: %s) with name %s | 'lastbackup_s'=%s" % (last_backup_time, time_past, last_backup_name, time_past_sec))
  sys.exit(1)
elif time_past_sec > crit_sec:
  print("CRITICAL - last borgmatic backup: %s (age: %s) with name %s | 'lastbackup_s'=%s" % (last_backup_time, time_past, last_backup_name, time_past_sec))
  sys.exit(2)
else:
  print("UNKOWN - last borgmatic backup: %s (age: %s) with name %s | 'lastbackup_s'=%s" % (last_backup_time, time_past, last_backup_name, time_past_sec))
  sys.exit(3)

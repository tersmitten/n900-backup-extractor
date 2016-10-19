#!/usr/bin/env python

# -*- coding: utf-8 -*-

"""

Reads the eventlogger database (el-v1.db) and writes the text messages
to an XML file compatible with the backup format used by "Backup SMS
Pro" on Android. Tested successfully importing 11,000+ SMS
messages. Blatantly ripped off from rtcom-eventlogger-export.py...


"""

import sys
import sqlite3
import csv
import string
from datetime import datetime

import utils

if len(sys.argv) != 3:
  show_usage('%s [path to el-v1.db] [path to xml file]' % sys.argv[0])

dbFileName = sys.argv[1].strip()
xmlFileName = sys.argv[2].strip()

try:
  # Try to open eventlogger database
  connection = sqlite3.connect(dbFileName)
  # Try to open csv file for writing
  outFd = open(xmlFileName, 'wb')
  count = 0
  offset = 1000
  ignored = 0

  with connection, outFd:
    cursor = connection.cursor()

    outFd.write("<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><backup><sms-backup>")
    
    sql = 'SELECT `start_time`, `end_time`, `remote_uid`, `free_text` FROM `Events` WHERE `event_type_id` = 7'
    for record in cursor.execute(sql):
      startTime, endTime, phoneNumber, textMessage = record

      startDateTime = datetime.fromtimestamp(startTime).strftime('%Y-%m-%d %H:%M:%SZ')
      msgtype = 0

      try:
        if endTime > 0:
          msgtype = 2
        else:
          msgtype = 1
        phoneNumber = string.replace(phoneNumber, "&", "&amp;")
        phoneNumber = string.replace(phoneNumber, "\"", "&quot;")
        phoneNumber = string.replace(phoneNumber, "\'", "&apos;")
        phoneNumber = string.replace(phoneNumber, "<", "&lt;")
        phoneNumber = string.replace(phoneNumber, ">", "&gt;")
        phoneNumber = phoneNumber.encode('utf-8')
        textMessage = string.replace(textMessage, "\r\n", " ") 
        textMessage = string.replace(textMessage, "\n", " ")
        textMessage = string.replace(textMessage, "&", "&amp;")
        textMessage = string.replace(textMessage, "\"", "&quot;")
        textMessage = string.replace(textMessage, "\'", "&apos;")
        textMessage = string.replace(textMessage, "<", "&lt;")
        textMessage = string.replace(textMessage, ">", "&gt;")
        textMessage = textMessage.encode('utf-8')
        outFd.write('<sms _id="%d">' % (count + offset))
        outFd.write('<address>%s</address>' % phoneNumber)
        outFd.write('<date>%d</date>' % (startTime * 1000))
        outFd.write('<date_sent>%d</date_sent>' % 0)
        outFd.write('<read>1</read>')
        outFd.write('<status>-1</status>')
        outFd.write('<type>%d</type>' % msgtype)
        outFd.write('<body>%s</body>' % textMessage)
        outFd.write('<seen>1</seen>')
        outFd.write('</sms>')        
        count += 1
#        print "%d messages parsed" % count
      except Exception, e:
        ignored += 1
#        print "ignoring junk data:"
        pass

    outFd.write('</sms-backup></backup>\n')


  # Close database connection
  connection.close()

  # Close xml file
  outFd.close()
except sqlite3.Error, err:
  utils.show_error('SQLite said: %s' % err)
except IOError, err:
  utils.show_error('Could not open xml file for writing: %s' % err)

print "Read and wrote %d messages" % count
print "Ignored %d junk messages" % ignored

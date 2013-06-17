#!/usr/bin/env python

# -*- coding: utf-8 -*-

import sys
import sqlite3
import os.path
import csv
from datetime import datetime

if len(sys.argv) != 3:
  print
  print 'Usage:'
  print '%s [path to el-v1.db] [path to csv file]' % sys.argv[0]
  print
  sys.exit(1)

dbFileName = sys.argv[1].strip()
csvFileName = sys.argv[2].strip()

if not os.path.exists(dbFileName):
  print
  print 'Error:'
  print 'Could not open \'%s\'' % dbFileName
  print
  sys.exit(1)

with sqlite3.connect(dbFileName) as connection, open(csvFileName, 'wb') as csvFd:
  cursor = connection.cursor()
  writer = csv.writer(csvFd, delimiter='\t', quotechar='"', quoting=csv.QUOTE_ALL)

  sql = 'SELECT `start_time`, `remote_uid`, `free_text` FROM `Events` WHERE `event_type_id` = 7'
  for record in cursor.execute(sql):
    startTime, phoneNumber, textMessage = record

    startDateTime = datetime.fromtimestamp(startTime).strftime('%Y-%m-%d %H:%M:%S')
    phoneNumber = phoneNumber.encode('utf-8')
    textMessage = textMessage.encode('utf-8')

    writer.writerow([startTime, startDateTime, phoneNumber, textMessage])

connection.close()
csvFd.close()

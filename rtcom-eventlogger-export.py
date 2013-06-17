#!/usr/bin/env python

# -*- coding: utf-8 -*-

import sys
import sqlite3
import csv
from datetime import datetime

import utils

if len(sys.argv) != 3:
  show_usage('%s [path to el-v1.db] [path to csv file]' % sys.argv[0])

dbFileName = sys.argv[1].strip()
csvFileName = sys.argv[2].strip()

try:
  # Try to open eventlogger database
  connection = sqlite3.connect(dbFileName)
  # Try to open csv file for writing
  csvFd = open(csvFileName, 'wb')

  with connection, csvFd:
    cursor = connection.cursor()
    writer = csv.writer(csvFd, delimiter='\t', quotechar='"', quoting=csv.QUOTE_ALL)

    sql = 'SELECT `start_time`, `remote_uid`, `free_text` FROM `Events` WHERE `event_type_id` = 7'
    for record in cursor.execute(sql):
      startTime, phoneNumber, textMessage = record

      startDateTime = datetime.fromtimestamp(startTime).strftime('%Y-%m-%d %H:%M:%S')
      phoneNumber = phoneNumber.encode('utf-8')
      textMessage = textMessage.encode('utf-8')

      writer.writerow([startTime, startDateTime, phoneNumber, textMessage])

  # Close database connection
  connection.close()
  # Close csv file
  csvFd.close()
except sqlite3.Error, err:
  utils.show_error('SQLite said: %s' % err)
except IOError, err:
  utils.show_error('Could not open csv file for writing: %s' % err)

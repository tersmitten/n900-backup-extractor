#!/usr/bin/env python

# -*- coding: utf-8 -*-

import sys
import vobject
from bsddb3 import db

if len(sys.argv) != 2:
  print ""
  print "Usage:"
  print "%s [path to addressbook.db]" % sys.argv[0]
  print ""
  sys.exit(1)

fileName = sys.argv[1].strip()

addressBookDb = db.DB()
try:
  # Try to open db file
  addressBookDb.open(fileName, None, db.DB_HASH, db.DB_DIRTY_READ)

  cursor = addressBookDb.cursor()
  record = cursor.first()

  # Fill a list with vcard strings from db
  vCards = []
  while record:

    # Get vcard string and correct line endings
    vCardString = record[1].replace('\x00', '\r\n')
    vCards.append(vCardString)

    record = cursor.next()

  # Write vcard strings
  for vCard in vCards:

    parsedVCard = vobject.readOne(vCard)

    # Not all entries have a n(ame) attribute
    if hasattr(parsedVCard, 'n'):
      vCardName = str(parsedVCard.n.value).strip()

      # Open vcard for writing
      with open('vcards/%s.vcf' % vCardName, 'w') as fd:
        fd.write(vCard)
      fd.close()

except db.DBNoSuchFileError:
  print ""
  print "Error:"
  print "Could not open '%s'" % fileName
  print ""
  sys.exit(1)

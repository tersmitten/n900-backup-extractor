#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""
Reads the eventlogger database (el-v1.db) and writes the text messages
to an XML file compatible with the backup format used by "Backup SMS
Pro" on Android. Tested successfully importing 11,000+ SMS
messages. Blatantly ripped off from rtcom-eventlogger-export.py...
"""

import argparse
from contextlib import closing
import sqlite3
import logging

from lxml import etree
from lxml.builder import E


log = logging.getLogger(__name__)


def format_record(record, id):
    start_time, end_time, phone_number, text_message = record

    # import datetime as dt
    # start_date_time = dt.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%SZ')

    if end_time > 0:
        msgtype = 2
    else:
        msgtype = 1

    return E.sms(
        E.address(phone_number),
        E.date(str(start_time * 1000)),
        E.date_sent('0'),  # ???
        E.read('1'),
        E.status('-1'),  # ???
        E.type(str(msgtype)),
        E.body(text_message),
        E.seen('1'),
        _id=str(id),
    )


def main():
    logging.basicConfig(level='INFO')

    parser = argparse.ArgumentParser()
    parser.add_argument('database', help='path to el-v1.db')
    parser.add_argument('xml', type=argparse.FileType(mode='wb'), help='path to XML file to write')
    args = parser.parse_args()

    count = 0
    offset = 1000
    ignored = 0

    smss = []

    # Try to open eventlogger database
    with closing(sqlite3.connect(args.database)) as connection:
        cursor = connection.cursor()

        sql = '''
        SELECT
            `start_time`, `end_time`, `remote_uid`, `free_text`
        FROM
            `Events`
        WHERE
            `event_type_id` = 7
        '''  # TODO: type 7 is only received, not sent, I think?
        for record in cursor.execute(sql):
            try:
                smss.append(format_record(record, count + offset))
                count += 1
            except Exception:
                log.exception('while processing record', *record)
                ignored += 1

    doc = E('backup', E('sms-backup', *smss))
    args.xml.write(etree.tostring(doc,
                                  encoding='utf-8',
                                  xml_declaration=True,
                                  standalone=True,
                                  pretty_print=True))

    print("Read and wrote %d messages" % count)
    print("Ignored %d junk messages" % ignored)


if __name__ == '__main__':
    main()

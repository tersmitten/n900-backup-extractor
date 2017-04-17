#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reads the eventlogger database (el.db) and writes the text messages
to an XML file compatible with the backup format used by "Backup SMS
Pro" on Android, or a CSV.
"""

import argparse
import csv
from contextlib import closing
import io
import sqlite3
import logging

from lxml import etree
from lxml.builder import E


log = logging.getLogger(__name__)


RTCOM_EL_EVENTTYPE_SMS_INBOUND = 7
RTCOM_EL_EVENTTYPE_SMS_OUTBOUND = 8

SMS_EVENT_TYPES = (
    RTCOM_EL_EVENTTYPE_SMS_INBOUND,
    RTCOM_EL_EVENTTYPE_SMS_OUTBOUND,
)


def format_record_xml(record, id):
    # import datetime as dt
    # start_date_time = dt.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%SZ')

    if record['direction'] == 'Inbound':
        msgtype = 2
    else:
        msgtype = 1

    return E.sms(
        E.address(record['remote_uid']),
        E.date(str(record['start_time'] * 1000)),
        E.date_sent('0'),  # ???
        E.read('1'),
        E.status('-1'),  # ???
        E.type(str(msgtype)),
        E.body(record['free_text']),
        E.seen('1'),
        _id=str(id),
    )


def format_xml(records, output):
    '''
    Backup format used by "Backup SMS Pro" on Android
    '''
    count = 0
    offset = 1000
    ignored = 0

    smss = []

    for record in records:
        try:
            smss.append(format_record_xml(record, count + offset))
            count += 1
        except Exception:
            log.exception('while processing record %s', record)
            ignored += 1

    print("Read and wrote %d messages" % count)
    print("Ignored %d junk messages" % ignored)

    doc = E('backup', E('sms-backup', *smss))
    output.write(etree.tostring(doc,
                                encoding='utf-8',
                                xml_declaration=True,
                                standalone=True,
                                pretty_print=True))


def format_csv(records, output):
    '''Raw-ish CSV output of SQL query.'''
    writer = csv.writer(io.TextIOWrapper(output, encoding='utf-8'))

    # first row
    for row in records:
        writer.writerow(row.keys())
        writer.writerow(row)
        break

    # rest of rows!
    writer.writerows(records)


formats = {
    'xml': format_xml,
    'csv': format_csv,
}


def main():
    logging.basicConfig(level='INFO')

    parser = argparse.ArgumentParser(
        description='Reads the eventlogger database (el.db) and writes the '
                    'text messages to a CSV, or to an XML file compatible '
                    'with the backup format used by "Backup SMS Pro" on '
                    'Android.')
    parser.add_argument('database', help='path to el.db')
    parser.add_argument('output',
                        type=argparse.FileType(mode='wb'),
                        help='path to file to write')
    parser.add_argument('--format',
                        choices=formats.keys(),
                        default='xml')
    args = parser.parse_args()

    with closing(sqlite3.connect(args.database)) as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        # free_text is NULL when the SMS has an attachment
        sql = '''
        SELECT
            CASE
                WHEN e.`event_type_id` = ? THEN "Inbound"
                WHEN e.`event_type_id` = ? THEN "Outbound"
                ELSE NULL
            END as `direction`,
            e.`start_time`,
            datetime(e.`start_time`, 'unixepoch') as `datetime`,
            e.`remote_uid`,
            r.`remote_name`,
            COALESCE(e.`free_text`, '') as `free_text`,
            a.`path` as `attachment_path`,
            a.`desc` as `attachment_format`
        FROM
            `Events` e
        LEFT JOIN
            `Remotes` r
        ON
            e.`local_uid` = r.`local_uid` AND
            e.`remote_uid` = r.`remote_uid`
        LEFT JOIN
            `Attachments` a
        ON
            e.`id` = a.`event_id`
        WHERE
            e.`event_type_id` IN (?, ?)
        ORDER BY
            e.`start_time`
        '''
        records = cursor.execute(sql, SMS_EVENT_TYPES * 2)
        with closing(args.output):
            formats[args.format](records, args.output)


if __name__ == '__main__':
    main()

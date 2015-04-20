#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import pymysql
from database import database
import codecs
import cStringIO

class UnicodeWriter:
    """
    Reference : https://docs.python.org/2/library/csv.html
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        tmp = []
        for s in row:
            tmp.append( unicode(s).encode('utf-8') if s is not None else None )
        self.writer.writerow(tmp)
        # User comment
        # self.writer.writerow([unicode(s).encode("utf-8") for s in row if s])
        
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

class CSVExporter():
    db = None
    headers = ['UID', 'Material ID', 'Color', 'Brand', 'ItemName', 'Year', 'Month']

    def initial_connection(self):
        self.db = database
        self.db.create_connection()

    def export_each_location(self):
        sql = "select items.uid, items.sku_mat_code, skus.color, skus.brand_id, items.item_name, items.created_at, items.location_id "
        sql += "from items, skus "
        sql += "where substring_index(items.sku_mat_code, '-', 1) = skus.sku_id "

        
        location_list = [item[0] for item in self.db.get_location_id_group_from_items()]
        for location in location_list:
            self.db.cursor.execute(sql + " and location_id = '{}'".format(location))
            with open('items_on_{}.csv'.format(location), 'wb') as csvfile:

                writer = UnicodeWriter(csvfile)
                writer.writerow(self.headers)

                for row in self.__iter_rows(self.db.cursor):
                    #print row
                    writer.writerow([row[0], row[1], row[2], row[3], u'%s' % row[4], row[5].year, row[5].month])
                
    def __iter_rows(self, cursor, size=100):
        while True:
            rows = cursor.fetchmany(size=size)
            if not rows: 
                break
            for row in rows: 
                yield row

if __name__=='__main__':
    c = CSVExporter()
    c.initial_connection()
    c.export_each_location()

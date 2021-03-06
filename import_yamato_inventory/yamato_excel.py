#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import datetime
import textwrap
import openpyxl

from database import *
from yamato_utils import *


class yamato_excel:
    current_uid = 1
    worksheet = None
    items = []
    lost_locations = []
    lost_materials = []
    columns = {
        'date': 'A',
        'warehouse_code': 'B',
        'item_code': 'C',
        'item_name': 'D',
        'item_color': 'E',
        'location_no': 'F',
        'qty_on_hand': 'G'
    }
    status = {
        'GOOD': 1,
        'B2B': 2,
        'DEFECT': 3,
        'GRADING': 3,
        'DAMAGE': 4
    }

    @classmethod
    def load_data(cls, filename, sheetname='Yamato Format with Locations'):
        workbook = openpyxl.load_workbook(filename)
        cls.worksheet = workbook[sheetname]

        for row in range(2, len(cls.worksheet.rows) + 1):
            data = {
                'row': row,
                'date': cls.get_cell_value(row, 'date'),
                'warehouse_code': cls.get_cell_value(row, 'warehouse_code'),
                'item_code': cls.get_cell_value(row, 'item_code'),
                'item_name': cls.get_cell_value(row, 'item_name'),
                'item_color': cls.get_cell_value(row, 'item_color'),
                'location_no': cls.get_cell_value(row, 'location_no'),
                'qty_on_hand': cls.get_cell_value(row, 'qty_on_hand')
            }
            cls.items.append(data)

    @classmethod
    def get_cell_value(cls, row, col):
        return cls.worksheet[cls.columns[col] + str(row)].value

    @classmethod
    def generate_sql_file(cls, filename='yamato.sql'):
        uid = 'TH011500000'

        sqlfile = open(filename, 'w')
        sqlfile.write("DELETE FROM item_history;\n")
        sqlfile.write("DELETE FROM items;\n")

        for item in cls.items:
            location = database.get_location_from_location_id(item['location_no'])
            material = database.get_mat_from_sap_matcode(item['item_code'])

            if location == None:
                #cls.lost_locations[item['location_no']] = "%s, %s" % (item['location_no'], item['qty_on_hand'])
                cls.lost_locations.append("%s, %s, %s" % (item['row'], item['location_no'], item['qty_on_hand']))
                continue

            if material == None:
                #cls.lost_materials[item['item_code']] = "%s, %s" % (item['item_code'], item['qty_on_hand'])
                cls.lost_materials.append("%s, %s, %s" % (item['row'], item['item_code'], item['qty_on_hand']))
                continue

            supplier = database.get_supplier_from_supplier_code(material[2])

            qty = int(item['qty_on_hand'])
            if qty > 0:
                for i in range(0, qty):
                    uid = get_next_uid(uid)

                    sql_item = cls.build_item_statement(uid, item, material, supplier)
                    sql_history = cls.build_item_history_statement(uid, item)

                    sqlfile.write(textwrap.dedent(sql_item.encode('utf-8')))
                    sqlfile.write(textwrap.dedent(sql_history.encode('utf-8')))

        sqlfile.write("\n")
        sqlfile.write("DELETE FROM item_sequencing;\n")
        sqlfile.write("INSERT INTO item_sequencing (item_id, sequence) VALUES ('%s', '%s');" % (uid[:6], uid[-5:]))
        sqlfile.close()

    @classmethod
    def build_item_statement(cls, uid, item, material, supplier):
        supplier_code = supplier[0]
        company_name = supplier[2]

        sku_mat_code = material[0]
        supplier_sku = material[5]

        date = datetime.datetime.strptime(str(item['date']), '%Y%m%d')
        item_name = item['item_name'].replace("'", "\\'")
        location_id = item['location_no']
        status_id = cls.status[item['warehouse_code']]

        sql = """
            INSERT INTO items (uid, sku_mat_code, item_name, location_id, status_id, updated_by, company_name, supplier_code, supplier_sku, created_at)
            VALUES ('%s', '%s', '%s', '%s', %s, '%s', '%s', '%s', '%s', '%s');
        """ % (uid, sku_mat_code, item_name, location_id, status_id, 'Yamato Migration', company_name, supplier_code, supplier_sku, date)
        return sql

    @classmethod
    def build_item_history_statement(cls, uid, item):
        status_id = cls.status[item['warehouse_code']]

        sql = """
            INSERT INTO item_history (uid, status_id, created_by)
            VALUES ('%s', %s, '%s');
        """ % (uid, status_id, 'Yamato Migration')
        return sql

    @classmethod
    def log_error_items(cls):
        if cls.lost_locations == {} and cls.lost_materials == {}:
            print "Not found any error, your data is ready to import."
            return True
        else:
            print "Data errors:"

            location_file = open('not_found_locations.csv', 'w')
            location_file.write("row, location_no, qty_on_hand\n")

            for location in cls.lost_locations:
                location_file.write("%s\n" % location)
            location_file.close()

            material_file = open('not_found_materials.csv', 'w')
            material_file.write("row, item_code, qty_on_hand\n")

            for material in cls.lost_materials:
                material_file.write("%s\n" % material)
                #material_file.write("%s\n" % cls.lost_materials[material])
            material_file.close()

            print "Save log to 'not_found_locations.csv' and 'not_found_materials.csv'"

            return False


if __name__ == "__main__":
    print sys.argv[1]

    if not len(sys.argv):
        print "Please specify excel file."
    else:
        database.create_connection(
            host='localhost',
            user='root',
            passwd='1q2w3e4r',
            db='ops'
        )
        yamato_excel.load_data(sys.argv[1])

        print "Generating sql file please wait ..."
        yamato_excel.generate_sql_file('yamato.sql')
        print "Data generate completed."

        yamato_excel.log_error_items()

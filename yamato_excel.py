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
    lost_locations = {}
    lost_materials = {}
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
    def load_data(cls, filename, sheetname='Inventory for check stock'):
        workbook = openpyxl.load_workbook(filename)
        cls.worksheet = workbook[sheetname]

        for row in range(2, len(cls.worksheet.rows) + 1):
            data = {
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
        sqlfile = open(filename, 'w')
        uid = 'TH011500000'

        for item in cls.items:
            location = database.get_location_from_location_id(item['location_no'])
            material = database.get_mat_from_sap_matcode(item['item_code'])

            if location == None:
                cls.lost_locations[item['location_no']] = "Not found location: %s" % item['location_no']
                continue

            if material == None:
                cls.lost_materials[item['item_code']] = "Not found material: %s" % item['item_code']
                continue

            supplier = database.get_supplier_from_supplier_code(material[2])

            qty = int(item['qty_on_hand'])
            for i in range(0, qty):
                uid = get_next_uid(uid)

                sql_item = cls.build_item_statement(uid, item, material, supplier)
                sql_history = cls.build_item_history_statement(uid, item)

                sqlfile.write(textwrap.dedent(sql_item.encode('utf-8')))
                sqlfile.write(textwrap.dedent(sql_history.encode('utf-8')))

        sqlfile.write("\nUPDATE item_sequencing SET sequence='%s' WHERE item_id='%s';" % (uid[-5:], uid[:6]))
        sqlfile.close()

    @classmethod
    def build_item_statement(cls, uid, item, material, supplier):
        supplier_code = supplier[0]
        company_name = supplier[2]

        sku_mat_code = material[0]
        supplier_sku = material[5]

        date = datetime.datetime.strptime(item['date'], '%Y%m%d')
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

            location_file = open('not_found_locations.txt', 'w')
            for location in cls.lost_locations.keys():
                location_file.write("%s\n" % cls.lost_locations[location])
                print cls.lost_locations[location]
            location_file.close()

            material_file = open('not_found_materials.txt', 'w')
            for material in cls.lost_materials.keys():
                material_file.write("%s\n" % cls.lost_materials[material])
                print cls.lost_materials[material]
            material_file.close()

            print "Save log to 'not_found_locations.txt' and 'not_found_materials.txt'"

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

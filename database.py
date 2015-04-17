# -*- coding: utf-8 -*-

import pymysql

class database:
    cursor = None
    connection = None

    @classmethod
    def create_connection(cls):
        cls.connection = pymysql.connect(
            host='localhost',
            user='root',
            passwd='1q2w3e4r',
            db='ops'
        )
        cls.cursor = cls.connection.cursor()

    @classmethod
    def close_connection(cls):
        cls.connection.close()

    @classmethod
    def get_mat_from_sap_matcode(cls, sap_mat_code):
        sql = "SELECT * FROM materials WHERE sap_mat_code='%s'" % sap_mat_code
        cls.cursor.execute(sql)
        return cls.cursor.fetchone()

    @classmethod
    def get_supplier_from_supplier_code(cls, supplier_code):
        sql = "SELECT * FROM suppliers WHERE supplier_code='%s'" % supplier_code
        cls.cursor.execute(sql)
        return cls.cursor.fetchone()

    @classmethod
    def get_location_from_location_id(cls, location_id):
        sql = "SELECT * FROM locations WHERE location_id='%s'" % location_id
        cls.cursor.execute(sql)
        return cls.cursor.fetchone()

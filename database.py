# -*- coding: utf-8 -*-

import pymysql

class database:
    cursor = None
    connection = None

    @classmethod
    def create_connection(cls, **kwargs):
        cls.connection = pymysql.connect(
            host=kwargs.get('host', 'localhost'),
            user=kwargs.get('user', 'root'),
            passwd=kwargs.get('passwd', '1q2w3e4r'),
            db=kwargs.get('db', 'ops'),
            charset='utf8'
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

    @classmethod
    def get_location_id_group_from_items(cls):
        sql = "select location_id from items group by location_id"
        cls.cursor.execute(sql)
        return cls.cursor.fetchall()

    @classmethod
    def get_all_skus(cls):
        sql = "SELECT * FROM skus;"
        cls.cursor.execute(sql)
        return cls.cursor.fetchall()

    @classmethod
    def count_items_by_sku(cls, sku):
        sql = "SELECT COUNT(*) FROM items WHERE sku_mat_code LIKE '{}%';".format(sku)
        cls.cursor.execute(sql)
        return cls.cursor.fetchone()

    @classmethod
    def count_virtual_stock_by_sku(cls, sku):
        sql = "SELECT stock_level FROM materials WHERE sku_id='{}';".format(sku)
        cls.cursor.execute(sql)
        return cls.cursor.fetchone()

    @classmethod
    def get_all_failure_messages(cls):
        sql = "SELECT * FROM failure_messages WHERE status='open';"
        cls.cursor.execute(sql)
        return cls.cursor.fetchall()

    @classmethod
    def mark_message_close(cls, msg_id):
        sql = "UPDATE failure_messages SET status='close' WHERE id={};".format(msg_id)
        cls.cursor.execute(sql)
        cls.connection.commit()


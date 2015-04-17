import pymysql

class database:
    cursor = None
    connection = None

    @classmethod
    def create_connection(cls, **kwargs):
        cls.connection = pymysql.connect(
            host='localhost',
            user='root',
            passwd=kwargs.get('passwd', '1q2w3e4r'),
            db='ops',
            charset='utf8'
        )
        cls.cursor = cls.connection.cursor()

    @classmethod
    def close_connection(cls):
        cls.connection.close()

    @classmethod
    def get_mat_from_sap_matcode(cls, sap_mat_code='1'):
        sql = "SELECT * FROM materials WHERE sap_mat_code='%s'" % sap_mat_code
        cls.cursor.execute(sql)
        return cls.cursor.fetchone()

    @classmethod
    def get_location_id_group_from_items(cls):
        sql = "select location_id from items group by location_id"
        cls.cursor.execute(sql)
        return cls.cursor.fetchall()
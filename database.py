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
        cls.cursor = connection.cursor()

    @classmethod
    def close_connection(cls):
        cls.connection.close()

    @classmethod
    def get_mat_from_sap_matcode(cls, sap_mat_code='1'):
        sql = "SELECT * FROM materials WHERE sap_mat_code='%s'" % sap_mat_code
        cls.cursor.execute(sql)
        return cls.cursor.fetchone()

import pymysql.cursors
import pymysql

class Connection:

    def __init__(self):
        # Connect to the database
        connection = pymysql.connect(host='localhost',
                                     user='root',
                                     password='XvX-313VC',
                                     db='samlogs',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor,
                                     autocommit=True)
        self.cursor = connection.cursor();
        return;

###############################################################################################################################

    def run_sql(self, sql, parameters):
        self.cursor.execute(sql, parameters);
        result = self.cursor.fetchall();
        return result;

###############################################################################################################################

    def close_cursor(self):
        self.cursor.close();
        return;

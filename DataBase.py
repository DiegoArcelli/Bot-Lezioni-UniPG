import mysql.connector
from mysql.connector import Error
import datetime as dt


class DataBase:


    def __init__(self, user, host, db, password):
        self.connection = self.db_connect(user, host, db, password)


    def db_connect(self, user, host, db, password):
        try:
            connection = mysql.connector.connect(host='localhost', database='lezioni_db', user='root', password='')
            if connection.is_connected():
                db_Info = connection.get_server_info()
                print("Connected to MySQL Server version ", db_Info)
                cursor = connection.cursor()
                cursor.execute("select database();")
                record = cursor.fetchone()
                print("You're connected to database: ", record)
        except Error as e:
            print("Error while connecting to MySQL", e)
        finally:
            if(connection.is_connected()):
                cursor.close()
        return connection


    def list_teachings(self):
        try:
            query = "SELECT * FROM Insegnamento INNER JOIN Docente ON Insegnamento.id_docente = Docente.id_docente "
            cursor = self.connection.cursor()
            cursor.execute(query)
            records = cursor.fetchall()
            full_string = ""
            for row in records:
                temp = "Insegnamento: " + str(row[0], 'utf-8') + "\nId insegnamento: " + str(row[1]) + "\nDocente: " + str(row[5], 'utf-8') + " " + str(row[6], 'utf-8') + "\n\n"
                full_string += temp
            print(full_string)
        except Error as e:
            print("Error reading data from MySQL table", e)
        finally:
            if(self.connection.is_connected()):
                cursor.close()
        return full_string


    def show_teaching_info(self, id):
        try:
            query = "SELECT * FROM Insegnamento INNER JOIN Docente ON Insegnamento.id_docente = Docente.id_docente WHERE Insegnamento.id_insegnamento = " + str(id)
            cursor = self.connection.cursor()
            cursor.execute(query)
            records = cursor.fetchall()
            str_info = "Insegnamento: " + str(records[0][0], 'utf-8') + "\nDocente: " + str(records[0][5], 'utf-8') + " " + str(records[0][6], 'utf-8') + "\nDescrizione: " + str(records[0][3], 'utf-8') + "\nId insegnamento: " + str(records[0][1])
        except Error as e:
            print("Error reading data from MySQL table", e)
        finally:
            if(self.connection.is_connected()):
                cursor.close()
        return str_info


    def get_cdl_list(self):
        try:
            query = "SELECT corso_di_laurea FROM Insegnamento GROUP BY corso_di_laurea"
            cursor = self.connection.cursor()
            cursor.execute(query)
            records = cursor.fetchall()
            cdl_names = []
            for itm in records:
                cdl_names.append(str(itm[0],'utf-8'))
        except Error as e:
            print("Error reading data from MySQL table", e)
        finally:
            if(self.connection.is_connected()):
                cursor.close()
        return cdl_names


    def get_cdl_teachings(self, teaching):
        try:
            query = "SELECT nome_insegnamento, id_insegnamento FROM Insegnamento WHERE corso_di_laurea = '" + teaching + "'"
            print(query)
            cursor = self.connection.cursor()
            cursor.execute(query)
            records = cursor.fetchall()
            teachings_names = []
            teachings_ids = []
            for itm in records:
                teachings_names.append(str(itm[0],'utf-8'))
                teachings_ids.append(itm[1])
        except Error as e:
            print("Error reading data from MySQL table", e)
        finally:
            if(self.connection.is_connected()):
                cursor.close()
        return teachings_names, teachings_ids


    def get_lessons(self, id):
        try:
            query = "SELECT * FROM Lezione INNER JOIN Insegnamento ON Insegnamento.id_insegnamento = Lezione.id_insegnamento INNER JOIN Docente ON Docente.id_docente = Lezione.id_docente WHERE Lezione.id_insegnamento =" + str(id)
            cursor = self.connection.cursor()
            cursor.execute(query)
            records = cursor.fetchall()
            full_string = "Insegnamento " + str(records[0][6], 'utf-8') + "\n\n"
            print(full_string)
            for itm in records:
                data = itm[3]
                str_data = data.strftime('%m/%d/%Y')
                temp = "Data: " + str_data + "\n\n"
                full_string += temp
        except Error as e:
            print("Error reading data from MySQL table", e)
        finally:
            if(self.connection.is_connected()):
                cursor.close()
        return full_string

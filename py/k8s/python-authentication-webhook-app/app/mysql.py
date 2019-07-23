#!/usr/bin/python

import pymysql.cursors
import random, string
import base64


def password_hide(choice, password):
    if choice == 'encode':
        new = base64.b64encode(password)
    if choice == 'decode':
        new = base64.b64decode(password)
    return new


class mysql_operation():

    def __init__(self, host, port, user, password, db):

    	self.host = host            				# '172.31.102.236'
    	self.port = port            				# 6181
    	self.user = user            				# 'webhook'
    	self.password = password    				# 'webhook123'
    	self.db = db                				# 'webhook'
        self.connection = pymysql.connect(host=host, 
					  port=port, 
					  user=user, 
					  password=password, 
					  db=db)

    def create_tables(self):

    	sql = """CREATE TABLE k8s_users (id INT(10) UNSIGNED AUTO_INCREMENT PRIMARY KEY, 
				   username VARCHAR(50) NOT NULL, 
				   password VARCHAR(250) NOT NULL, 
				   groups VARCHAR(100) NOT NULL);"""
	sql2 = """CREATE TABLE login_users (id INT(10) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
					username VARCHAR(50) NOT NULL,
					password VARCHAR(250) NOT NULL);"""
	sql3 = "INSERT INTO login_users (username, password) values (%s, %s);"

	web_admin_password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(22))
    	with self.connection.cursor() as cursor:
            cursor.execute(sql)
            cursor.execute(sql2)
	    cursor.execute(sql3, ('admin', str(web_admin_password)))
    	self.connection.commit()
	print "Web username: admin"
        print "Web password: %s" % web_admin_password


    def check_password(self, password):
       
        sql = "SELECT id,username,groups FROM k8s_users WHERE password=%s;"
        with self.connection.cursor() as cursor:
            cursor.execute(sql, (password))
            result = cursor.fetchone()
        
	return result	

    def check_webpassword(self, password):

	sql = "SELECT id,username,password FROM login_users WHERE password=%s;"
        with self.connection.cursor() as cursor:
            cursor.execute(sql, (password))
            result = cursor.fetchone()
        return result


    def insert_record(self, username, password, groups):
       
	sql = "insert into k8s_users (username, password, groups) values (%s, %s, %s);"
	with self.connection.cursor() as cursor:
	    cursor.execute(sql, (username, password, groups))
        self.connection.commit()

    def delete_record(self, username, password):

        sql = "delete from k8s_users where username=%s and password=%s;"
        with self.connection.cursor() as cursor:
            cursor.execute(sql, (username, password))
        self.connection.commit()

    def list_all_k8s(self):
	
	sql = "select * from k8s_users;"
        with self.connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
	return result


    def close(self):
	self.connection.close()


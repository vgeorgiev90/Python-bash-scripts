#!/usr/bin/python
#Database connection and queries


import getpass
import time
import MySQLdb
import os
import sys


###### DB variables ##########

username = "bazata"
password = "*75ED6F9E59DDB3699C23A492B374A5D0FE12ED33"
database = "know"
table = "comands"



######### Functions ###########

def install():
    try:
        print("The script will now install the database and user for it")
        print("Provide your mysql root password..")
        PASS = getpass.getpass()
        connect = MySQLdb.connect(host='localhost', user='root', passwd=PASS)
        cursor = connect.cursor()

        sql = "create database know;"
        sql2 = "create table know.comands (id int not null auto_increment, name varchar(30), command varchar(300), comment varchar(300), primary key (id));"
        sql3 = "create user 'bazata'@'localhost' identified by password '*75ED6F9E59DDB3699C23A492B374A5D0FE12ED33';"
        sql4 = "grant all privileges on know.* to 'bazata'@'localhost' identified by '*75ED6F9E59DDB3699C23A492B374A5D0FE12ED33';"

        cursor.execute(sql)
        cursor.execute(sql2)
        cursor.execute(sql3)
        cursor.execute(sql4)
        connect.commit()

        cursor.close()
        connect.close()
    except:
        print("Error has occured check if the database and user already exists..")


def main():
    try:
        print("Mysql connection scirpt")
        print("=========================")
        print("search  --  for db search")
        print("insert  --  for db insert")
        print("remove  --  for db remove")
        CH = raw_input("Choice: ")

        if CH == 'search':
            read()
        elif CH == 'insert':
            insert()
        elif CH == 'remove':
            remove()
        else:
            print("Nothing....")
            cur.close()
            con.close()
    except:
        print("Goodbye....")
        cur.close()
        con.close()

def read():
    try:
        while (1):
            ID = raw_input("What to fetch: ")
            if ID == 'quit':
                cur.close()
                con.close()
                break
            elif ID == 'clear':
                os.system('clear')
            elif ID == 'back':
                main()
            else:
                sql = "select * from " + table + " where name like '%" + ID + "%';"
                cur.execute(sql)

                answer = cur.fetchall()
                for row in answer:
                    answer = str(row)
                    b = answer.split(",")
                    print("----------------------------------------------------------------")
                    print(b[0].split("(")[1] + " | " + b[1] + " | " + b[2] + " | " + b[3].split(")")[0])
    except:
        print("Nothing to show")
        cur.close()
        con.close()

def insert():

    try:
        NAME = raw_input("What is the name:  ")
        COM = raw_input("What is the command: ")
        COMM = raw_input("What is the comment: ")

        sql2 = "insert into comands (name, command, comment) values ('" + NAME +"', '" + COM + "', '" + COMM + "');"

        cur.execute(sql2)
        con.commit()
        time.sleep(2)
        main()
    except:
        print("Something is wrong with the query...")
        cur.close()
        con.close()

def remove():

    try:
        ID = raw_input("Which ID to remove: ")

        sql3 = "delete from comands where id=" + ID + ";"
        cur.execute(sql3)
        con.commit()
        time.sleep(2)
        main()
    except:
        print("Error please try again or check if there is such record...")
        cur.close()
        con.close()
        break

######### Script start ###########



if len(sys.argv) > 1:
    var = sys.argv[1]
    if var == 'install':
        install()
    else:
        print("This script takes as argument only install")
else:
    try:
        ########## DB connection ##########

        con = MySQLdb.connect(host="localhost", user=username, passwd=password, db=database)
        cur = con.cursor()
        main()
    except:
        print("Please check if database and user are created..")

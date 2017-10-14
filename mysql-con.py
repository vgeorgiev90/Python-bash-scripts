#!/usr/bin/python


import time
import MySQLdb
import gc
import os

gc.collect()

###### Variables for db connection #######

username = "root"
password = "viktor123"
database = "viktor"
table = "comands"

######## DB connection ###########

con = MySQLdb.connect(host="localhost", user=username, passwd=password, db=database)
cur = con.cursor()


######### Functions ###########

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
    except:
        print("Goodbye....")
        cur.close()
        con.close()

def read():
    try:
        while (1):
            ID = raw_input("What to fetch: ")
            if ID == 'quit':
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

######### Script start ###########

main()

cur.close()
con.close()

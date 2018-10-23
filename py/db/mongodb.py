#!/usr/bin/python
#Script for historical cleanup of data automation

import pymongo
import sys

################

class mongo():
    def __init__(self,id):
        self.id = id
        self.query = {"projectId": self.id}
        self.mongo = pymongo.MongoClient('192.168.55.95', 27017)  ### Host for mongodb must be changed if the script will run localy leave it as localhost , if it will run remotely make sure that your IP is added to the EC2 security group
        self.db = self.mongo['database']                    ## your database and collection here
        self.collection = self.db['collection']

    def list(self):
        cursor = self.collection.find(self.query)
        for coll in cursor:
            return coll

    def remove(self):
        result = self.collection.delete_one(self.query)

    def insert(self,document):
        result = self.collection.insert_one(document)


def reinsert(project_id):
    find = mongo(project_id)
    result = find.list()
    d1 = result['lastFeed']
    d2 = d1.replace(year=2015,month=01,day=01)
    result['lastFeed'] = d2
    del result['lastTicketDate']
    print "The following document will be inserted..."
    print ""
    print result
    print ""
    choice = raw_input('Proceed with insert(yes/no): ')
    if choice == 'yes':
        find.remove()
        find.insert(result)
        print "The record is now inserted"
    else:
        print "Nothing will be inserted.."

def usage():
    print "Argument must be E2E projectID"

##################

project_id = sys.argv[1]

try:
    reinsert(project_id)
except (TypeError,KeyError) as e:
    usage()
    print "There is a problem with: %s" % e

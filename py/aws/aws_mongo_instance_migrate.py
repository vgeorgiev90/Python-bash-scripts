#!/usr/bin/python

import argparse
import pymongo

########### Functions ################

def parser():
   parser = argparse.ArgumentParser()
   parser.add_argument('--order','-o',nargs=1,metavar='OrderID',help='Provide orderID')
   parser.add_argument('--client','-c',nargs=1,metavar='Client',help='Provide ClientID')
   parser.add_argument('--options','-p',nargs=3,metavar="url_public url_private instance_id", help="new records for the migration")
   parser.add_argument('--usage','-u',action='store_true',help="Print usage for the script")
   return parser

class Mongo():

    def __init__(self,host):
        self.port = 27017
        self.db = 'aiamhpdpintegration'
        self.connection = pymongo.MongoClient(host,self.port)
        self.database = self.connection[self.db]

    def find_entry(self,query,collection):
        self.coll = self.database[collection]
        entries = self.coll.find(query)
        for coll in entries:
            return coll

    def insert_new(self,document,collection):
        self.new_coll = self.database[collection]
        result = self.new_coll.insert_one(document)

    def remove_old(self,query,collection):
        self.rem_coll = self.database[collection]
        result = self.rem_coll.delete_one(query)


def modify_entry(document,url_private,url_public,instance_id):
    document['urlPublic'] = url_public
    document['urlPrivate'] = url_private
    document['instanceId'] = instance_id
    del document["_id"]
    return document


def usage():
    print "./migration.py --client stesofiproteo1 --order 02aa109f-b86d-4f3d-a17e-5c98f189b413 --options https://some-shity-example/example https://1.1.1.1:8211 example_instance"

############## Script ###################


parser = parser()
args = parser.parse_args()


if args.order and args.client and args.options:

    url_public = args.options[0]
    url_private = args.options[1]
    instance_id  = args.options[2]
    order = args.order[0]
    client = args.client[0]

    query1 = {"clientId": client }
    query2 = {"orderId": order}


    mongo = Mongo('localhost')
    server_entry = mongo.find_entry(query1,'server')
    order_entry = mongo.find_entry(query2,'orderRequest')

    doc = modify_entry(server_entry,url_private,url_public,instance_id)

    try:
        mongo_remote = Mongo('192.168.55.102')
        mongo_remote.insert_new(doc,'server')
        new_doc = mongo_remote.find_entry(query1,'server')
        key = str(new_doc["_id"])

        order_entry['server'] = key
        mongo_remote.insert_new(order_entry,'orderRequest')
    except (pymongo.errors.DuplicateKeyError,pymongo.errors.PyMongoError) as e:
        print "There was a problem found.."
        print e

if args.usage:
    usage()

from pymongo import MongoClient
from pprint import pprint
client = MongoClient("mongodb+srv://${User}:${Pass}@${server}/<dbname>?retryWrites=true&w=majority")
db=client.aws_audit
db.prueba.insert_one({'lenguaje': 'python'})

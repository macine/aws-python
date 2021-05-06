from pymongo import MongoClient
from pprint import pprint
client = MongoClient("mongodb+srv://aws_audit:aws_audit@mongomacinegcp.famw7.gcp.mongodb.net/<dbname>?retryWrites=true&w=majority")
db=client.aws_audit
db.prueba.insert_one({'lenguaje': 'python'})

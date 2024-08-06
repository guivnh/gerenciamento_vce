from pymongo import MongoClient


class Database:
    def __init__(self, db_name='gerenciamento_vendas'):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client[db_name]

    def get_collection(self, collection_name):
        return self.db[collection_name]

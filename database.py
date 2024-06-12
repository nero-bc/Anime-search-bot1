from pymongo.collection import Collection
from config import client, database_name, default_gogoanime_token, default_auth_token, default_url

default_data = {
    "_id": "GogoAnime",
    "url": default_url,
    "gogoanime": default_gogoanime_token,
    "auth": default_auth_token
}

class ConfigDB:
    def __init__(self):
        self.col = Collection(client[database_name], 'ConfigDB')
        
    def find(self, data):
        result = self.col.find_one(data)
        if result:
            return result
        else:
            return default_data

    def add(self, data):
        self.col.insert_one(data)

    def modify(self, search_dict, new_dict):
        try:
            self.col.find_one_and_update(search_dict, {'$set': new_dict})
        except Exception as e:
            print(f"Exception in ConfigDB -> modify\n\n{e}")
            
        existing_data = self.find({"_id": "GogoAnime"})
        if existing_data:
            self.modify({"_id": "GogoAnime"}, default_data)
        else:
            self.add(default_data)

class UsersDB:
    def __init__(self):
        self.files_col = Collection(client[database_name], 'UsersDB')
        
    def find(self, data):
        return self.files_col.find_one(data)
    
    def full(self):
        return list(self.files_col.find())

    def add(self, data):
        try:
            self.files_col.insert_one(data)
        except:
            pass

    def remove(self, data):
        self.files_col.delete_one(data)

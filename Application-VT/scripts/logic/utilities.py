import pymongo
import os
import json
import sys
import time
from bson.objectid import ObjectId
OS = sys.platform


class AuthenticationError(Exception):
    pass


class ConnectDB():
    def __init__(self):
        self.info_db = self.get_info_db()
        self.conn = pymongo.MongoClient(*self.info_db)
        self.db = self.conn.mydb

    def config_app(self):
        path = os.getcwd() + "\config.json"
        with open(path) as config:
            json_str = config.read()
            return json.loads(json_str)

    def get_info_db(self):
        info_db = self.config_app()['Data_Base']
        host, port = info_db['host'], info_db['port']
        return host, int(port)


class User:
    def __init__(self, login, password):
        self.login = login
        self.password = password


class WrapperDB:
    def __init__(self):
        self.db = ConnectDB().db
        self.coll_users = self.db.users
        self.coll_message = self.db.message

    def is_authentication(self, login, password) -> bool:
        print(login, password)
        find = self.coll_users.find_one({"user_name": login,
                                         "password": password})
        print(find)
        if find:
            return True
        return False

    def registration(self, login, password) -> bool:
        doc = {"user_name": login, "password": password, "friends": []}
        if self.coll_users.insert_one(doc):
            return True
        return False

    def is_user(self, login) -> bool:
        data = self.coll_users.find({"user_name": login})
        status = [user for user in data]
        print(status)
        if status:
            return True
        return False

    def seve_message(self, doc) -> bool:
        status = self.coll_message.insert_one(doc)
        if status:
            return True
        return False

    def check_message(self, login):
        data = self.coll_message.find({"whom": login,
                                       "status": "not_view"})
        return data

    def update_write_message(self, id):
        self.coll_message.update({'_id': ObjectId(id)},
                                 {'$set': {"status": "view"}})

    def add_friend(self, login, user_friend) -> bool:
        user = self.coll_users.find_one({"user_name": login})
        user['friends'].append(user_friend)
        friend = user['friends']
        status = self.coll_users.update_one({'user_name': login}, {'$set': {"friends": friend}})
        if isinstance(status, list):
            return True
        return False
    
    def is_friend(self, login, friend):
        doc_user = self.coll_users.find_one({"user_name": login})
        if friend in doc_user['friends']:
            return True
        return False

    def get_friends(self, login):
        doc_user = self.coll_users.find_one({"user_name": login})
        return doc_user['friends']


class Destributor:
    def __init__(self, login, password, data=None):
        self.user = User(login, password)
        self.authentication = WrapperDB().is_authentication(login, password)
        self.data = data

    def registration(self) -> bool:
        print('registration')
        login = self.user.login
        password = self.user.password
        if not WrapperDB().is_user(login):
            status = WrapperDB().registration(login, password)
            return status
        return False

    def seve_message(self, data) -> bool:
        print('save_message')
        if WrapperDB().is_user(data['whom']):
            doc = dict()
            doc["user_name"] = self.user.login
            doc["whom"] = self.data["whom"]
            doc["data"] = self.data["data"]
            doc["message"] = self.data["message"]
            doc["status"] = "not_view"
            status = WrapperDB().seve_message(doc)
            login = self.user.login
            if not WrapperDB().is_friend(login, self.data["whom"]):
                WrapperDB().add_friend(login, self.data["whom"])
            return status
        return False

    def is_whom_user(self, data):
        print('is_whom_user')
        whom = data['whom']
        status = WrapperDB().is_user(whom)
        return status

    def read_message(self):
        print('read_message')
        message = WrapperDB().check_message(self.user.login)
        pars_data = self.parsing(message)
        return pars_data
    
    def check_message(self):
        print('check_message')
        message = WrapperDB().check_message(self.user.login)
        counter = len([i for i in message])
        return counter


    def parsing(self, data):
        """ Parsing data in dict(dict()...) """
        try:
            new_data = dict()
            new_data['messages'] = []
            for mess in data:
                id = mess['_id']
                WrapperDB().update_write_message(id)
                del mess['_id']
                new_data['messages'].append(mess)
                if new_data['messages']:
                    new_data['status'] = True
            return new_data
        except TypeError:
            return None

    def is_user(self):
        status = WrapperDB().is_user(self.user.login)
        return status
    
    def get_friends(self):
        friends = WrapperDB().get_friends(self.user.login)
        return friends
    
    def is_friend(self, login, friend):
        status = WrapperDB().is_friend(self.user.login, friend)
        return status


class CommandDB(WrapperDB):
    def dell_user(self, id):
        status = self.coll_users.remove({'_id': ObjectId(id)})
        data = self.coll_users.find({})
        print(data)
        return status

    def find_to_user_id(self, id):
        status = self.coll_users.find_one({"_id": ObjectId(id)})
        print(status)

    def find_to_user_login(self, login):
        status = self.coll_users.find_one({"user_name": login})
        return status

    def find_to_message_id(self, id):
        status = self.coll_message.find_one({"_id": ObjectId(id)})
        print(status)

    def create_new_user(self, login, password):
        doc = {"user_name": login, "password": password, "friends": []}
        status = self.coll_users.save(doc)
        print(status)

    def get_all_users(self):
        users = self.coll_users.find({})
        for user in users:
            print(user)

    def message_update(self, id):
        self.coll_message.update_one({'_id': ObjectId(id)}, {'$set': {"status": "view"}})

    def get_all_message(self):
        messages = self.coll_message.find({})
        for mess in messages:
            print(mess)


def validator_time(sent):
    times = sent['data']
    time.ctime(times)
    

def use_admin_command():
    CommandDB().create_new_user('Sasha', 'Rukina')
    CommandDB().dell_user('5ebbc1a616c8491443fd40f1')
    CommandDB().get_all_users()
    CommandDB().message_update('5ebbff04e49793d4574b7c47')
    CommandDB().get_all_message()


# CommandDB().dell_user('5eed142b14b1de16befdec5b')
# CommandDB().find_to_message_id('5ebbb204bc47cb21fa3db29d')

# CommandDB().create_new_user('kop', '123')

# CommandDB().dell_user('5ef09b83a9ffc54e736ff20d')
# CommandDB().dell_user('5eec63f6673f3fd3a82b11fb')



# CommandDB().get_all_users()

# CommandDB().dell_user('5ec28010414dbc790d0c34e8')
# CommandDB().dell_user('5ec2863ecf361818e6236525')

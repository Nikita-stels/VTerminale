from flask import Flask, request
# from scripts.logic.core_logic import main_logic
from scripts.logic.utilities import WrapperDB
from scripts.logic.utilities import AuthenticationError
import json


app = Flask(__name__)


@app.route('/api/v1/info/<user_name>', methods=['POST'])
def info(user_name):
    # data = request.json
    print(user_name)
    return {"ok": [1, 3, 4, 5]}


@app.route('/api/v1/<user_name>/check_message', methods=['POST'])
def check_message(user_name):
    # print(user_name)
    data = request.json
    # print(data)

    client0 = WrapperDB(user_name, data)
    status = client0.check_message()
    print(status)
    if status:
        # print(status, type(status))
        # print(type()
        return status
    return {}


@app.route('/api/v1/<user_name>/write_message/', methods=['POST'])
def write_message(user_name):
    print(user_name)
    data = request.json
    print(data)

    client = WrapperDB(user_name, data)
    client.seve_message()
    return {"ok write message": True}


@app.route('/api/v1/<user_name>/authentication/', methods=['POST'])
def authentication(user_name):
    """ Сравнивает логин и пароль пользователя с БД """
    print(user_name)
    data = request.json
    print(data)
    # command = 'authentication'
    # status = main_logic(user_name, data, command)
    try:
        WrapperDB(user_name, data)
        status = True
    except AuthenticationError:
        status = False
    # if user_name == 'bob':
    #     if data['password'] == '123':
    #         return {"status": True}
    # return {"status": False}
    print(status)
    return {"status": status}


@app.route('/api/v1/<user_name>/registration/', methods=['POST'])
def registration(user_name):
    data = request.json
    status = WrapperDB.save_reg_user(user_name, data)
    return {"status": status}


@app.route('/api/v1/<user_name>/is_users/', methods=['POST'])
def is_users(user_name):
    data = request.json
    print(data)
    info = WrapperDB(user_name, data)
    status = info.is_users()
    return {"status": status}


@app.route('/api/v1/<user_name>/is_login', methods=['POST'])
def is_login(user_name):
    print(user_name)
    data = request.json
    print(data)
    status = WrapperDB.is_login(user_name)
    return {"status": status}



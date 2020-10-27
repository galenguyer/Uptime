""" A small flask Hello World """

import os
import sys
import threading
import atexit
import sqlite3
import json

from flask import Flask, jsonify
import yaml

def read_config():
    if not (os.path.exists('./data/config.yml') or os.path.exists('./data/config.yaml')):
        print('config file not found, creating and exiting')
        basic_config = {'sites': 
            [
                { 'sitename': { 'name': 'Site 1', 'url': 'http://example.com' } }, 
                { 'anothersite': { 'name': 'Another Site', 'url': 'https://example.com' } }
            ] 
        }
        if not os.path.exists('./data'):
            os.mkdir('./data')
        with open('./data/config.yml', 'w') as config_file:
            config = yaml.dump(basic_config)
            config_file.write('---\n'+config)
            print(config)
        sys.exit(1)
    else:
        if os.path.exists('./data/config.yml'):
            filename = './data/config.yml'
        else:
            filename = './data/config.yaml'
    with open(filename, 'r') as config_file:
        config = yaml.load(config_file.read(), Loader=yaml.FullLoader)
        return config

APP = Flask(__name__)
db_conn = sqlite3.connect('data/data.sqlite3')
for site in read_config()['sites']:
    c = db_conn.cursor()
    key = list(site.keys())[0]
    sql = f'CREATE TABLE IF NOT EXISTS `{key}` (time DATETIME, isup BOOLEAN);'
    c.execute(sql)
db_conn.commit()

# Load file based configuration overrides if present
#if os.path.exists(os.path.join(os.getcwd(), 'config.py')):
#    APP.config.from_pyfile(os.path.join(os.getcwd(), 'config.py'))
#else:
#    APP.config.from_pyfile(os.path.join(os.getcwd(), 'config.env.py'))

APP.secret_key = os.urandom(24)

@APP.route('/')
def _index():
    data = {}
    for site in read_config()['sites']:
        c = db_conn.cursor()
        key = list(site.keys())[0]    
        sql = f'SELECT * FROM `{key}`;'
        c.execute(sql)
        data[key] = [{'time': d[0], 'up': d[1]} for d in c.fetchall()]

    return jsonify(data)

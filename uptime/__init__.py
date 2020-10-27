""" A small flask Hello World """

import os
import sys
import threading
import atexit
import sqlite3
import json
import requests

from flask import Flask, jsonify
import yaml

POOL_TIME = 30 # Seconds
db_lock = threading.Lock()
ping_thread = threading.Thread()

def read_config():
    if not (os.path.exists('./data/config.yml') or os.path.exists('./data/config.yaml')):
        print('config file not found, creating')
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
    else:
        if os.path.exists('./data/config.yml'):
            filename = './data/config.yml'
        else:
            filename = './data/config.yaml'
    with open(filename, 'r') as config_file:
        config = yaml.load(config_file.read(), Loader=yaml.FullLoader)
        return config

def interrupt():
    global ping_thread
    ping_thread.cancel()

def ping_sites():
    global commonDataStruct
    global ping_thread
    with db_lock:
        db_conn = sqlite3.connect('data/data.sqlite3')
        for site in read_config()['sites']:
            c = db_conn.cursor()
            key = list(site.keys())[0]
            try:
                code = requests.get(site[key]['url']).status_code
                if 100 <= code < 400:
                    sql = f'INSERT INTO `{key}` VALUES (datetime(\'now\'), true);'
                else:
                    sql = f'INSERT INTO `{key}` VALUES (datetime(\'now\'), false);'
            except Exception: 
                    sql = f'INSERT INTO `{key}` VALUES (datetime(\'now\'), false);'
            c.execute(sql)
            db_conn.commit()
        db_conn.close()
    ping_thread = threading.Timer(POOL_TIME, ping_sites, ())
    ping_thread.start()

def ping_sites_start():
    # Do initialisation stuff here
    global ping_thread
    # Create your thread
    ping_thread = threading.Timer(POOL_TIME, ping_sites, ())
    ping_thread.start()


ping_sites_start()
# When you kill Flask (SIGTERM), clear the trigger for the next thread
atexit.register(interrupt)

APP = Flask(__name__)
db_conn = sqlite3.connect('data/data.sqlite3')
for site in read_config()['sites']:
    c = db_conn.cursor()
    key = list(site.keys())[0]
    sql = f'CREATE TABLE IF NOT EXISTS `{key}` (time DATETIME, isup BOOLEAN);'
    c.execute(sql)
db_conn.commit()
db_conn.close()

# Load file based configuration overrides if present
#if os.path.exists(os.path.join(os.getcwd(), 'config.py')):
#    APP.config.from_pyfile(os.path.join(os.getcwd(), 'config.py'))
#else:
#    APP.config.from_pyfile(os.path.join(os.getcwd(), 'config.env.py'))

APP.secret_key = os.urandom(24)

@APP.route('/')
def _index():
    with db_lock:
        db_conn = sqlite3.connect('data/data.sqlite3')
        data = {}
        for site in read_config()['sites']:
            c = db_conn.cursor()
            key = list(site.keys())[0]    
            sql = f'SELECT * FROM `{key}`;'
            c.execute(sql)
            data[key] = [{'time': d[0], 'up': (d[1] == 1)} for d in c.fetchall()]
        db_conn.close()
        return jsonify(data)

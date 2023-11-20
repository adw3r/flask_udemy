import os
import pathlib

import configparser

import dotenv

ROOT_FOLDER = pathlib.Path(__file__).parent
dotenv.load_dotenv()
__conf_pars = configparser.ConfigParser()
__conf_pars.add_section('general')
__conf_pars['general'] = os.environ
GENERAL_CONF = __conf_pars['general']

APP_PORT = GENERAL_CONF.getint('APP_PORT')
APP_HOST = GENERAL_CONF.get('APP_HOST')
APP_DEBUG = GENERAL_CONF.getboolean('APP_DEBUG')

SECRET_KEY = GENERAL_CONF.get('SECRET_KEY')

MYSQL_HOST = GENERAL_CONF.get('MYSQL_HOST')
MYSQL_DBNAME = GENERAL_CONF.get('MYSQL_DBNAME')
MYSQL_USERNAME = GENERAL_CONF.get('MYSQL_USERNAME')
MYSQL_PASSWORD = GENERAL_CONF.get('MYSQL_PASSWORD')
MYSQL_PORT = GENERAL_CONF.get('MYSQL_PORT')

DB_URI = f'mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DBNAME}'

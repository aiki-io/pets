import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.venv'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    MONGODB_HOST = os.environ.get('MONGODB_HOST') or ''
    MONGODB_DB = os.environ.get('MONGODB_DB') or 'pets'

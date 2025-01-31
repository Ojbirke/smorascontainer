import os

class Config:
    SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:////app/instance/football_team.db' 
    SQLALCHEMY_TRACK_MODIFICATIONS = False

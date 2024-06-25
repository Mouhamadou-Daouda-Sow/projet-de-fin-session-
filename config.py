import os


class Config:
    #ADMIN_EMAIL = None
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sow_noble_yazid_diaby'
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'MySql123?'
    MYSQL_DB = 'reservation_evenements'

from flask_script import Manager
from myapp import app

__author__ = 'Elijah Lopez'
__version__ = 1.0
__created__ = '2017-08-22'
'''
manage - by Elijah Lopez
version 1.0
'''

# manage.py



manager = Manager(app)

@manager.command
def hello():
    print ("hello")

if __name__ == "__main__":
    manager.run()

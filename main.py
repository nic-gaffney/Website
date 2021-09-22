# Source code for my website gaffclant.com
import datetime
import os.path

import cherrypy
from jinja2 import Environment, FileSystemLoader, select_autoescape
from peewee import *

env = Environment(loader=FileSystemLoader('public'), autoescape=select_autoescape())
db = SqliteDatabase('blog_database.db')


class BaseModel(Model):
    class Meta:
        database = db


class Post(BaseModel):
    created_date = DateTimeField(default=datetime.datetime.now)
    title = TextField()
    text = TextField()
    id = IntegerField(unique=True)


db.connect()
db.create_tables([Post])


class Website(object):
    @cherrypy.expose
    def index(self):
        template = env.get_template("html/index.html")
        return template.render(index=True, blog=["TEST", "THIS NO SHOW"])

    @cherrypy.expose
    def about(self):
        template = env.get_template("html/about.html")
        return template.render(about=True)


if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        }
    }
    cherrypy.quickstart(Website(), '/', conf)

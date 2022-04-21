# Source code for my website gaffclant.com
import datetime
import json
import os.path
import re

import markdown
import cherrypy
import requests
from cherrypy.lib import auth_digest
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader, select_autoescape
from peewee import *
from playhouse.signals import pre_save

env = Environment(loader=FileSystemLoader('public'), autoescape=select_autoescape())
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "blog_database.db")
db = SqliteDatabase(db_path)


class BaseModel(Model):
    class Meta:
        database = db


class Post(BaseModel):
    date = DateTimeField(default=datetime.datetime.now)
    title = TextField()
    text = TextField()
    id = IntegerField(primary_key=True)


@pre_save(sender=Post)
def on_save_handler(model_class, instance, created):
    next_value = Post.select(fn.Max(Post.temp_id))[0].temp_id + 1
    instance.temp_id = next_value


db.connect()

db.create_tables([Post])


class Website(object):
    @cherrypy.expose
    def index(self):
        preview = Post.select().order_by(Post.date.desc()).limit(3)
        template = env.get_template("html/index.html")
        motdJson = requests.get("https://xkcd.com/info.0.json").json()
        motd = motdJson.get("img")
        return template.render(index=True,
                               re=re,
                               blog=preview,
                               motd=motd,
                               title="Nicolas Gaffney",
                               sub="I make APIs, bots, and CLI apps!",
                               topper="Recent posts",
                               markdown=markdown)

    @cherrypy.expose
    def about(self):
        template = env.get_template("html/about.html")
        return template.render(about=True)

    @cherrypy.expose
    def admin(self):
        template = env.get_template("html/admin.html")
        return template.render(admin=True)

    @cherrypy.expose
    def post(self, title, text):
        Post.create(
            title=title,
            text=text
        )

        raise cherrypy.HTTPRedirect("/#")

    @cherrypy.expose
    def blogpost(self, id):
        template = env.get_template("html/blogpost.html")
        post = Post.get(id=id)
        return template.render(p=post,
                               markdown=markdown,
                               re=re)

    @cherrypy.expose
    def blog(self):
        template = env.get_template("html/index.html")
        blog = Post.select().order_by(Post.date.asc())
        motdJson = requests.get("https://xkcd.com/info.0.json").json()
        motd = motdJson.get("img")
        return template.render(re=re,
                               blg=True,
                               blog=blog,
                               motd=motd,
                               title="Posts",
                               markdown=markdown)

    @cherrypy.expose
    def portfolio(self):
        template = env.get_template("html/portfolio.html")
        return template.render(port=True)


load_dotenv()
USERS = os.environ['USERS']
USERS = json.loads(USERS)

if __name__ == '__main__':
    conf = {
        'global': {
            'server.socket_host': 'ngaffney.netlify.app',
            'server.socket_port': int(os.environ.get('PORT', 8080)),
        },
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        },
        '/admin': {
            'tools.auth_digest.on': True,
            'tools.auth_digest.realm': 'localhost',
            'tools.auth_digest.get_ha1': auth_digest.get_ha1_dict_plain(USERS),
            'tools.auth_digest.key': os.environ['DIGESTKEY'],
            'tools.auth_digest.accept_charset': 'UTF-8',
        },
        '/post': {
            'tools.auth_digest.on': True,
            'tools.auth_digest.realm': 'localhost',
            'tools.auth_digest.get_ha1': auth_digest.get_ha1_dict_plain(USERS),
            'tools.auth_digest.key': os.environ['DIGESTKEY'],
            'tools.auth_digest.accept_charset': 'UTF-8',
        }
    }
    cherrypy.quickstart(Website(), '/', conf)

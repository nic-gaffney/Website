# Source code for my website gaffclant.com
import os.path

import cherrypy


class Website(object):
    @cherrypy.expose
    def index(self):
        return open("public/html/index.html")


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

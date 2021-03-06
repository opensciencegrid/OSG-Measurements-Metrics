#!/usr/bin/env python

import os

import cherrypy
from pkg_resources import resource_filename

from graphtool.web import WebHost
from gratia.tools.gratia_web import fix_matplotlib

def main():
    fix_matplotlib()
    os.environ.setdefault("DBPARAM_LOCATION", "/etc/DBParam.xml")
    filename = resource_filename("gratia.config", "website-basic.xml")
    WebHost( file=filename ) 
    cherrypy.engine.start() 
    cherrypy.engine.block()

if __name__ == '__main__':
    main()


#!/usr/bin/env python

import os
import cherrypy
from pkg_resources import resource_filename

from graphtool.web import WebHost

if 'DBPARAM_LOCATION' not in os.environ:
    os.environ['DBPARAM_LOCATION'] = '/etc/DBParam.xml'
if 'DBSECURITY_LOCATION' not in os.environ:
    os.environ['DBSECURITY_LOCATION'] = '/etc/DBParam.xml'
    
def main():
    filename = resource_filename("gratia.config", "website-devel.xml")
    WebHost(file=filename)
    #cherrypy.server.quickstart()
    cherrypy.engine.start() 
    cherrypy.engine.block()

if __name__ == '__main__':
    main()


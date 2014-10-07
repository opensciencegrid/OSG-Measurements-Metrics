#!/bin/bash

# Get Root Access
# stop service
# first uninstall in the correct order
# install again
# start service
echo "Root Access"
su root -c "service GratiaWeb stop ;
 rpm -e osg-measurements-metrics-web ; 
 rpm -e osg-measurements-metrics-db" 

#!/bin/bash


# Build RPM's
 ./buildrpms.sh ;
# Get Root Access
# stop service
# first uninstall in the correct order
# install again
# start service
echo "Root Access"
su root -c "service GratiaWeb stop ;
 rpm -e osg-measurements-metrics-web ; 
 rpm -e osg-measurements-metrics-db ; 
 cd ./dist ; 
rpm -ivh osg-measurements-metrics-db-1.3-$1.noarch.rpm ; 
rpm -ivh osg-measurements-metrics-web-1.3-$1.noarch.rpm ; 
 cd .. ; 
 service GratiaWeb start" 

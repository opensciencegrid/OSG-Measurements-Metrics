#!/bin/bash


# Build RPM's
./buildrpms.sh
cd ../graphtool
./buildrpms.sh
cd ../OSG-Measurements-Metrics
# Get Root Access
# stop service
# first uninstall in the correct order
# install again
# start service
echo "Root Access"
su root -c "service GratiaWeb stop ;
 rpm -e osg-measurements-metrics-web ; 
 rpm -e osg-measurements-metrics-db ; 
 rpm -e graphtool ; 

 cd ../graphtool/dist;
rpm -ivh graphtool-0.9.0-$2.noarch.rpm ;
 cd ../../OSG-Measurements-Metrics/dist;
rpm -ivh osg-measurements-metrics-db-1.6-$1.noarch.rpm ;
rpm -ivh osg-measurements-metrics-web-1.6-$1.noarch.rpm ;
 cd .. ; 
service GratiaWeb start;"

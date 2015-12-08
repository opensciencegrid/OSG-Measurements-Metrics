#!/bin/bash

echo "Root Access on $1"
kinit
# Build and copy RPM's
./buildrpms.sh
scp ./dist/osg-measurements-metrics-db-1.4-$2.noarch.rpm root@$1:~/
scp ./dist/osg-measurements-metrics-web-1.4-$2.noarch.rpm root@$1:~/
cd ../graphtool
./buildrpms.sh
scp ./dist/graphtool-0.8.0-$3.noarch.rpm root@$1:~/
cd ../OSG-Measurements-Metrics
# Get Root Access
# stop service
# first uninstall in the correct order
# install again
# start service
ssh root@$1 "service GratiaWeb stop ;
 rpm -e osg-measurements-metrics-web ; 
 rpm -e osg-measurements-metrics-db ; 
 rpm -e graphtool ; 
 cd ~/;
rpm -ivh graphtool-0.8.0-$3.noarch.rpm ;
rpm -ivh osg-measurements-metrics-db-1.4-$2.noarch.rpm ; 
rpm -ivh osg-measurements-metrics-web-1.4-$2.noarch.rpm ; 
 cd .. ; 
service GratiaWeb start;"
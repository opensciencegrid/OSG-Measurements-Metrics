import datetime
import json
import urllib2
import simplejson
import string
import os.path
from gratia.web.gratia_urls import GratiaURLS

class WLCGWebCap:
    def wlcg_capacity(self, month=datetime.datetime.now().month, year=datetime.datetime.now().year):     
            
        thisyear = str(year)
        debug=1
	sites_per_accountname={}
	fednames_and_accounts={}

        #fed_capacity = {}

        srchUrl = 'TopologyUrl'
        modName = 'wlcg_capacity'
        print "%s: srchUrl: %s" % (modName, srchUrl)
        try:
            url = getattr(globals()['GratiaURLS'](), 'GetUrl')(srchUrl)
            print "%s: SUCCESS: getattr(globals()['GratiaURLS'](), 'GetUrl')(%s)" \
                % (modName,srchUrl)
            print "%s: retUrl: %s" % (modName, url)
        except:
            print "%s: FAILED: getattr(globals()['GratiaURLS'](), 'GetUrl')(urlname=%s)" \
                % (modName,srchUrl)
            pass
        response  = urllib2.urlopen(url)
	s = response.read()
	x = simplejson.loads(s)
	#resourcesnestedlist=x['aaData']
	for obj in x:
	    if('USA'==obj['Country']):   
		try:
                    fednames_and_accounts[obj['Federation']]=obj['FederationAccountingName'] #Name is key
                except:
                    None

        if(debug > 0):
            print "debug: ======================================================"
            print "debug: fednames_and_accounts: "
            print "debug: ======================================================"
            print "debug: \t\t\t key      \t\t\t FederationName" 
            for key in fednames_and_accounts:
                print "debug: \t %30s   \t %20s" % (key, fednames_and_accounts[key])

        srchUrl = 'FedCapacityUrl'
        modName = 'wlcg_capacity'
        print "%s: srchUrl: %s" % (modName, srchUrl)
        try:
            url = getattr(globals()['GratiaURLS'](), 'GetUrl')(srchUrl)
            print "%s: SUCCESS: getattr(globals()['GratiaURLS'](), 'GetUrl')(%s)" % (modName,srchUrl)
            print "%s: retUrl: %s" % (modName, url)
        except:
            print "%s: FAILED: getattr(globals()['GratiaURLS'](), 'GetUrl')(urlname=%s)" % (modName,srchUrl)
            pass
        response  = urllib2.urlopen(url)
	s = response.read()
	x = simplejson.loads(s)
	#resourcesnestedlist=x['aaData']
        myCapList = []
	for obj in x:
            info = {}
	    if('USA'==obj['Country'] ):
		try:
                    info['FederationName'] = fednames_and_accounts[obj['Federation']]
                    info['Capacity'] = obj['HEPSPEC06']
                    info['PhysicalCPUs'] = obj['PhysicalCPUs']
                    info['LogicalCPUs']  = obj['LogicalCPUs']
                    info['TotalOnlineSize'] = obj['TotalOnlineSize']

		except:
		   None

                if(debug > 0):
                    print "-----------------------------------------------------"
                    print "FedName: %s" % info['FederationName']
                    print "Capacity: %s" % info['Capacity']
                    print "PhysicalCPUs: %s" % info['PhysicalCPUs']
                    print "LogicalCPUs: %s" % info['LogicalCPUs']
                    print "TotalOnlineSize: %s" % info['TotalOnlineSize']
                myCapList.append(info)

        if(debug > 0):
            print "debug: ================================================================================="
            print "debug:                                  Final Data Check"
            print "debug: ================================================================================="
            print "debug:                                      myCapList: "
            print "debug: ================================================================================="
            print "debug: \t     FederationName         Capacity    PhysicalCPUs    LogicalCPUs    TotalOnlineSize "
            for myRow in myCapList:
                print "debug: %20s \t %10s  %12s  %12s %20s" % (myRow['FederationName'], myRow['Capacity'],
                                                              myRow['PhysicalCPUs'],   myRow['LogicalCPUs'],
                                                              myRow['TotalOnlineSize'])

        return myCapList


#WLCGWebCap().wlcg_capacitys()


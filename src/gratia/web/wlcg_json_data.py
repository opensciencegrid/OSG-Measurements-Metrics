import datetime
import json
import urllib2
import simplejson
import string
import os.path
from gratia.web.gratia_urls import GratiaURLS

class WLCGWebUtil:
    def wlcg_pledges(self, month=datetime.datetime.now().month, year=datetime.datetime.now().year):     
            
        thisyear = str(year)
        debug=1
	sites_per_accountname={}
	fednames_and_accounts={}

        cms_fed = {}
        atlas_fed = {}
        alice_fed = {}

        cms_pledge = {}
        atlas_pledge = {}
        alice_pledge = {}

        #url = 'http://gstat-wlcg.cern.ch/apps/topology/2/json'
        srchUrl = 'TopologyUrl'
        modName = 'wlcg_pledges'
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
	for obj in x:
	    if('USA'==obj['Country']):   
		try:
			sites_per_accountname[obj['FederationAccountingName']].append(obj['Site'])
		except KeyError:
			sites_per_accountname[obj['FederationAccountingName']]=[obj['Site']]

		fednames_and_accounts[obj['Federation']]=obj['FederationAccountingName']#Name is key
	    if('USA'==obj['Country'] and obj['Federation'].find('CMS') >= 0):  
		cms_fed[obj['FederationAccountingName']]=1;
	    if('USA'==obj['Country'] and obj['Federation'].find('ATLAS') >= 0):  
		atlas_fed[obj['FederationAccountingName']]=1;
	    if('USA'==obj['Country'] and obj['Federation'].find('ALICE') >= 0):  
		alice_fed[obj['FederationAccountingName']]=1;
        if(debug > 0):
            print "debug: ======================================================"
            print "debug: sites_per_accountname: "
            print "debug: ======================================================"
            for key in sites_per_accountname:
                print "\ndebug:  FederationName: %s" % key	
                print "debug: \t\t ResourceGroups:"
                for key2 in sites_per_accountname[key]:
                    print "debug: \t\t\t %s"%(key2)	

            print "\ndebug: ======================================================"
            print "debug: cms_fed: CMS Federation Names"
            print "debug: ======================================================"
            for key in cms_fed:
                print "debug: \t\t %s " % key

            print "\ndebug: ======================================================"
            print "debug: atlas_fed: Atlas Federation Names"
            print "debug: ======================================================"
            for key in atlas_fed:
                print "debug: \t\t %s " % key

            print "\ndebug: ======================================================"
            print "debug: alice_fed: Alice Federation Names"
            print "debug: ======================================================"
            for key in alice_fed:
                print "debug: \t\t %s " % key

        #url = 'http://gstat-wlcg.cern.ch/apps/pledges/resources/'+thisyear+'/2/json'
        srchUrl = 'PledgeUrl'
        modName = 'wlcg_pledges'
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
	for obj in x:
	    if('USA'==obj['Country'] and 'HEP-SPEC06' == obj['PledgeUnit']):
		try:
		   int(obj['ATLAS']) #atlas number exists
                   atlas_pledge[fednames_and_accounts[obj['Federation']]] = \
                       {'pledge': obj['ATLAS'], 'ResourceGroups': \
                            sites_per_accountname[fednames_and_accounts[obj['Federation']]]}
		except:
		   None

		try:
		   int(obj['CMS']) #cms number exists
                   cms_pledge[fednames_and_accounts[obj['Federation']]] = \
                       {'pledge': obj['CMS'], 'ResourceGroups': \
                            sites_per_accountname[fednames_and_accounts[obj['Federation']]]}
		except:
		   None

		try:
		   int(obj['ALICE']) #alice number exists
                   alice_pledge[fednames_and_accounts[obj['Federation']]] = \
                       {'pledge': obj['ALICE'], 'ResourceGroups': \
                            sites_per_accountname[fednames_and_accounts[obj['Federation']]]}
		except:
		   None

        if(debug > 0):
            print "debug: ================================================================="
            print "debug: Final Data Check"
            print "debug: ================================================================="
            print "debug: cms_pledge: "
            print "debug: ======================================================"
            for key in cms_pledge:
                print "\ndebug:  FederationName: %s   Pledge: %s"%(key, cms_pledge[key]['pledge'])	
                print "debug: \t\t Resource Groups:"
                for key2 in cms_pledge[key]['ResourceGroups']:
                    print "debug: \t\t\t %s" % key2
            print "debug: ======================================================"
            print "debug: atlas_pledge: "
            print "debug: ======================================================"
            for key in atlas_pledge:
                print "\ndebug:  FederationName: %s   Pledge: %s"%(key, atlas_pledge[key]['pledge'])
                print "debug: \t\t Resource Groups:"
                for key2 in atlas_pledge[key]['ResourceGroups']:
                    print "debug: \t\t %s" % key2
            print "debug: ======================================================"
            print "debug: alice_pledge: "
            print "debug: ======================================================"
            for key in alice_pledge:
                print "\ndebug:  FederationName: %s   Pledge: %s"%(key, alice_pledge[key]['pledge'])	
                print "degub: \t\t Resource Groups:"
                for key2 in alice_pledge[key]['ResourceGroups']:
                    print "debug: \t\t\t %s" % key2
        if(debug > 1):
            print "\ndebug: ======================================================"
            print "debug: cms_fed: CMS Federation Accounting Names"
            print "debug: ======================================================"
            for key in cms_fed:
                print "debug:  \t\t %s" % key	

            print "\ndebug: ======================================================"
            print "debug: atlas_fed: Atlas Federation Accounting Names"
            print "debug: ======================================================"
            for key in atlas_fed:
                print "debug:  \t\t %s " % key	
            print "\ndebug: ======================================================"
            print "debug: alice_fed: Alice Federation Accounting Names"
            print "debug: ======================================================"
            for key in alice_fed:
                print "debug:  alice_fed: ",key	
        return atlas_pledge, cms_pledge, alice_pledge


#WLCGWebUtil().wlcg_pledges()


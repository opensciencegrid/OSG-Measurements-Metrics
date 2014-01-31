
import re
import sys
import time
import types
import urllib
import urllib2
import calendar
import datetime
import json
import os.path
import string
from xml.dom.minidom import parse
import ConfigParser
import cherrypy 
from pkg_resources import resource_stream
from operator import itemgetter, attrgetter

from graphtool.base.xml_config import XmlConfig
from auth import Authenticate
from gratia.web.gratia_urls import GratiaURLS
from wlcg_json_data import WLCGWebUtil
from wlcg_json_cap import WLCGWebCap

########################################################################
# supplies "year" "month" interval for web page queries - 2014Jan22 - wbh
########################################################################
def gratia_interval(year, month):
    info = {}
    info['starttime'] = datetime.datetime(year, month, 1, 0, 0, 0)
    last_day = calendar.monthrange(year, month)[1]
    info['endtime'] = datetime.datetime(year, month, last_day, 23, 59, 59)
    return info

class JOTReporter(Authenticate):

    ########################################################################
    # Extracts data text from xml doc page - 2014Jan22 - wbh
    ########################################################################
    #def getText(self, nodelist):
    #	    rc = ""
    #	    for node in nodelist:
    #	        if node.nodeType == node.TEXT_NODE:
    #	            rc = rc + node.data
    #	    return rc

    ###########################################################################
    # get pledge info - 2014Jan22 - wbh
    ###########################################################################
    def get_pledge_info(self, month, year):

	atlas_pledge, cms_pledge, alice_pledge = \
            WLCGWebUtil().wlcg_pledges(month, year)

        print "========== atlas_pledge ==================================================="
        print atlas_pledge
        print "============================================================="

        print "========== cms_pledge ==================================================="
        print cms_pledge
        print "============================================================="

        print "========== alice_pledge ==================================================="
        print alice_pledge
        print "============================================================="

        ###########################################################################
        # assuming: (pledged CPU hrs) Per (hour) Per (day) - 2013Jan28 - wbh
        ###########################################################################
        days_in_month = calendar.monthrange(year, month)[1]
        thisDay=datetime.datetime.now().day
        thisHour=datetime.datetime.now().hour 
        thisMinute=datetime.datetime.now().minute
        daily_mult = 24
        nextHour_fract = float(thisMinute) / float(60)
        thisTime_mult = float(daily_mult) * float(thisDay) + thisHour + nextHour_fract
        print "days_in_month: %d " % days_in_month
        print "daily_mult:    %d " % daily_mult
        print "thisDay:       %d " % thisDay
        print "thisHour:      %d " % thisHour
        print "nextHour_fract: %f " % nextHour_fract
        print "thisTime_mult: %f " % thisTime_mult

        myDailyPledgeCpuHrs = {}
        myNormTimePledgeCpuHrs = {}

        #############################################################################
        # pledge data - 2014Jan27 - wbh
        #############################################################################
        for key in atlas_pledge:
            mypledge = int(atlas_pledge[key]['pledge'])
            #myDailyPledgeCpuHrs[key]  = daily_mult * mypledge
            myNormTimePledgeCpuHrs[key] = thisTime_mult * mypledge

        for key in cms_pledge:
            mypledge = int(cms_pledge[key]['pledge'])
            #myDailyPledgeCpuHrs[key]  = daily_mult * mypledge
            myNormTimePledgeCpuHrs[key] = thisTime_mult * mypledge

        for key in alice_pledge:
            mypledge = int(alice_pledge[key]['pledge'])
            #myDailyPledgeCpuHrs[key]  = daily_mult * mypledge
            myNormTimePledgeCpuHrs[key] = thisTime_mult * mypledge

        return myDailyPledgeCpuHrs, myNormTimePledgeCpuHrs

    ###########################################################################
    def get_cap_info(self, month, year):

	FederationCapacity = WLCGWebCap().wlcg_capacity(month, year)

        print "================================== FederationCapacity ======================================"
        print "         FederationName      Capacity    PhysicalCPUs    LogicalCPUs    TotalOnlineSize "
        for myRow in FederationCapacity:
            print " %20s \t %10s  %12s  %12s %20s" % (myRow['FederationName'], myRow['Capacity'],
                                                      myRow['PhysicalCPUs'],   myRow['LogicalCPUs'],
                                                      myRow['TotalOnlineSize'])
        print "============================================================================================"

        ###########################################################################
        # assuming: (pledged CPU hrs) Per (hour) Per (day) - 2013Jan28 - wbh
        ###########################################################################
        days_in_month = calendar.monthrange(year, month)[1]
        thisDay=datetime.datetime.now().day
        thisHour=datetime.datetime.now().hour 
        thisMinute=datetime.datetime.now().minute
        daily_mult = 24
        nextHour_fract = float(thisMinute) / float(60)
        ###########################################################################
        # calculate factor for: hrs/day * days + numberHoursToday + fractionNextHour
        ###########################################################################
        thisTime_mult = float(daily_mult) * float(thisDay) + thisHour + nextHour_fract
        print "days_in_month: %d " % days_in_month
        print "daily_mult:    %d " % daily_mult
        print "thisDay:       %d " % thisDay
        print "thisHour:      %d " % thisHour
        print "nextHour_fract: %f " % nextHour_fract
        print "thisTime_mult: %f " % thisTime_mult

        myNormTimeCapCpuHrs = {}
        for myRow in FederationCapacity:
            myNormTimeCapCpuHrs[myRow['FederationName']] = int(round((thisTime_mult * myRow['Capacity']),0))

        print "myNormTimeCapCpuHrs: %s" % myNormTimeCapCpuHrs

        return myNormTimeCapCpuHrs

    ###########################################################################
    # key data source function - 2014Jan22 - wbh
    ###########################################################################
    def get_apel_data_jot(self, year=datetime.datetime.now().year, month=datetime.datetime.now().month):

        NormTimeCapCpuHrs = self.get_cap_info(month, year)

        DailyPledgeCpuHrs, NormTimePledgeCpuHrs = self.get_pledge_info(month, year)

        #print "====================================================="
        #print "debug: DailyPledgeCpuHrs:"
        #print "====================================================="
        #print "debug: \t\t\tFederation Name  \t\t DailyPledge "
        #print "debug: \t\t\t---------------- \t\t ------------ "
        #for key in DailyPledgeCpuHrs:
        #    print "debug:\t\t%20s     \t\t % 12d" % (key, DailyPledgeCpuHrs[key])

        print "====================================================="
        print "debug: NormTimePledgeCpuHrs:"
        print "====================================================="
        print "debug: \t\t\tFederation Name  \t\t ThisTimePledge "
        print "debug: \t\t\t---------------- \t\t ------------ "
        for key in NormTimePledgeCpuHrs:
            print "debug:\t\t%20s     \t\t % 12d" % (key, int(NormTimePledgeCpuHrs[key]))

        srchUrl = 'ApelUrl'
        modName = 'get_apel_data_jot'
        print "%s: srchUrl: %s" % (modName, srchUrl)
        try:
            apel_url = getattr(globals()['GratiaURLS'](), 'GetUrl')(srchUrl)
            print "%s: SUCCESS: getattr(globals()['GratiaURLS'](), 'GetUrl')(%s)" % (modName,srchUrl)
            print "%s: retUrl: %s" % (modName, apel_url)
        except:
            print "%s: FAILED: getattr(globals()['GratiaURLS'](), 'GetUrl')(urlname=%s)" % (modName,srchUrl)
            pass
        usock = urllib2.urlopen(apel_url)
        data = usock.read()
        usock.close()
        apel_data = []
        fed_rpt = []
        datafields = []
        numcells=13
        report_time     = None
        for i in range(numcells):
            datafields.append(0)
        datafields[0]="ResourceGroup"
        datafields[1]="NormFactor"
        datafields[2]="LCGUserVO"
        datafields[3]="Njobs"
        datafields[4]="SumCPU"
        datafields[5]="SumWCT"
        datafields[6]="Norm_CPU"
        datafields[7]="Norm_WCT"
        datafields[8]="RecordStart"
        datafields[9]="RecordEnd"
        datafields[10]="MeasurementDate"
        datafields[11]="FederationName"
        datafields[12]="ResourcesReporting"
        linesrec=data.split('\n')
        for line in linesrec:
            thisTuple=line.split('\t')
            print "thisTuple: %s" % thisTuple
            count=0
            info = {}
            fed_info = {}
            myFedName       = None
            myResourceGroup = None
            myNormCPU       = None
            normPledge      = None
            normCapacity    = None
            myPctPledge     = None
            for thisField in thisTuple:
                print "thisField: %s" % thisField
                if(thisField.strip() == ""):
                    continue
                if(count<numcells):
                    info[datafields[count]]=thisField
                    print "info[datafields[%d]]= %s" % (count, thisField)
                    if datafields[count] == 'ResourceGroup':
                        fed_info[datafields[count]] = thisField
                        myResourceGroup = thisField
                        print "debug: myResourceGroup: %s " % myResourceGroup
                    if datafields[count] == 'FederationName':
                        fed_info[datafields[count]] = thisField
                        myFedName = thisField
                        print "degug: myFedName: %s " % myFedName
                        for key in NormTimeCapCpuHrs:
                            if key == myFedName:
                                normCapacity = NormTimeCapCpuHrs[key]
                                print "debug: : myFedName: %20s \t normCapacity: % 12d" % \
                                    (key, normCapacity)
                    if datafields[count] == 'Norm_CPU':
                        myNormCPU = thisField
                        print "degug: myNormCPU: %s " % myNormCPU
                    if datafields[count] == 'ResourcesReporting':
                        fed_info[datafields[count]] = thisField
                        if myFedName is not None and \
                                (myResourceGroup is not None):
                           print "debug: myFedName: %s " % myFedName
                           print "debug: myResourceGroup: %s " % myResourceGroup
                           for key in NormTimePledgeCpuHrs.keys():
                               if key == myFedName:
                                   print "debug: MyFedName: %20s \t\t NormPledge: % 12d" % \
                                       (key, int(NormTimePledgeCpuHrs[key]))
                                   normPledge = int(NormTimePledgeCpuHrs[key])
                           if (myNormCPU is not None) and (normPledge is not None):
                               myPctPledge = round(100 * (float(myNormCPU) / float(normPledge)),2)
                               myPctPledgeStr = "%.2f" % myPctPledge
                               print "debug:   \t myPctPledgeStr: %s" % myPctPledgeStr
                if count<numcells and datafields[count] == 'MeasurementDate' and report_time == None:
                    report_time = thisField
                count=count+1
            if(not info):
                continue
            if (normPledge is None):
                continue
            info['NormPledge'] = normPledge
            info['PctPledge']  = myPctPledgeStr
            info['month']  = month
            info['year']   = year
            apel_data.append(info)
            print "info: %s" % info
            fed_info['NormPledge']   = normPledge
            fed_info['NormCapacity'] = normCapacity
            fed_rpt.append(fed_info)
            print "fed_info: %s" % fed_info
        return apel_data, report_time, fed_rpt

    ###########################################################################
    #                            Main   
    ###########################################################################
    def uslhc_table(self, year=datetime.datetime.now().year, 
            month=datetime.datetime.now().month, **kw):

        data = dict(kw)
        self.user_auth(data)
        self.user_roles(data)
        year = int(year)
        month = int(month)
        try:
            apel_data, report_time, fed_rpt = self.get_apel_data_jot(year, month)
            data['error'] = False
        except (KeyboardInterrupt, SystemExit):
            raise 
        except Exception, e:
            print >> sys.stderr, "Exception occurred while APEL data: %s" % str(e)
            data['title'] = "WLCG Reporting Info Error"
            data['error'] = True
            data['error_message'] = 'Exception occurred while fetching APEL data for <strong>Year:</strong> %s and <strong>Month:</strong> %s <br/></br/><strong>Details:</strong> %s' %(year, month,str(e))
            #raise e
            return data

        data['CPUHrs'] = {}
        data['normCPUHrs'] = {}
        data['wallHrs'] = {}
        data['jobs'] = {}

        ###########################################################################
        # To comply with request to sort by FederationName - 2013Jan24 - wbh
        ###########################################################################
        myApelDict = {}
        for apelRow in apel_data:
            print "apelRow: %s" % apelRow
            myKey = apelRow['FederationName'] + ',' + apelRow['ResourceGroup'] + \
                ',' + apelRow['LCGUserVO']
            myApelDict[myKey] = apelRow
        sortedApel = sorted(myApelDict.iteritems(), key=itemgetter(0))
        myNewApel = []
        for line in sortedApel:
            (myKey, myApelRow) = (line[0], line[1])
            print "myKey = %s" % myKey
            print "myApelRow = %s" % myApelRow
            myNewApel.append(myApelRow)

        ###########################################################################
        # To comply with request to sort by FederationName - 2013Jan24 - wbh
        ###########################################################################
        myFedDict = {}
        for fedRow in fed_rpt:
            print "fedRow: %s" % fedRow
            myKey = fedRow['FederationName'] + ',' + apelRow['ResourceGroup'] + \
                ',' + fedRow['ResourcesReporting']
            myFedDict[myKey] = fedRow
        sortedFed = sorted(myFedDict.iteritems(), key=itemgetter(0))
        myNewFed = []
        for line in sortedFed:
            (myKey, myFedRow) = (line[0], line[1])
            print "myKey = %s" % myKey
            print "myFedRow = %s" % myFedRow
            myNewFed.append(myFedRow)


        data['apel'] = myNewApel
        data['year'] = year
        data['month'] = month 
        data['month_name'] = calendar.month_name[month]
        data['report_time'] = report_time
        data['fedRpt'] = myNewFed
        
        time_info = gratia_interval(year, month)

        data['title'] = "WLCG Reporting Overview for %s %i" % \
            (calendar.month_name[month], year)

        return data


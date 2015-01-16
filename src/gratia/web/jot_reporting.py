
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

    ###########################################################################
    # key data source function - 2014Jan22 - wbh
    ###########################################################################
    def get_apel_data_jot(self, year=None, month=None):

        apel_data   = []
        report_time = None

        if (year is not None) and (month is not None):

            srchUrl = 'ApelUrl'
            modName = 'get_apel_data_jot'
            print "%s: srchUrl: %s" % (modName, srchUrl)
            try:
                apel_url = GratiaURLS().GetUrl(srchUrl, year, month)
            except:
                print "%s: ======================================" % modName
                print "%s: FAILED: GratiaURLS().GetUrl(url = %s)" % (modName,srchUrl)
                print "%s: ======================================" % modName
                pass
            else:
                print "%s: SUCCESS: GratiaURLS().GetUrl(url = %s)" % (modName,srchUrl)
                print "%s: retUrl: %s" % (modName, apel_url)
                try:
                    usock = urllib2.urlopen(apel_url)
                except urllib2.HTTPError, e:
                    print "%s: ======================================" % modName
                    print "%s: HTTPError: URL server couldn\'t fulfill the URL request." %modName
                    print modName, ': HTTPError: Error code: ', e.code
                    print modName, ': HTTPError:  ', e.read()
                    print "%s: ======================================" % modName
                    raise
                except urllib2.URLError, e:
                    print "%s: ======================================" % modName
                    print "%s: URLError: Failed to reach the URL server."
                    print modName, ": URLError: Reason: ", e.reason
                    print "%s: ======================================" % modName
                    raise
                else:
                    print "%s: ======================================" % modName
                    print "%s: Successful URL open to: %s" % (modName, apel_url)
                    print "%s: ======================================" % modName

                    data = usock.read()
                    usock.close()
                    datafields = []
                    numcells=13
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
                        for thisField in thisTuple:
                            print "thisField: %s" % thisField
                            if(thisField.strip() == ""):
                                continue
                            if(count<numcells):
                                info[datafields[count]]=thisField
                                print "info[datafields[%d]]= %s" % (count, thisField)
                            if count<numcells and datafields[count] == 'MeasurementDate' and report_time == None:
                                report_time = thisField
                            count=count+1
                        if(not info):
                            continue

                        info['month']  = month
                        info['year']   = year
                        apel_data.append(info)
                        print "info: %s" % info
        else:
            print "Error no (Month,Day) for the report"
        return apel_data, report_time

    ###########################################################################
    #                            Main   
    ###########################################################################
    def uslhc_table(self, year=None, month=None, **kw):

        data = dict(kw)
        self.user_auth(data)
        self.user_roles(data)

        print "================================================================="
        print "uslhc_table: month: %s    year: %s" % (month, year)
        print "================================================================="

        if year == None:
            year=datetime.datetime.now().year
        else:
            year = int(year)
        if month == None:
            month=datetime.datetime.now().month
        else:
            month = int(month)

        try:
            apel_data, report_time = self.get_apel_data_jot(year, month)
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
        myApelCnt = 0
        for line in sortedApel:
            (myKey, myApelRow) = (line[0], line[1])
            print "myKey = %s" % myKey
            print "myApelRow = %s" % myApelRow
            myNewApel.append(myApelRow)
            myApelCnt += 1

        myLastRecord = myApelCnt

        ###########################################################################
        # Requested to summarize by FederationName - 2014Feb12 - wbh
        ###########################################################################
        myLastFedName = None
        mySum_Njobs   = 0
        mySum_SumCpu  = 0
        mySum_SumWct  = 0
        mySum_NormCpu = 0
        mySum_PctEff  = 0
        cnt = 1
        mySumApelData = []
        mySumApel = {}
        for MyNewApelRow in myNewApel:
            print "MyNewApelRow %d: %s" % (cnt, MyNewApelRow)
            print "================================================================"
            #print "Debug: Before 'if': cnt: %d    myLastFedName: %s" % (cnt, myLastFedName)
            if (cnt == 1) and (myLastFedName == None):
                #print "Debug: -----------------------------------------------------------------"
                #print "Debug: top: (cnt ==1) and (myLastFedName == None)"
                myLastFedName  = MyNewApelRow['FederationName']
                mySum_Njobs    = int(MyNewApelRow['Njobs'])
                mySum_SumCPU   = int(MyNewApelRow['SumCPU'])
                mySum_SumWCT   = int(MyNewApelRow['SumWCT'])
                mySum_Norm_CPU = int(MyNewApelRow['Norm_CPU'])
                mySum_Norm_WCT = int(MyNewApelRow['Norm_WCT'])
                mySumApel['FederationName'] = MyNewApelRow['FederationName']
                #print "Debug: bottom: cnt: %d    myLastFedName: %s" % (cnt, myLastFedName)
                #print "Debug: mySumApel: %s" % mySumApel
                #print "Debug: -----------------------------------------------------------------"
            elif (MyNewApelRow['FederationName'] == myLastFedName):
                #print "Debug: -----------------------------------------------------------------"
                #print "Debug: top: (MyNewApelRow['FederationName'] == myLastFedName)"
                mySum_Njobs    = int(mySum_Njobs)    + int(MyNewApelRow['Njobs'])
                mySum_SumCPU   = int(mySum_SumCPU)   + int(MyNewApelRow['SumCPU'])
                mySum_SumWCT   = int(mySum_SumWCT)   + int(MyNewApelRow['SumWCT'])
                mySum_Norm_CPU = int(mySum_Norm_CPU) + int(MyNewApelRow['Norm_CPU'])
                mySum_Norm_WCT = int(mySum_Norm_WCT) + int(MyNewApelRow['Norm_WCT'])
                #print "Debug: bottom: cnt: %d    myLastFedName: %s" % (cnt, myLastFedName)
                #print "Debug: mySumApel: %s" % mySumApel
                #print "Debug: -----------------------------------------------------------------"
            else:
                #print "Debug: -----------------------------------------------------------------"
                #print "Debug: top: (MyNewApelRow['FederationName'] != myLastFedName)"
                mySumApel['Njobs']    = int(mySum_Njobs)
                mySumApel['SumCPU']   = int(mySum_SumCPU)
                mySumApel['SumWCT']   = int(mySum_SumWCT)
                mySumApel['Norm_CPU'] = int(mySum_Norm_CPU)
                mySumApel['Norm_WCT'] = int(mySum_Norm_WCT)
                # no div by 0
                if (mySum_SumWCT > 0):
                    mySum_PctEff = float(round(float(mySum_SumCPU * 100) / 
                                               (float(mySum_SumWCT)),0))
                else:
                    mySum_PctEff = 0
                mySumApel['PctEff']   = int(mySum_PctEff)
                #print "Debug: ==================================================================="
                #print "Debug: mySum_SumCPU: %f   mySum_SumWCT: %f  mySum_PctEff: %f" % \
                #           (mySum_SumCPU, mySum_SumWCT, mySum_PctEff)
                #print "Debug: ==================================================================="
                mySumApelData.append(mySumApel)
                print "==================================================="
                print "mySumApel = %s" % mySumApel
                print "---------------------------------------------------"
                print "mySumApelData: %s " % mySumApelData
                print "==================================================="
                #-------------------------------------------
                mySumApel     = {}
                mySum_Njobs   = 0
                mySum_SumCpu  = 0
                mySum_SumWct  = 0
                mySum_NormCpu = 0
                mySum_NormWCT = 0
                mySum_PctEff  = 0
                #-------------------------------------------
                myLastFedName  = MyNewApelRow['FederationName']
                mySum_Njobs    = int(MyNewApelRow['Njobs'])
                mySum_SumCPU   = int(MyNewApelRow['SumCPU'])
                mySum_SumWCT   = int(MyNewApelRow['SumWCT'])
                mySum_Norm_CPU = int(MyNewApelRow['Norm_CPU'])
                mySum_Norm_WCT = int(MyNewApelRow['Norm_WCT'])
                mySumApel['FederationName'] = MyNewApelRow['FederationName']
                #print "Debug: bottom: cnt: %d    myLastFedName: %s" % (cnt, myLastFedName)
                #print "Debug: mySumApel: %s" % mySumApel
                #print "Debug: -----------------------------------------------------------------"

            if (cnt == myLastRecord):
                #print "Debug: -----------------------------------------------------------------"
                #print "Debug: top: (cnt == myLastRecord)"
                mySumApel['Njobs']    = int(mySum_Njobs)
                mySumApel['SumCPU']   = int(mySum_SumCPU)
                mySumApel['SumWCT']   = int(mySum_SumWCT)
                mySumApel['Norm_CPU'] = int(mySum_Norm_CPU)
                mySumApel['Norm_WCT'] = int(mySum_Norm_WCT)
                # no div by 0
                if (mySum_SumWCT > 0):
                    mySum_PctEff = float(round(float(mySum_SumCPU * 100) / 
                                               (float(mySum_SumWCT)),0))
                else:
                    mySum_PctEff = 0
                mySumApel['PctEff']   = int(mySum_PctEff)
                print "Debug: ==================================================================="
                print "Debug: mySum_SumCPU: %f   mySum_SumWCT: %f  mySum_PctEff: %f" % \
                    (mySum_SumCPU, mySum_SumWCT, mySum_PctEff)
                print "Debug: ==================================================================="
                mySumApelData.append(mySumApel)
                print "==================================================="
                print "mySumApel = %s" % mySumApel
                print "---------------------------------------------------"
                print "mySumApelData: %s " % mySumApelData
                print "==================================================="
                #print "Debug: bottom: cnt: %d    myLastFedName: %s" % (cnt, myLastFedName)
                #print "Debug: mySumApel: %s" % mySumApel
                #print "Debug: -----------------------------------------------------------------"
            cnt += 1

        mySumApel     = {}
        print "==================================================="
        print "mySumApelData:"
        print "==================================================="
        for myRow in mySumApelData:
            print "\t %s " % myRow
        print "==================================================="

        data['apel'] = mySumApelData
        data['year'] = year
        data['month'] = month 
        data['month_name'] = calendar.month_name[month]
        data['report_time'] = report_time
        
        time_info = gratia_interval(year, month)

        data['title'] = "WLCG Reporting Overview for %s %i" % \
            (calendar.month_name[month], year)

        return data


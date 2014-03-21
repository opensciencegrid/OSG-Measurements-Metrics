import datetime
import urllib
import urllib2
import os
import sys
import string

class GratiaURLS:

    def GetUrl(self, urlname=None, inYear=datetime.datetime.now().year, 
                  inMonth=datetime.datetime.now().month ):
        """Simple GetUrl function to extract a Return Url by urlname """
        retUrl = None
        retUrl1 = None
        if urlname is not None:
            fname = "../config/urls_list.conf"
            dirPath  = os.path.dirname(__file__)
            filename = os.path.join(dirPath,fname)
            try:
                gfile = open (filename, "r", buffering=-1)
            except IOError:
                pstring = "gratia_urls: Error: Could not open local file: %s" % filename
                print (pstring)
                sys.exit()
            else:
                print "gratia_urls: Success opening file: %s" % filename
                urlsDict = {}
                #print "urlsDict: %s" % urlsDict
                #print "-------------------------"
                #print "urlsDict: "
                #print "-------------------------"
                for line in gfile.readlines():
                    #print "line: %s" % line
                    rowlist = []
                    rowlist = line.strip().split()
                    uname = rowlist[0].strip()
                    uadd  = rowlist[1].strip()
                    #print "uname: [%s]" % uname
                    #print "uadd: [%s]" % uadd
                    #print "-------------------------"
                    urlsDict[uname] = uadd

            #print "======================================================="
            #print "urlsDict: %s" % urlsDict
            #print "======================================================="

            print "urlname: %s" % urlname
            if (urlname in urlsDict.keys()):
                retUrlStr = urlsDict[urlname]
                print "GratiaURLS: GetUrl: retUrlStr: %s" % retUrlStr
                localvars = {}
                myYear = "{0:4d}".format(inYear)
                print "GratiaURLS: GetUrl: year: %s" % myYear
                myMonth = "{0:02d}".format(inMonth)
                print "GratiaURLS: GetUrl: month: %s" % myMonth
                print "GratiaURLS: GetUrl: var discovery %s is successful at %s-%s" % (urlname, myYear, myMonth)
                localvars = {'year': myYear, 'month': myMonth}
                print "GratiaURLS: GetUrl: localvars: ", localvars
                retUrl1 = retUrlStr.format(**localvars)
                retUrl = urllib2.Request(retUrl1)
                print "GratiaURLS: GetUrl: retUrl: %s" % retUrl

        else:
            print "GratiaURLS().GetUrl(): ERROR: 'Search_Url_Name' supplied: %s" % urlname
            raise Exception("GratiaURLS().GetUrl(): FAILED")
        return retUrl

#GratiaURLS().GetUrl(urlname)


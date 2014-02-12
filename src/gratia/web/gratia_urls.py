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
        if urlname is not None:
            urlsDict = {
                "ApelUrl": "http://gratia-apel-wlcg.opensciencegrid.org:8319/gratia-apel/{year}-{month}.summary.dat",
                "CpuInfoUrl": "http://myosg.grid.iu.edu/misccpuinfo/xml?count_sg_1&count_active=on&count_enabled=on&datasource=cpuinfo",
                "OimUrl": "http://myosg.grid.iu.edu/misccpuinfo/xml?datasource=cpuinfo&count_sg_1=on",
                "TopologyUrl": "http://gstat-wlcg.cern.ch/apps/topology/2/json",
                "PledgeUrl": "http://gstat-wlcg.cern.ch/apps/pledges/resources/{year}/2/json",
                "FedCapacityUrl": "http://gstat-wlcg.cern.ch/apps/capacities/federations/ALL/{year}/{month}/2/json",
                "PledgeTableUrl": "http://gratiaweb.grid.iu.edu/gratia/pledge_table",
                "GridviewBaseUrl": "http://grid-monitoring.cern.ch/mywlcg/sam-pi/group_availability_in_profile/",
                "GridResServUrl": "http://myosg.grid.iu.edu/miscmetric/xml?datasource=metric&metric_attrs_showservices=on",
                "OimVoFilterUrl": "http://myosg.grid.iu.edu/vosummary/xml?datasource=summary&all_vos=on&active_value=1",
                "OimResFilterUrl": "http://myosg.grid.iu.edu/rgsummary/xml?datasource=summary&all_resources=on&summary_attrs_showwlcg=on",
                "OimFosFilterUrl": "http://myosg.grid.iu.edu/miscproject/xml?count_sg_1&count_active=on&count_enabled=on",
                "OimScienceFilterUrl": "http://myosg.grid.iu.edu/vosummary/xml?datasource=summary&summary_attrs_showfield_of_science=on&all_vos=on&show",
                "EngageFilterUrl": "http://engage-central.renci.org/engage-sciences.csv",
                "NysGridFilterUrl": "https://www.ccr.buffalo.edu/download/attachments/31558659/NYSGrid-classifications.csv",
                "OverrideFilterUrl": "http://t2.unl.edu/store/override-classifications.csv",
                "TwikiFilterUrl": "https://twiki.grid.iu.edu/twiki/pub/MeasurementsAndMetrics/MetricScienceUsage/othermapping.csv",
                "VoOwnershipUrl": 'https://myosg.grid.iu.edu/rgsummary/xml?datasource=summary&summary_attrs_showvoownership=on&gip_status_attrs_showtestresults=on&downtime_attrs_showpast=&account_type=cumulative_hours&ce_account_type=gip_vo&se_account_type=vo_transfer_volume&bdiitree_type=total_jobs&bdii_object=service&bdii_server=is-osg&start_type=7daysago&start_date=02%2F02%2F2012&end_type=now&end_date=02%2F02%2F2012&all_resources=on&facility_10009=on&gridtype=on&gridtype_1=on&active_value=1&disable_value=1',
                "OimCriticalMetricsUrl": "http://myosg.grid.iu.edu/miscmetric/xml?datasource=metric&metric_attrs_showservices=on",
                "DashboardSummaryUrl": "http://lxarda09.cern.ch/dashboard/request.py/jobsummary",
                "DashboardStatusUrl": "http://lxarda09.cern.ch/dashboard/request.py/jobstatus",
                "LigoSiteInfoUrl": "http://t2.unl.edu/gratia/xml/site_info",
                "LigoSesameServerUrl": "http://buran.aei.mpg.de:25002/openrdf-sesame/repositories",
                "InitFontUrl": "http://scan.grid.iu.edu",
                "InitGipValidUrl": "http://gip-validate.grid.iu.edu/production",
                "InitD0Url": "http://physics.lunet.edu/~snow/d0osgprod.csv",
                "LastStatusUrl": "http://t2.unl.edu/gratia/xml/wlcg_last_status",
                "VoHoursUrl": "http://t2.unl.edu/gratia/xml/osg_vo_hours",
                "VoCountUrl": "http://t2.unl.edu/gratia/xml/osg_vo_count",
                "CmsTransfersUrl": "http://t2.unl.edu/phedex/xml/quantity_cumulative",
                "CmsTransfersProdUrl": "http://cmsweb.cern.ch/phedex/datasvc/json/prod/transferhistory",
                "CmsTransfersDebugUrl": "http://cmsweb.cern.ch/phedex/datasvc/json/debug/transferhistory",
                "GipUrl": "http://t2.unl.edu/gratia/xml/gip_facility",
                "GratiaUrl": "http://t2.unl.edu/gratia/xml/facility_hours_bar_smry",
                "RsvSamReliabilityUrl": "http://t2.unl.edu/gratia/xml/rsv_sam_reliability",
                "DashboardUrl": "http://dashb-atlas-data.cern.ch/dashboard/request.py/site",
                "AvailSummaryUrl": "http://t2.unl.edu/gratia/xml/avail_summary_daily",
                "FacilityWorkUrl": "http://t2.unl.edu/gratia/xml/facility_hours_bar_smry",
                "DashboardAnalyzerUrl": "http://dashb-cms-sam.cern.ch/dashboard/request.py/historicalserviceavailability.png",
                "GridScanUrl": "http://scan.grid.iu.edu/cgi-bin/get_grid_sv?",
                "GumsTemplateUrl": "http://software.grid.iu.edu/pacman/tarballs/vo-version/gums.template"
                }

            #print "urlsDict: %s" % urlsDict
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
            print "GratiaURLS: GetUrl: %s" % retUrl
        else:
            print "GratiaURLS().GetUrl(): ERROR: 'Search_Url_Name' supplied: %s" % urlname
            raise Exception("GratiaURLS().GetUrl(): FAILED")
        return retUrl

#GratiaURLS().GetUrl(urlname)


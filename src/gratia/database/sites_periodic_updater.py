import query_handler

import xml.dom.minidom
from gratia.web.gratia_urls import GratiaURLS

class OimSitesPeriodicUpdater(query_handler.PeriodicUpdater):

    def parse(self, results):
        dom = xml.dom.minidom.parseString(results)
        sites = []
        for child in dom.getElementsByTagName('ResourceGroup'):
            try:
                rg_name = child.getElementsByTagName('GroupName')[0].firstChild.data
                rg_added = False
                for child_res in child.getElementsByTagName('Resource'):
                    try:
                        r_name = child_res.getElementsByTagName('Name')[0].firstChild.data
                        for child_servs in child_res.getElementsByTagName('Service'):
                            service_name = child_servs.getElementsByTagName('Name')[0].firstChild.data
                            if service_name == "CE":
                                hidden_str = child_servs.getElementsByTagName('hidden')[0].firstChild.data
                                if hidden_str == "False":
                                    if not rg_added:
                                        sites.append(rg_name)
                                        rg_added = True
                                    sites.append(r_name)
                                    continue
                    except:
                        pass
            except:
                pass
        return sites

class OimCMST2Sites(OimSitesPeriodicUpdater):

    def __init__(self):
        srchUrl = 'OimCMST2SitesUrl'
        modName = 'OimCMST2Sites'
        print "%s: srchUrl: %s" % (modName, srchUrl)
        try:
            self.url = GratiaURLS().GetUrl(srchUrl)
            print "%s: SUCCESS: GratiaURLS().GetUrl(url = %s)" % (modName,srchUrl)
            print "%s: retUrl: %s" % (modName, self.url)
        except:
            print "%s: FAILED: GratiaURLS().GetUrl(url = %s)" % (modName,srchUrl)
            pass
        super(OimCMST2Sites, self).__init__(self.url)

oim_cms_t2_sites = OimCMST2Sites()



class OimWLCGSites(OimSitesPeriodicUpdater):

    def __init__(self):
        srchUrl = 'OimWLCGSitesUrl'
        modName = 'OimWLCGSites'
        print "%s: srchUrl: %s" % (modName, srchUrl)
        try:
            self.url = GratiaURLS().GetUrl(srchUrl)
            print "%s: SUCCESS: GratiaURLS().GetUrl(url = %s)" % (modName,srchUrl)
            print "%s: retUrl: %s" % (modName, self.url)
        except:
            print "%s: FAILED: GratiaURLS().GetUrl(url = %s)" % (modName,srchUrl)
            pass
        super(OimWLCGSites, self).__init__(self.url)
        
oim_wlcg_sites = OimWLCGSites()
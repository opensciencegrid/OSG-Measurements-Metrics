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
                sites.append(rg_name)
                for child in child.getElementsByTagName('Resource'):
                    try:
                        r_name = child.getElementsByTagName('Name')[0].firstChild.data
                        sites.append(r_name)
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
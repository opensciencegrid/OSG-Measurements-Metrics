import query_handler
import re

import xml.dom.minidom
from gratia.web.gratia_urls import GratiaURLS

def create_in_from_enumerable(enumerable,is_num=False):
    str_in = "("
    str_placeholder = "%s" if is_num else "'%s'"
    for i, item_i in enumerate(enumerable):
        str_in += (str_placeholder+ (")" if i==len(enumerable)-1 else ","))%str(item_i).lower()
    return str_in

def add_to_dict_grouping(dictionary,x,y):
  if not dictionary.has_key(x):
      dictionary[x] = []
  dictionary[x].append(y)

class OimVOOwnership(query_handler.PeriodicUpdater):

    """
    This object, when called, will return a dictionary
    containing the ownership description of VO/Facility
    loaded from OIM
    """

    def __init__(self):
        print "================================="
        srchUrl = 'VoOwnershipUrl'
        modName = 'OimVOOwnership'
        print "%s: srchUrl: %s" % (modName, srchUrl)
        try:
            self.url = GratiaURLS().GetUrl(srchUrl)
            print "%s: SUCCESS: GratiaURLS().GetUrl(url = %s)" % (modName,srchUrl)
            print "%s: retUrl: %s" % (modName, self.url)
        except:
            print "%s: FAILED: GratiaURLS().GetUrl(url = %s)" % (modName,srchUrl)
            pass
        super(OimVOOwnership, self).__init__(self.url)

    def parse(self, results):
        dom = xml.dom.minidom.parseString(results)
        vo_ownership_dict={}
        vo_set = set()
        facility_set = set()
        for node in dom.getElementsByTagName('Resource'):
            resourcename= (node.getElementsByTagName("Name"))
            for innernode in node.getElementsByTagName('Ownership'):
                voname= (innernode.getElementsByTagName("VO")) 
                t = voname[0].firstChild.nodeValue.encode("utf8"),resourcename[0].firstChild.nodeValue.encode("utf8")
                percent_num = 0
                p_str = None
                try:
                    p_str = innernode.getElementsByTagName("Percent")[0].firstChild.nodeValue.encode("utf8")
                    percent_num = int(p_str)
                except:
                    print "CAN'T CONVERT VO OWNERSHIP PERCENTAGE: %s" % p_str
                    percent_num = -1
                if percent_num > 0:
                    add_to_dict_grouping(vo_ownership_dict,t[0].lower(),t[1].lower())
                    vo_set.add(t[0].lower())
                    facility_set.add(t[1].lower())
        return vo_ownership_dict, vo_set, facility_set


    def build_sql(self,conn,is_batch,is_opportunistic):
        msd_var = "R"
        vo_ownership_dict, vo_set, facility_set = self.results()
        vo_corrids_sql = 'SELECT lower(VO.VOName), VC.corrid '\
                        'FROM VO as VO JOIN VONameCorrection VC ON (VC.void = VO.void) '\
                        'WHERE lower(VO.VOName) IN '+create_in_from_enumerable(vo_set)
        probenames_sites_sql = 'SELECT lower(S.SiteName), P.probename '\
                               'FROM Probe P JOIN Site S on S.siteid = P.siteid '\
                               'WHERE lower(S.SiteName) IN '+create_in_from_enumerable(facility_set)
        res = conn.execute_statement(vo_corrids_sql)
        vo_2_corrids = {}
        for record_i in res:
          add_to_dict_grouping(vo_2_corrids, record_i[0], record_i[1])
        res = conn.execute_statement(probenames_sites_sql)
        site_2_probename = {}
        for record_i in res:
          add_to_dict_grouping(site_2_probename, record_i[0], record_i[1])
        sql_select_owned = " (\nFALSE "
        for vo in vo_ownership_dict:
            if vo.lower() == "osg":
                continue
            if vo_2_corrids.has_key(vo):
                owned_facilities = vo_ownership_dict[vo]
                corrids_vo_i = vo_2_corrids[vo]
                temp_sql_vo = '\n OR (%s.VOcorrid IN '%msd_var+create_in_from_enumerable(corrids_vo_i,True)
                if is_batch:
                    probes = []
                    for facility_i in owned_facilities:
                        if site_2_probename.has_key(facility_i.lower()):
                            probes += site_2_probename[facility_i.lower()]
                    if len(probes) > 0:
                        sql_select_owned += temp_sql_vo+'\n      AND %s.ProbeName IN '%msd_var+create_in_from_enumerable(probes)+")"
                else:
                    if len(owned_facilities) > 0:
                        sql_select_owned += temp_sql_vo+'\n      AND lower(%s.HostDescription) IN '%msd_var+create_in_from_enumerable(owned_facilities)+")"
            else:
                print "UNKOWN VO: %s"%vo
        sql_select_owned += "\n)"
        if is_opportunistic:
            return " NOT "+sql_select_owned
        return sql_select_owned
        
    def alter_sql(self,sql_string,conn,**my_kw):
        if my_kw.has_key('opportunistic-filter'):
            filter_val = my_kw['opportunistic-filter']
            if filter_val == 'BOTH':
                return sql_string.replace(":opportunistic-filter","TRUE")
            if not my_kw.has_key('resource-type'):
                raise Exception("Missing resource-type parameter.")
            resource_type = my_kw['resource-type']
            is_batch = re.match(resource_type, 'Batch', re.IGNORECASE) is not None
            is_batchpilot = re.match(resource_type, 'BatchPilot', re.IGNORECASE) is not None
            if not is_batch and not is_batchpilot:
                raise Exception("resource-type parameter must be Batch or BatchPilot only.")
            is_opportunistic = filter_val=='OPPORTUNISTIC'
            try:
                return sql_string.replace(":opportunistic-filter",self.build_sql(conn,is_batch,is_opportunistic))
            except:
                import traceback
                traceback.print_exc()
        else:
            raise Exception("Missing opportunistic-filter parameter.")

oim_vo_ownership = OimVOOwnership()


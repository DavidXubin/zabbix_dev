import random
from zabbix_api import ZabbixAPI
from zabbix_api import ZabbixAPIException
from zabbix_api import Already_Exists
from zabbix_api import InvalidProtoError
from zabbix_api import APITimeout

g_color_table = ["000000", "FF0000", "00FF00", "0000FF", "FFFF00", "FF00CC",  "880066", "FFF143",
                 "FFA631", "AFDD22", "FF7500", "00BC12", "FFC773", "0AA344", "D6ECF0", "FFFBF0",
                 "E3F9FD", "BCE672", "C0EBD7", "21A675", "808080", "6B6882", "725E82", "A78E44",
                 "CA6924", "7FECAD", "75664D", "B35C44", "5D513C", "9B4400", "549688", "789262",
                 "758A99", "622A1D", "FF461F", "70F3FF", "FF2D51", "C32136", "1685A9", "ED5736",
                 "003472", "60281E", "4B5CC4", "C93756", "574266", "8D4BBB", "FF2121", "801DAE",
                 "FF3300", "003371", "CCA4E3", "EF7A82", "FF0097", "EAFF56", "9ED900", "789262"]


def LoginZabbixServer(server, username, password):

    try:
        zapi = ZabbixAPI(server=server, path="", log_level=6)
        zapi.login(username, password)
    except ZabbixAPIException, e:
        print e
        return False, None
    else:
        return True, zapi


def GetZabbixHostgroup(zapi, hostgroupName):

    try:
        zapi.hostgroup.create({"name": (hostgroupName)})
        hostgroup = zapi.hostgroup.get({"filter":{"name": hostgroupName}})

        return True, hostgroup

    except (InvalidProtoError, APITimeout), e:
        print e
        return False, None
    except Already_Exists:

        hostgroup = zapi.hostgroup.get({"filter":{"name": hostgroupName}})
        return True, hostgroup
    except ZabbixAPIException, e:
        print e
        return False, None


def DeleteZabbixHostgroup(zapi, hostgroup):

    try:
        gid = hostgroup[0]["groupid"]

        zapi.hostgroup.delete([gid])

        return True
    except ZabbixAPIException, e:
        print e
        return False


def GetZabbixHost(zapi, hostgroup, hostid, hostname, interfaceIP, interfacePort):

    try:
        groupId = hostgroup[0]["groupid"]

        zapi.host.create({"host" : (hostid), "name" : (hostname), "interfaces" : [{"type" : 1, "main" : 1, "useip" : 1, "ip" : (interfaceIP), "dns" : "", "port" : (interfacePort)}], "groups": [{"groupid" : (groupId)}]})

        host = zapi.host.get({"filter":{"host": hostid}, "output":["hostid", "host"], "selectInterfaces":["interfaceid", "ip"]})

        return True, host

    except (InvalidProtoError, APITimeout), e:
        print e
        return False, None
    except Already_Exists:

        host = zapi.host.get({"filter":{"host": hostid}, "output":["hostid", "host"], "selectInterfaces":["interfaceid", "ip"]})
        return True, host
    except ZabbixAPIException, e:
        print e
        return False, None


def GetZabbixHostByName(zapi, hostname):

    try:
        host = zapi.host.get({"filter":{"name": hostname}, "output":["hostid", "host"]})

        return True, host
    except (InvalidProtoError, APITimeout), e:
        print e
        return False, None
    except ZabbixAPIException, e:
        print e
        return False, None



def DeleteZabbixHost(zapi, host, template):

    try:
        hostid = host[0]["hostid"]

        templateId = template[0]["templateid"]

        zapi.host.update({"hostid" : (hostid), "templates_clear" : [{"templateid" : (templateId)}]})

        zapi.host.delete([hostid])

        return True
    except ZabbixAPIException, e:
        print e
        return False


def GetTemplate(zapi, template_name):

    try:
        hostgroup_name = "templates.mozy.all"

        hostgroup = zapi.hostgroup.get({"filter":{"name": hostgroup_name}})
        groupId = hostgroup[0]["groupid"]

        zapi.template.create({"host" : (template_name), "groups": (groupId)})

        template = zapi.template.get({"filter":{"host": template_name}, "output":["templateid", "host"]})

        return True, template

    except (InvalidProtoError, APITimeout), e:
        print e
        return False, None
    except Already_Exists:

        template = zapi.template.get({"filter":{"host": template_name}, "output":["templateid", "host"]})
        return True, template
    except ZabbixAPIException, e:
        print e
        return False, None


def DeleteTemplate(zapi, template):

    try:
        templateId = template[0]["templateid"]

        zapi.template.delete([templateId])

        return True
    except ZabbixAPIException, e:
        print e
        return False


def GetApplication(zapi, app_name, template):

    try:
        templateId = template[0]["templateid"]

        zapi.application.create({"hostid" : (templateId), "name": (app_name)})

        app = zapi.application.get({"filter":{"name": app_name}, "templated" : "true", "output" : ["applicationid", "name", "hostid"]})

        return True, app

    except (InvalidProtoError, APITimeout), e:
        print e
        return False, None
    except Already_Exists:

        app = zapi.application.get({"filter":{"name": app_name}, "templated" : "true", "output" : ["applicationid", "name", "hostid"]})
        return True, app
    except ZabbixAPIException, e:
        print e
        return False, None


def DeleteApplication(zapi, appList):

    try:
        appIDList = []
        for app in appList:
            appIDList.append(app[0]['applicationid'])

        if len(appIDList) > 0:
            zapi.application.delete(appIDList)
            return True
        else:
            return False
    except (InvalidProtoError, APITimeout), e:
        print e
        return False
    except ZabbixAPIException, e:
        print e
        return False


def GetZabbixItem(zapi, template, params, application = None):

    try:
        templateId = template[0]["templateid"]

        key = params["key"]
        name = params["name"]
        type = params["type"]
        value_type = params["value_type"]
        description = params["description"]
        history = params["history"]
        trends = params["trends"]

        if not application:
            zapi.item.create({'hostid' : (templateId), 'key_' : key,  'name' : (name), 'description' : (description), 'type' : (type), 'value_type' : (value_type), 'history' : (history), 'trends' : (trends)})
        else:
            appid = application[0]["applicationid"]
            zapi.item.create({'hostid' : (templateId), 'key_' : key,  'name' : (name), 'description' : (description), 'type' : (type), 'value_type' : (value_type), 'history' : (history), 'trends' : (trends), 'applications' : [appid]})

        item = zapi.item.get({"hostids" : templateId, "search":{"key_": key}, "output":["itemid", "key_", "hostid"]})

        return True, item
    except (InvalidProtoError, APITimeout), e:
        print e
        return False, None
    except Already_Exists:

        item = zapi.item.get({"hostids" : templateId, "search":{"key_": key} , "output":["itemid", "key_", "hostid"]})
        return True, item
    except ZabbixAPIException, e:
        print e
        return False, None


def GetZabbixTextItem(zapi, template, params, application = None):

    try:
        templateId = template[0]["templateid"]

        key = params["key"]
        name = params["name"]
        type = params["type"]
        value_type = params["value_type"]
        description = params["description"]

        if not application:
            zapi.item.create({'hostid' : (templateId), 'key_' : key,  'name' : (name), 'description' : (description), 'type' : (type), 'value_type' : (value_type)})
        else:
            appid = application[0]["applicationid"]
            zapi.item.create({'hostid' : (templateId), 'key_' : key,  'name' : (name), 'description' : (description), 'type' : (type), 'value_type' : (value_type), 'applications' : [appid]})

        item = zapi.item.get({"hostids" : templateId, "search":{"key_": key}, "output":["itemid", "key_", "hostid"]})

        return True, item
    except (InvalidProtoError, APITimeout), e:
        print e
        return False, None
    except Already_Exists:

        item = zapi.item.get({"hostids" : templateId, "search":{"key_": key} , "output":["itemid", "key_", "hostid"]})
        return True, item
    except ZabbixAPIException, e:
        print e
        return False, None


def GetZabbixAggregateItem(zapi, template, params, application = None):

    try:
        templateId = template[0]["templateid"]

        key = params["key"]
        name = params["name"]
        type = params["type"]
        value_type = params["value_type"]
        delay = params["delay"]
        history = params["history"]
        trends = params["trends"]

        if not application:
            zapi.item.create({'hostid' : (templateId), 'key_' : key,  'name' : (name), 'delay' : (delay), 'type' : (type), 'value_type' : (value_type), 'history' : (history), 'trends' : (trends)})
        else:
            appid = application[0]["applicationid"]
            zapi.item.create({'hostid' : (templateId), 'key_' : key,  'name' : (name), 'delay' : (delay), 'type' : (type), 'value_type' : (value_type), 'history' : (history), 'trends' : (trends), 'applications' : [appid]})

        item = zapi.item.get({"hostids" : templateId, "search":{"key_": key}, "output":["itemid", "key_", "hostid"]})

        return True, item
    except (InvalidProtoError, APITimeout), e:
        print e
        return False, None
    except Already_Exists:

        item = zapi.item.get({"hostids" : templateId, "search":{"key_": key} , "output":["itemid", "key_", "hostid"]})
        return True, item
    except ZabbixAPIException, e:
        print e
        return False, None


def DeleteItems(zapi, itemList):

    try:
        itemIDList = []
        for item in itemList:
            itemIDList.append(item[0]['itemid'])

        if len(itemIDList) > 0:
            zapi.item.delete(itemIDList)
            return True
        else:
            return False
    except (InvalidProtoError, APITimeout), e:
        print e
        return False
    except ZabbixAPIException, e:
        print e
        return False


def PickColor(pickedList):
    global g_color_table

    if len(pickedList) > 0:
        availColorSet = set(g_color_table).difference(set(pickedList))
    else:
        availColorSet = g_color_table

    i = random.randint(0, len(availColorSet) - 1)

    return list(availColorSet)[i]


def GetGraph(zapi, graph_name, itemList, template = None, width = 900, height = 200):

    try:
        gitems = []
        pickedColorList = []

        for item in itemList:
            color = PickColor(pickedColorList)
            pickedColorList.append(color)

            gitems.append({"itemid" : item[0]["itemid"], "color" : (color)})

        if template:
            templateId = template[0]["templateid"]
            zapi.graph.create({"name" : (graph_name), "width" : (width), "height" : (height), "templateid" : (templateId), "gitems" : (gitems)})
        else:
            zapi.graph.create({"name" : (graph_name), "width" : (width), "height" : (height), "gitems" : (gitems)})

        graph = zapi.graph.get({"filter":{"name": graph_name}, "output":["graphid", "name"]})

        return True, graph
    except (InvalidProtoError, APITimeout), e:
        print e
        return False, None
    except Already_Exists:

        graph = zapi.graph.get({"filter":{"name": graph_name}, "output":["graphid", "name"]})
        return True, graph
    except ZabbixAPIException, e:
        print e
        return False, None


def GetGraphByHost(zapi, hostIDList, graphName = ""):

    try:
        if len(graphName) > 0:
            graph = zapi.graph.get({'hostids' : hostIDList, 'search':{'name' : graphName}, 'output' : 'extend'})
        else:
            graph = zapi.graph.get({'hostids' : hostIDList,  'output' : 'extend'})
        return True, graph
    except (InvalidProtoError, APITimeout), e:
        print e
        return False, None
    except ZabbixAPIException, e:
        print e
        return False, None


def GetGraphByTemplate(zapi, hostIDList, template):

    try:
        templateId = template[0]["templateid"]

        graph = zapi.graph.get({'hostids' : hostIDList, 'search':{'templateid' : templateId}, 'output' : 'extend'})

        return True, graph
    except (InvalidProtoError, APITimeout), e:
        print e
        return False, None
    except ZabbixAPIException, e:
        print e
        return False, None


def DeleteGraph(zapi, graph):
    try:
        graphId = graph[0]["graphid"]

        zapi.graph.delete([graphId])

        return True
    except ZabbixAPIException, e:
        print e
        return False

def LinkTemplateToHost(zapi, host, template):

    try:
        templateId = template[0]["templateid"]

        hostid = host[0]["hostid"]

        zapi.host.update({"hostid" : (hostid), "templates" : [{"templateid" : (templateId)}]})

        return True
    except (InvalidProtoError, APITimeout), e:
        print e
        return False
    except ZabbixAPIException, e:
        print e
        return False


def DeleteAllZabbixHostGroup(zapi, hostgroupList):

    for key in hostgroupList.iterkeys():
        DeleteZabbixHostgroup(zapi, hostgroupList[key])


def DeleteAllZabbixHost(zapi, hostList, template):

    for key in hostList.iterkeys():
        DeleteZabbixHost(zapi, hostList[key], template)


def DeleteAllGraph(zapi, graphList):

    for key in graphList.iterkeys():
        DeleteGraph(zapi, graphList[key])


def GetAllItems(zapi, template, parmaList, app = None):
    itemList = {}

    for key in parmaList.iterkeys():
        if parmaList[key]["value_type"] != 4:
            ret, item = GetZabbixItem(zapi, template, parmaList[key], app)
        else:
            ret, item = GetZabbixTextItem(zapi, template, parmaList[key], app)
        if not ret: return False, None

        itemList[key] = item

    return True, itemList


def GetAllAggregateItems(zapi, template, parmaList, app = None):
    itemList = {}

    for key in parmaList.iterkeys():
        ret, item = GetZabbixAggregateItem(zapi, template, parmaList[key], app)
        if not ret: return False, None

        itemList[key] = item

    return True, itemList


def LinkTemplateToHosts(zapi, template, hostList):

    for key in hostList.iterkeys():
        if not LinkTemplateToHost(zapi, hostList[key], template):
            return False

    return True

def createScreen(zapi, screenName, hsize):

    try:
        totalItemNum = 0
        vsize = 0
        hpos = 0
        vpos = 0
        curItemIDList = []

        screen = zapi.screen.get({'filter': {"name" : screenName}, 'selectScreenItems':'extend', 'output':'extend'})
        if screen:
            if int(screen[0]['hsize']) != int(hsize) :
                raise ZabbixAPIException("Couldn't update screen, existing screen hsize = %s, request screen hsize = %s" % (screen[0]['hsize'], hsize))

            for item in screen[0]['screenitems'] :

                if hpos >= (hsize - 1) :
                    hpos = 0
                    vpos += 1
                else:
                    hpos += 1

                curItemIDList.append(item['resourceid'])

        newScreenItemList = []

        for item in screenItemList :

            if item['resourceid'] not in curItemIDList:

                if screen :
                    item['screenid'] = screen[0]['screenid']

                item['x'] = hpos
                item['y'] = vpos

                newScreenItemList.append(item)

            hpos += 1
            if hpos >= hsize :
                hpos = 0
                vpos += 1

        if screen :
            totalItemNum = len(screen[0]['screenitems'])
            totalItemNum += len(newScreenItemList)
            vsize = totalItemNum / hsize
            if totalItemNum % hsize != 0:
                vsize += 1

            zapi.screen.update({'screenid' : screen[0]['screenid'], 'hsize' : hsize, 'vsize' : vsize})
            for item in newScreenItemList :
                zapi.screenitem.create(item)
        else :
            totalItemNum = len(screenItemList)
            vsize = totalItemNum / hsize
            if totalItemNum % hsize != 0:
                vsize += 1

            zapi.screen.create({'name' : screenName, 'hsize' : hsize, 'vsize' : vsize, 'screenitems' : screenItemList})

        return True
    except (InvalidProtoError, APITimeout), e:
        print e
        return False
    except ZabbixAPIException, e:
        print e
        return False


def UpdateScreen(zapi, screenName, width, height, colspan, rowspan):

    try:
        screen = zapi.screen.get({'filter': {"name" : screenName}, 'selectScreenItems':'extend', 'output':'extend'})
        if not screen:
            raise ZabbixAPIException("The screen of %s does not exist!" % screenName)

        for item in screen[0]['screenitems'] :
            item['width'] = width
            item['height'] = height
            item['colspan'] = colspan
            item['rowspan'] = rowspan

            zapi.screenitem.update(item)

        zapi.screen.update({'screenid' : screen[0]['screenid'], 'screenitems' : screen[0]['screenitems']})
        return True
    except (InvalidProtoError, APITimeout), e:
        print e
        return False
    except ZabbixAPIException, e:
        print e
        return False


def DeleteScreen(zapi, screenNameList):

    try:
        screenIDList = []
        for screenName in screenNameList:
            ret, screen = GetScreen(zapi, screenName)
            if ret:
                screenIDList.append(screen[0]['screenid'])
            else:
                print "The screen of %s does not exist!" % screenName

        if len(screenIDList) > 0:
            zapi.screen.delete(screenIDList)
            return True
        else:
            return False
    except (InvalidProtoError, APITimeout), e:
        print e
        return False
    except ZabbixAPIException, e:
        print e
        return False



def GetScreen(zapi, screenName):
    try:
        screen = zapi.screen.get({'filter': {"name" : screenName}, 'selectScreenItems':'extend', 'output':'extend'})
        if screen:
            return True, screen
        else:
            return False, None
    except (InvalidProtoError, APITimeout), e:
        print e
        return False, None
    except ZabbixAPIException, e:
        print e
        return False, None


def MakeScreenItem(resourceId, resourceType = 0, width = 500, height = 100, colspan = 1, rowspan = 1, x = 0, y = 0):

    return dict(colspan = colspan, rowspan = rowspan, resourcetype = resourceType, resourceid = resourceId, x = x, y = y, width = width, height = height)



def GetZabbixItemsByApp(zapi, template, appName):

    try:
        templateiId = template[0]["templateid"]
        ret, app = GetApplication(zapi, appName, template)
        if not ret:
            raise ZabbixAPIException("The app of %s is not found" % appName)

        itemList = zapi.item.get({"applicationids" : [app[0]["applicationid"]], "search":{"templateid": templateiId},  "output":["itemid", "key_", "name", "type", "value_type"]})

        return True, itemList

    except ZabbixAPIException, e:
        print e
        return False, None


def GetZabbixItemsByTemplate(zapi, template):

    try:
        templateiId = template[0]["templateid"]
        itemList = zapi.item.get({"templateids" : [templateiId],  "output":["itemid", "key_", "name", "type", "value_type"]})

        return True, itemList

    except ZabbixAPIException, e:
        print e
        return False, None


def GetZabbixItemsByName(zapi, template, itemName):

    try:
        templateiId = template[0]["templateid"]

        item = zapi.item.get({"templateids" : [templateiId], "search" : {"name" : itemName}, "output":["itemid", "key_", "name", "type", "value_type"]})

        return True, item
    except ZabbixAPIException, e:
        print e
        return False, None


def GetZabbixItemsBykey(zapi, template, key):

    try:
        templateiId = template[0]["templateid"]

        item = zapi.item.get({"templateids" : [templateiId], "search" : {"key_" : key}, "output":["itemid", "key_", "name", "type", "value_type"]})

        return True, item
    except ZabbixAPIException, e:
        print e
        return False, None

def GetZabbixItemsByHost(zapi, hostName):

    try:
        itemList = zapi.item.get({"host" : hostName, "output":["itemid", "key_", "name", "type", "value_type"]})

        return True, itemList
    except ZabbixAPIException, e:
        print e
        return False, None


def GetzabbixItemsByGroup(zapi, groupName):

    try:
        itemList = zapi.item.get({"group" : groupName, "output":["itemid", "key_", "name", "type", "value_type"]})

        return True, itemList
    except ZabbixAPIException, e:
        print e
        return False, None


def GetZabbixItemByNameExt(zapi, hostIdList, itemName):

    try:
        item = zapi.item.get({"hostids" : hostIdList, "search" : {"name" : itemName}, "output":["itemid", "key_", "name", "type", "value_type"]})

        return True, item
    except ZabbixAPIException, e:
        print e
        return False, None


def GetZabbixItemByKeyExt(zapi, hostIdList, key):

    try:
        item = zapi.item.get({"hostids" : hostIdList, "search" : {"key_" : key}, "output":["itemid", "key_", "name", "type", "value_type"]})

        return True, item
    except ZabbixAPIException, e:
        print e
        return False, None


def GetZabbixItemsByAppExt(zapi, hostIdList, template, appName):

    try:
        ret, itemList = GetZabbixItemsByApp(zapi, template, appName)
        keyList = []
        for item in itemList:
            keyList.append(item["key_"])

        templateiId = template[0]["templateid"]
        itemList = zapi.item.get({"hostids" : hostIdList, "search":{"templateid": templateiId},  "output":["itemid", "key_", "name", "type", "value_type"]})

        filterItemList = []
        for item in itemList:
            if item["key_"] in keyList:
                filterItemList.append(item)

        return True, filterItemList

    except ZabbixAPIException, e:
        print e
        return False, None

def GetZabbixItemsByTemplateExt(zapi, hostIdList, template):

    try:
        templateiId = template[0]["templateid"]
        itemList = zapi.item.get({"hostids" : hostIdList, "search":{"templateid": templateiId},  "output":["itemid", "key_", "name", "type", "value_type"]})

        return True, itemList

    except ZabbixAPIException, e:
        print e
        return False, None


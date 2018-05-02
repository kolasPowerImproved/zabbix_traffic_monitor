from datetime import datetime
from datetime import date
import time
import numpy

from pyzabbix import ZabbixAPI, ZabbixAPIException

from consts import LOGIN_ZABBIX, PASSWORD_ZABBIX, SERVER_ZABBIX

vl780 = "32938"
vl1804 = "33258"
vl1088 = "32808"
vl940 = "32901"
vl777 = "32932"
vl775 = "32934"
vl65 = "32960"
vl800 = "32960"

z = ZabbixAPI(SERVER_ZABBIX)
z.login(user=LOGIN_ZABBIX, password=PASSWORD_ZABBIX)


def get_graphs_ids(hostid):
    """
    Get all graphs ids from the host
    :param hostid:
    :return: list with ids
    """
    result = z.do_request(method="graph.get", params={
        "output": "name",
        "hostids": hostid,
        "sortfield": "name"
    })
    return result


def get_item_id_from_graph_id(graphid):
    """
    get items ids wich are on the graph
    :param graphid:
    :return: list with items ids
    """
    result = z.do_request(method="graphitem.get", params={
        "output": "extend",
        "graphids": graphid
    })
    return result['result'][0]['itemid']


def get_item_data_from_itemid(itemid, time_from, time_till):
    """
    get traffic data for the item
    :param itemid:
    :param time_from:
    :param time_till:
    :return: list with all traffic data per 5 minutes
    """
    result = z.do_request(method="history.get", params={
        "output": "extend",
        "itemids": itemid,
        "time_from": time_from,
        "time_till": time_till
    })

    data = []

    for d in result['result']:
        data.append(int(d['value']))

    return data


def get_data(vlan, time_from, time_till):
    """
    get traffic data for vlan
    :param vlan:
    :param time_from:
    :param time_till:
    :return: list with all traffic data per 5 minutes for vlan
    """
    vlan_data = get_item_id_from_graph_id(vlan)
    data = get_item_data_from_itemid(vlan_data, time_from, time_till)
    return data


def get_mean_traffic(data_array):
    """
    get mean state foe all traffic for vlan
    :param data_array:
    :return: mean state
    """
    numpy_array = numpy.array(data_array)
    mean = numpy.mean(numpy_array, axis=0)
    mean_gb = mean / 1000000000
    return mean_gb


def get_max_traffic(data_array):
    """
    get maximum traffic data for vlan
    :param data_array:
    :return: maximum traffic state for vlan
    """
    numpy_array = numpy.array(data_array)
    max = numpy.amax(numpy_array)
    max_gb = max / 1000000000
    return max_gb


def get_fact_mean_traffic(maximum, mean):
    """
    get fact mean traffic state for vlan
    calculating with maximum traffic + mean traffic / 2
    :param maximum:
    :param mean:
    :return: fact mean traffic state for vlan
    """
    fact_mean = (maximum + mean) / 2
    return fact_mean


def get_percentile_traffic(data_array):
    """
    get percentile traffic state for vlan
    use 95% percentile
    :param data_array:
    :return: 95% percentile traffic state for vlan
    """
    numpy_array = numpy.array(data_array)
    percentile = numpy.percentile(numpy_array, 95, axis=0) / 1000000000
    return percentile


def get_traffic_info(vlan, time_from, time_till):
    """
    get maximum, mean, fact mean, 95% percentile traffic state for vlan
    :param vlan: set vlan from the vlan's list
    :param time_from: must be in unix timestamp format
    :param time_till: must be in unix timestamp format
    :return: all info about vlan =)))
    """
    data = get_data(vlan, time_from, time_till)
    mean = get_mean_traffic(data)
    maximum = get_max_traffic(data)
    fact_mean = get_fact_mean_traffic(maximum, mean)
    percentile = get_percentile_traffic(data)
    info = []
    info.append(maximum)
    info.append(mean)
    info.append(fact_mean)
    info.append(percentile)
    return info


# time_till = time.mktime(datetime.now().timetuple())
# time_from = time_till - 60 * 60 * 4

time_till = date(2018, 3, 26)                   # get traffic till time
time_from = date(2018, 3, 25)                   # get traffic from time

time_till_unix_timestamp = time.mktime(time_till.timetuple())    # convert till time to unix timestamp
time_from_unix_timestamp = time.mktime(time_from.timetuple())    # convert from time to unix timestamp

info_vlan780 = get_traffic_info(vl780, time_from_unix_timestamp, time_till_unix_timestamp)      # get traffic info for vlan 780
info_vlan1804 = get_traffic_info(vl1804, time_from_unix_timestamp, time_till_unix_timestamp)    # get traffic info for vlan 1804
info_vlan777 = get_traffic_info(vl777, time_from_unix_timestamp, time_till_unix_timestamp)      # get traffic info for vlan 777

print("info vlan 780 (Gb):")
print("maximum:     ", info_vlan780[0])
print("mean:        ", info_vlan780[1])
print("fact mean:   ", info_vlan780[2])
print("percentile:  ", info_vlan780[3])

print("\n------------------------------------------------\n")

print("info vlan 1804 (Gb):")
print("maximum:     ", info_vlan1804[0])
print("mean:        ", info_vlan1804[1])
print("fact mean:   ", info_vlan1804[2])
print("percentile:  ", info_vlan1804[3])

print("\n------------------------------------------------\n")

print("info vlan 777 (Gb):")
print("maximum:     ", info_vlan777[0])
print("mean:        ", info_vlan777[1])
print("fact mean:   ", info_vlan777[2])
print("percentile:  ", info_vlan777[3])


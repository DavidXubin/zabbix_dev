#!/usr/bin/python

import os
import re
import random
import tempfile
import time
import subprocess
import datetime
import log_wrapper

class ZabbixSender(object):

    def __init__(self, agent_hostname=None, zabbix_server=None, zabbix_port = 10051, source_ip = None, **kwargs):
        """
        Arguments:
        agent_hostname  -- Required for active checks and must match hostname as configured on the server
        zabbix_server   -- Hostname or IP address of Zabbix Server
        zabbix_port     -- Port number of Zabbix Server trapper running on the server. Default is 10051
        source_ip       -- Source IP address for outgoing connections, must match it as configured
                           on the server, or don't specify it

        Keyword arguments:
        config_file     -- Zabbix agent daemon configuration file, if specified all above arguments
                           will be ignored and we'll load config from this file
                           NOTE: Before using config_file, folder '/etc/zabbix/zabbix_agentd/' should be created
        """
        if kwargs.has_key('config_file'):
            self.config_file = kwargs['config_file']
        else:
            self.config_file = None
        self.zabbix_server = zabbix_server
        self.agent_hostname = agent_hostname
        self.zabbix_port = zabbix_port
        self.source_ip = source_ip

    def __get_metric_lines(self, items):
        """ Composite zabbix metrics line:
            "<agent_hostname> <key> <value>"
                or
            "<agent_hostname> <key> <timestamp> <value>"
        """
        lines = []

        item_count = 0
        for item in items:
            if item_count == 0:
                item_count = len(item)
            elif item_count != len(item):
                raise Exception("Element of items should not be heterogeneous")

            line = ''
            if self.agent_hostname:
                line = self.agent_hostname
            elif self.config_file:
                # TODO: zabbix_sender 1.8.2 couldn't use 'Hostname' from 'zabbix_agentd.conf' file,
                # should parse 'Hostname' from the config file, refer to:
                # https://support.zabbix.com/browse/ZBXNEXT-360
                line = '-'
            else:
                line = '-'

            for e in item:
                line += ' ' + str(e)
            lines.append(line)

        return lines

    def __zabbix_cmd_str(self, temp_file):
        """ Composite zabbix_sender command line
        """
        cmd_str = "zabbix_sender -vv --input-file %s" % temp_file

        if self.config_file:
            cmd_str += ' --config %s' % self.config_file
        if self.zabbix_server:
            cmd_str += ' --zabbix-server %s' % self.zabbix_server
        if self.zabbix_port:
            cmd_str += ' --port %d' % int(self.zabbix_port)
        if self.source_ip:
            cmd_str += ' --source-address %s' % self.source_ip
        if self.agent_hostname:
            cmd_str += ' --host %s' % self.agent_hostname

        #print "cmd_str: ", cmd_str
        return cmd_str

    def __get_result(self, return_code, stdout):
        data = stdout.read()
        log_wrapper.logWrapper.GetInstance().warning(data)
        
        result = {}
        result['return_code'] = return_code
        result['total_count'] = _extract_value(data, 'total:')
        result['processed_count'] = _extract_value(data, 'processed:')
        result['failed_count'] = _extract_value(data, 'failed:')
        result['skipped_count'] = _extract_value(data, 'skipped:')
        return result

    def __do_send(self, items):
        """
        Send metrics to zabbix server via zabbix_sender command
        """

        metric_lines = self.__get_metric_lines(items)
        fd, temp_file = tempfile.mkstemp()
        try:

            # write metric lines to temp file
            for line in metric_lines:
                os.write(fd, line + '\n')
            os.close(fd)
            fd = 0

            # composite zabbix_sender command line str
            cmd_str = self.__zabbix_cmd_str(temp_file)
            # execute zabbix_sender command
            #args = re.split('\ +', cmd_str)
            process = subprocess.Popen(cmd_str, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            return_code = process.wait()

            #line = process.stderr.readlines()

            #log_wrapper.logWrapper.GetInstance().warning(str(line))

            return self.__get_result(return_code, process.stdout)
        except Exception:
            return {'return_code' : -1,
                    'total_count' : len(items),
                    'processed_count' : 0,
                    'failed_count' : 0,
                    'skipped_count' : len(items)
                   }
        finally:
            # close file handle
            if fd and fd > 0:
                os.close(fd)

            # remove temp file
            os.remove(temp_file)


    def send_item(self, key, value, timestamp = None):
        """
        Arguments:
        key         -- Specify item key to send value to
        value       -- Specify value
        timestamp   -- Timestamp should be specified in Unix timestamp format(seconds from epoch).
                       If target item has triggers referencing it, all timestamps must be
                       in an increasing order, otherwise event calculation will not be correct.

        Return:
            dict{'return_code' : <-1|0|1|2>,
                 'total_count' : <int>,
                 'processed_count' : <int>,
                 'failed_count' : <int>,
                 'skipped_count' : <int>
                }

            About return_code:
                If zabbix_sender < 2.2:
                    It's always 0
                If zabbix_sender >= 2.2:
                    It's 0 if the values were sent and all of them were
                        successfully processed by server,
                    it's 2 if data was sent, but processing of at least
                        one of the values failed,
                    it's 1 if data sending failed.
        """
        if timestamp:
            return self.__do_send([(key, timestamp, value)])
        else:
            return self.__do_send([(key, value)])

    def send_items(self, items):
        """
        Keyword args:
        items - list of metric item tuple: (key, timestamp, value) or (key, value), but for
                each call of send_items, element count in meric item tuple should be same
        """
        return self.__do_send(items)


def _extract_value(data, key):
    """
    Extract value from zabbix_sender result stdout
    """
    matched_obj = re.search('.*%s ([0-9])+' % key, data)
    if matched_obj:
        return int(matched_obj.group(1))
    else:
        return '-'


"""
# following code is supposed as example of ZabbixSender
if __name__ == '__main__':
    sender = ZabbixSender('trogdor03', '10.29.108.41')
    #sender = ZabbixSender('trogdor03', config_file='/etc/zabbix/zabbix_agentd.conf')
    for i in range(0, 10):
        print sender.send_item('get.error.http_503_23', random.randint(0, 10))
        items = [('get.error.http_503_24', random.randint(50, 100)), ('get.error.http_503_602', random.randint(5, 10))]
        print sender.send_items(items)
        time.sleep(2)
"""

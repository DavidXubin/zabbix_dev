#!/usr/bin/env python
import os
import threading
import logging
from logging.handlers import RotatingFileHandler
import zabbix_settings as settings

class logWrapper(object):

    __DEFAULT_LOG_FILE_PATH = settings.log_path  + "tdn_monitor.log"
    __DEFAULT_LOG_NAME = 'tdn_metric'

    instance = None
    mutex = threading.Lock()

    def __init__(self):
        if not os.path.exists(settings.log_path):
            os.mkdir(settings.log_path)
        self.setup(logWrapper.__DEFAULT_LOG_NAME, logWrapper.__DEFAULT_LOG_FILE_PATH)

    @staticmethod
    def GetInstance():
        if logWrapper.instance == None:
            logWrapper.mutex.acquire()

            if logWrapper.instance == None:
                logWrapper.instance = logWrapper()

            logWrapper.mutex.release()

        return logWrapper.instance.logger

    def setup(self, logName, logFilePath, maxMBytesPerLog = 10, logCount = 7):
        """
        Arguments:
        logName   -- log name
        logFilePath  -- the log path
        maxMBytesPerLog  -- max bytes per log, unit is MB
        logCount -- the number of logs to roll
        """
        self.logger = logging.getLogger(logName)
        self.logger.setLevel(logging.WARNING)
        Rthandler = RotatingFileHandler(logFilePath, maxBytes = maxMBytesPerLog << 20, backupCount = logCount)
        formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt = "%Y-%m-%d %H:%M:%S")
        Rthandler.setFormatter(formatter)
        self.logger.addHandler(Rthandler)



#!/usr/bin/env python
import os
import fcntl

class flockWrapper(object):

    __lockfd = None
    __is_locked = False

    @staticmethod
    def lock():
        flockWrapper.__lockfd = open(os.path.realpath(__file__), 'r')
        fcntl.flock(flockWrapper.__lockfd, fcntl.LOCK_EX)
        flockWrapper.__is_locked = True

    @staticmethod
    def try_lock():
        try:
            flockWrapper.__lockfd = open(os.path.realpath(__file__), 'r')
            fcntl.flock(flockWrapper.__lockfd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except:
            flockWrapper.__is_locked = False
            return False
        else:
            flockWrapper.__is_locked = True
            return True

    @staticmethod
    def unlock():
        if flockWrapper.__is_locked:
            fcntl.flock(flockWrapper.__lockfd, fcntl.LOCK_UN)
            flockWrapper.__is_locked = False

        if flockWrapper.__lockfd and not flockWrapper.__is_locked:
            flockWrapper.__lockfd.close()
            flockWrapper.__lockfd = None

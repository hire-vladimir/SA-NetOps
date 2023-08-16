#!/usr/bin/env python3
welcomeText = '''#
# hire.vladimir@gmail.com
#
# takes in OUI dataset from the IEEE at the OUI_DATASET_URL, makes it pretty csv
#
# rev. history
# 9/28/15 1.0 initial write
#
'''
import time, re
import logging, logging.handlers
import requests
import sys

#######################################
# SCRIPT CONFIG
#######################################
# set log level valid options are: (NOTSET will disable logging)
# CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
LOG_LEVEL = logging.INFO
OUI_DATASET_URL = "https://standards-oui.ieee.org/oui/oui.txt"


def setup_logging():  # setup logging
    log_format = "%(asctime)s %(levelname)-s\t%(module)s[%(process)d]:%(lineno)d - %(message)s"
    logger = logging.getLogger('v')
    logger.setLevel(LOG_LEVEL)

    # ..and (optionally) output to console
    logH = logging.StreamHandler()
    logH.setFormatter(logging.Formatter(fmt=log_format))
    logger.addHandler(logH)

    logger.propagate = False
    return logger


def die(msg):
    logger.error(msg)
    exit(msg)


def getDataPayload(uri):
    logger.debug("Request uri=\"%s\"" % uri)
    payload = ""
    try:
        with requests.get(uri) as response:
            response.raise_for_status()
            payload = response.content
        logger.debug('Received payload="%s"' % payload)
    except requests.HTTPError as e:
        die('HTTP exception was thrown while making request for uri="%s", status_code=%s, e="%s"' % (uri, e.code, e))

    logger.info('function="getDataPayload" action="success" request="%s", bytes_in="%s"' % (uri, len(payload)))
    return payload.decode('utf-8')


if __name__ == '__main__':
    logger = setup_logging()
    logger.info('starting..')
    eStart = time.time()
    wspace = re.compile('\\s+')
    try:
        data = ""
        logger.debug("calling args_count=\"%d\" args=\"%s\"" % (len(sys.argv), str(sys.argv)))
        if len(sys.argv) > 1:
            filename = sys.argv[1]
            if filename[0:1] != "/":
                filename = "./%s" % filename

            with open(filename, "r") as oui:
                data = oui.read()
        else:
            data = getDataPayload(OUI_DATASET_URL)

        pattern = "(?P<mac>\w{6})\s+\(base\s16\)\s+(?:(?P<mac_vendor>[^\n\r]+)[\n\r]+)(?:\s+(?P<mac_vendor_address>[^\n\r]+)[\n\r]+)?(?:\s+(?P<mac_vendor_address2>[^\n\r]+)[\n\r]+)?(?:\s+(?P<mac_vendor_country>\w{2}))?[\n\r]"
        ma = re.findall(pattern, data)

        logger.debug("there are %d matches" % len(ma))

        print('mac,mac_vendor,mac_vendor_address,mac_vendor_address2,mac_vendor_country')
        ma.sort()
        for mac, mac_vendor, mac_vendor_address, mac_vendor_address2, mac_vendor_country in ma:
            # per http://docs.splunk.com/Documentation/CIM/latest/User/NetworkTraffic
            normalized_mac = "%s:%s:%s" % (mac[0:2], mac[2:4], mac[4:6])
            print('"%s*","%s","%s","%s","%s"' % (normalized_mac.lower(), mac_vendor,
                                                 ' '.join(wspace.split(mac_vendor_address)),
                                                 ' '.join(wspace.split(mac_vendor_address2)), mac_vendor_country))
    except Exception as e:
        logger.error('error while processing events, exception="%s"' % e)
        # raise Exception(e)
    finally:
        logger.info('exiting, execution duration=%s seconds' % (time.time() - eStart))

#!/usr/bin/env python
##
## This program is licensed under the GPL v3.0, which is found at the URL below:
##	http://opensource.org/licenses/gpl-3.0.html
##
## Copyright (c) 2012, ww@9Rivers.com. All rights reserved.

import re, sys
from os import path
from splunk.clilib import cli_common as cli
from splunklib.searchcommands import dispatch, StreamingCommand, Configuration, Option, validators


delims = re.compile("[^0-9a-f]")


class InvalidMACAddress(Exception):
    '''Exception for invalid MAC address.
    '''
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return 'Invalid MAC address: {0}'.format(self.value)


def split(mac, seg=2):
    '''To handle missing leading 0's in the given MAC address.
    '''
    x = _none(mac)
    return [ x[i:i+seg] for i in range(0, 12, seg) ]

def _cisco(mac):
    ''' 1122.3344.5566 '''
    return '.'.join(split(mac, 4))

def _dash(mac):
    ''' 11-22-33-44-55-66 '''
    return '-'.join(split(mac))

def _ieee(mac):
    ''' 11:22:33:44:55:66 '''
    return ':'.join(split(mac))

def _none(mac):
    ''' 112233445566 '''
    x = delims.split(mac.lower())
    if len(x) == 6:
        return ''.join([('00'+xe)[-2:] for xe in x])
    if len(x) == 3:
        return ''.join([('0000'+xe)[-4:] for xe in x ])
    if len(x) == 1:
        return ('0'*12+x[0])[-12:]
    raise InvalidMACAddress(mac)


@Configuration()
class MACFormatCommand(StreamingCommand):
    """ Convert a given MAC address field to specified format.

    ##Syntax

    .. code-block::
        | macformat input=field-list output=field-list format=[cisco|dash|ieee|none]

    ## Description

    Convert the fields in the `input` field list to the ones in the `output` list; Both lists are
    optional. The `input` list defaults to `macaddress`. The`output` list is filled with fields in
    the `input` list it the `output` list is shorter than the `input`.

    The `format` option is one of [cisco|dash|ieee|none]. The default is `none`.

    Raises a ValueError exception if the MAC address is invalid.
    """
    format = Option(
        doc='''
        **Syntax:** **format=**`[cisco|dash|ieee|none]`
        **Description:** Format of the output MAC address. Defaults to `none`.''',
        require=False, validate=validators.Set('cisco', 'dash', 'ieee', 'none')
        )

    inputs = Option(
        doc='''
        **Syntax:** **inputs=***<field-list>*
        **Description:** A comma-delimited list of input fields to convert. Defaults to `macaddress`.''',
        require=False, validate=validators.List()
        )

    outputs = Option(
        doc='''
        **Syntax:** **outputs=***<field-list>*
        **Description:** A comma-delimited list of fields for the results. Defaults to `inputs`.''',
        require=False, validate=validators.List()
        )

    def prepare(self):
        """ Prepare the options.

        :return: :const:`None`
        :rtype: NoneType
        """
        self.toform = globals()['_'+(self.format or self.def_format)]
        inputs = self.inputs
        if inputs is None:
            self.inputs = inputs = self.def_inputs
        outputs = self.outputs
        if outputs is None:
            outputs = inputs
        elif len(outputs) < len(inputs):
            outputs += inputs[len(outputs):]
        self.outputs = outputs
        self.logger.debug('MACFormatCommand.prepare: inputs = %s, outputs = %s', self.inputs, outputs)

    def stream(self, records):
        toform = self.toform
        inputs = self.inputs
        outputs = self.outputs
        if outputs is None:
            outputs = inputs
        elif len(outputs) < len(inputs):
            outputs += inputs[len(outputs):]
        for record in records:
            self.logger.debug('MACFormatCommand: record = %s', record)
            for i in range(len(inputs)):
                mac = record.get(inputs[i])
                if mac != None:
                    record[outputs[i]] = toform(mac)
            yield record

    def __init__(self):
        StreamingCommand.__init__(self)
        appdir = path.dirname(path.dirname(__file__))
        defconfpath = path.join(appdir, "default", "app.conf")
        defconf = cli.readConfFile(defconfpath).get('macformat') or {}
        localconfpath = path.join(appdir, "local", "app.conf")
        localconf = (cli.readConfFile(localconfpath).get('macformat') or {}) if path.exists(localconfpath) else {}
        self.def_format = localconf.get('format') or defconf.get('format') or 'none'
        inputs = localconf.get('inputs') or defconf.get('inputs')
        self.def_inputs = re.split('[\s,]', inputs) if inputs else ['macaddress']

dispatch(MACFormatCommand, sys.argv, sys.stdin, sys.stdout, __name__)

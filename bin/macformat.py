#!/usr/bin/env python
##
## This program is licensed under the GPL v3.0, which is found at the URL below:
##	http://opensource.org/licenses/gpl-3.0.html
##
## Copyright (c) 2012, ww@9Rivers.com. All rights reserved.

import re, sys
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
        default='none',
        require=False, validate=validators.Set('cisco', 'dash', 'ieee', 'none')
        )

    inputs = Option(
        doc='''
        **Syntax:** **inputs=***<field-list>*
        **Description:** A comma-delimited list of input fields to convert. Defaults to `macaddress`.''',
        default=['macaddress'],
        require=False, validate=validators.List()
        )

    outputs = Option(
        doc='''
        **Syntax:** **outputs=***<field-list>*
        **Description:** A comma-delimited list of fields for the results. Defaults to `inputs`.''',
        require=False, validate=validators.List()
        )

    def __init__(self):
	super(MACFormatCommand, self).__init__()
        self.logger.debug('MACFormatCommand: format=%s, inputs=%s', self.format, self.inputs)
        if not self.inputs:
            self.inputs = ['macaddress']
        if self.outputs is None:
            self.outputs = self.inputs
        if len(self.outputs) < len(self.inputs):
            self.output += self.inputs[len(self.outputs):]

    def stream(self, records):
        self.logger.debug('MACFormatCommand.stream: format=%s, inputs=%s, outputs=%s', self.format, self.inputs, self.outputs)
        toformat = globals()['_'+self.format]
        inputs = self.inputs
        outputs = self.outputs
        for record in records:
            self.logger.debug('MACFormatCommand: record = %s', record)
            for i in range(len(inputs)):
                mac = record.get(inputs[i])
                if mac != None:
                    record[outputs[i]] = toformat(mac)
            yield record

dispatch(MACFormatCommand, sys.argv, sys.stdin, sys.stdout, __name__)

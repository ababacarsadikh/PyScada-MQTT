#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from pyscada.utils.scheduler import SingleDeviceDAQProcessWorker
from pyscada.utils.scheduler import Process as BaseProcess
from pyscada.mqtt import PROTOCOL_ID

import logging


logger = logging.getLogger(__name__)


class Process(SingleDeviceDAQProcessWorker):
    device_filter = dict(mqttbroker__isnull=False, protocol_id=PROTOCOL_ID)
    bp_label = "pyscada.mqtt-%s"

    def __init__(self, dt=5, **kwargs):
        super(SingleDeviceDAQProcessWorker, self).__init__(dt=dt, **kwargs)

    def gen_group_id(self, item):
        # every broker gets its own process
        return "%d-%s:%s" % (item.pk, item.mqttbroker.ip_address, item.mqttbroker.port)

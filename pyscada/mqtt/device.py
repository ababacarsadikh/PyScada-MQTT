# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import paho.mqtt.client as mqtt
from pyscada.device import GenericDevice
from .devices import GenericDevice as GenericHandlerDevice


try:
    import paho.mqtt.client as mqtt_client

    driver_ok = True
except ImportError:
    driver_ok = False

from time import time
import logging

logger = logging.getLogger(__name__)


class Device(GenericDevice):
    def __init__(self, device):
        self.driver_ok = driver_ok
        self.handler_class = GenericHandlerDevice
        super().__init__(device)

        for var in self.device.variable_set.filter(active=1):
            if not hasattr(var, "mqttvariable"):
                continue
            self.variables[var.pk] = var

        if self.driver_ok and self.driver_handler_ok:
            self._h.connect()
        else:
            logger.warning(f"Cannot import mqtt or handler for {self.device}")

    def write_data(self, topic, value, task):
        """
        write value to the instrument/device
        """
        output = []
        if not self.driver_ok:
            logger.info("Cannot import MQTT client")
            return output

        for item in self.variables.values():
            if item.id == variable_id):
                continue
            
            read_value = self._h.write_data(variable_id, value, task)
            if read_value is not None and item.update_values([read_value], [time()]):
                output.append(item)
            else:
                logger.debug(f"No data to read after write for {task}")
        return output

    def request_data(self):
        """
        request data from the instrument/device
        """
        output = []
        if not self.driver_ok:
            logger.info("Cannot import paho mqtt")
            return output

        output = super().request_data()
        return output

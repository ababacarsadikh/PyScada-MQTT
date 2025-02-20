from __future__ import unicode_literals
from .. import PROTOCOL_ID
from pyscada.models import DeviceProtocol
from pyscada.device import GenericHandlerDevice

from django.conf import settings

try:
    import paho.mqtt.client as mqtt

    driver_ok = True
except ImportError:
    visa = None
    driver_ok = False

from time import time

import logging

logger = logging.getLogger(__name__)


class GenericDevice(GenericHandlerDevice):
    def __init__(self, pyscada_device, variables):
        super().__init__(pyscada_device, variables)
        self._protocol = PROTOCOL_ID
        self.driver_ok = driver_ok
        self.mqtt_client = None

    def connect(self):
        """
        establish a connection to the Instrument
        """
        super().connect()
        result = True

        try:
            self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
            self.mqtt_client.username_pw_set(
                self._device.mqttbroker.username, self._device.mqttbroker.password
            )

            self.mqtt_client.on_connect = self.on_connect
            self.mqtt_client.on_message = self.on_message

            self.mqtt_client.connect(
                self._device.mqttbroker.address,
                int(self._device.mqttbroker.port),
                int(self._device.mqttbroker.timeout),
            )

            self.mqtt_client.loop_start()
            logger.info("Connected MQTT .")
        except Exception as e:
            self._not_accessible_reason = f"Error MQTT connection: {e}"
            result = False

        return result

    def disconnect(self):
        """
        disconnect to the Instrument
        """
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            logger.info("Disconnected from MQTT.")
            return True
        return False


    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("connected to MQTTs.")
            for variable in self._device.variable_set.filter(active=1):
                if hasattr(variable, "mqttvariable"):
                    client.subscribe(variable.mqttvariable.topic)
        else:
            logger.warning(f"Not connected to MQTT, code : {rc}")

    def on_message(self, client, userdata, message):

        logger.info(f"Message received {message.topic}: {message.payload.decode()}")

    def read_data(self, variable_instance):
        return None

    def read_data_all(self, variables_dict):
        return None

    def write_data(self, topic, value, task):
        if self.mqtt_client:
            self.mqtt_client.publish(topic, value)
            logger.info(f"Publish to {topic}: {value}")
        return False

    def parse_value(self, value, **kwargs):
            return None

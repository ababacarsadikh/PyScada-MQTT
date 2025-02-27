from __future__ import unicode_literals
from .. import PROTOCOL_ID
from pyscada.models import DeviceProtocol
from pyscada.device import GenericHandlerDevice

from django.conf import settings

try:
    import paho.mqtt.client as mqtt
    driver_ok = True
except ImportError:
    driver_ok = False

from time import time

import logging

logger = logging.getLogger(__name__)


class GenericDevice(GenericHandlerDevice):
    def __init__(self, pyscada_device, variables):
        super().__init__(pyscada_device, variables)
        self._protocol = PROTOCOL_ID
        self.driver_ok = driver_ok
        self._address = self._device.mqttbroker.address
        self._port = self._device.mqttbroker.port
        self._timeout = self._device.mqttbroker.timeout
        self.data = (
            {}
        )  # holds the raw data for each topic, Value is None if no new data is there
        self.timestamp = (
            {}
        )  # holds timestamp received with a message topic
        self.broker = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2)
        self.broker.on_connect = self.on_connect
        self.broker.on_message = self.on_message
        self.broker.username = self._device.mqttbroker.username
        self.broker.password = self._device.mqttbroker.password
        self._connect()

    def connect(self):
        """
        establish a connection to the Instrument
        """
        super().connect()
        result = True

        try:
            self.broker.connect(
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
        if self.broker:
            self.broker.loop_stop()
            self.broker.disconnect()
            logger.info("Disconnected from MQTT.")
            return True
        return False


    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("connected to MQTTs.")
            for variable in self._variables:
                client.subscribe(variable.mqttvariable.topic)
                self.data[variable.mqttvariable.topic] = None
                if variable.mqttvariable.timestamp_topic is not None:
                    client.subscribe(
                        variable.mqttvariable.timestamp_topic
                    )  # timestamp Topic
                    self.data[variable.mqttvariable.timestamp_topic] = None
        else:
            logger.warning(f"Not connected to MQTT, code : {rc}")

    def on_message(self, client, userdata, message):
        """callback for new PUBLISH messages, is called on receive from Server"""
        logger.info(f"Message received {message.topic}: {message.payload.decode("utf-8")}")
        if msg.topic not in self.data:
            return
        self.data[msg.topic] = msg.payload
        if msg.timestamp:
            self.timestamp[msg.topic] = msg.timestamp

    def read_data_and_time(self, variable_instance):
        value = None
        timestamp = self.time()
        keys_to_reset = []
        if variable_instance.mqttvariable.topic in self.data:
            value = self.data[variable_instance.mqttvariable.topic].decode("utf-8")
            value = variable_instance.mqttvariable.parse_value(value)

            if variable_instance.mqttvariable.timestamp_topic is not None:
                if variable_instance.mqttvariable.timestamp_topice in self.data:
                    logger.debug(f"mqtt read_data {variable_instance.mqttvariable.timestamp_topic} is None")
                    continue

                timestamp = self.data[variable_instance.mqttvariable.timestamp_topic].decode(
                    "utf-8"
                )
                timestamp = variable_instance.mqttvariable.parse_timestamp(
                    timestamp
                )  # convert

                keys_to_reset.append(variable_instance.mqttvariable.timestamp_topic)
            elif variable_instance.mqttvariable.topic in self.timestamp:
                timestamp = self.timestamp[ variable_instance.mqttvariable.topic]

            self.data[variable_instance.mqttvariable.topic] = (
                None  # reset value for next loop, this is done here for the case that we recieved the value, but waiting for the timestamp
            )
        for key in keys_to_reset:
            self.data[key] = None  # reset value for next loop
            
        return value, timestamp
            
    def write_data(self, variable_id, value, task):
        if self.connect() and variable_id in self._variables:
            topic = self._variables[variable_id].mqttvariable.topic
            timestamp_topic = self._variables[variable_id].mqttvariable.timestamp_topic
            if self.broker:
                self.broker.publish(topic, value)
                logger.info(f"Publish to {topic}: {value}")
                self.write_timestamp(variable_id, value, task)
        return value

    def write_timestamp(self, variable_id, value, task):
        timestamp_topic = self._variables[variable_id].mqttvariable.timestamp_topic
        if timestamp_topic is not None:
            self.broker.publish(timestamp_topic, self.time())

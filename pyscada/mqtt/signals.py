# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Device, Variable
from pyscada.mqtt.models import (
    MQTTBroker,
    MQTTVariable,
    ExtendedMQTTBroker,
    ExtendedMQTTVariable,
)

from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete

import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=MQTTBroker)
@receiver(post_save, sender=MQTTVariable)
@receiver(post_save, sender=ExtendedMQTTBroker)
@receiver(post_save, sender=ExtendedMQTTVariable)
def _reinit_daq_daemons(sender, instance, **kwargs):
    """
    update the daq daemon configuration when changes be applied in the models
    """
    if type(instance) is MQTTBroker:
        post_save.send_robust(sender=Device, instance=instance.mqtt_broker)
    elif type(instance) is MQTTVariable:
        post_save.send_robust(sender=Variable, instance=instance.mqtt_variable)
    elif type(instance) is ExtendedMQTTVariable:
        post_save.send_robust(
            sender=Variable, instance=Variable.objects.get(pk=instance.pk)
        )
    elif type(instance) is ExtendedMQTTBroker:
        post_save.send_robust(
            sender=Device, instance=Device.objects.get(pk=instance.pk)
        )


@receiver(pre_delete, sender=MQTTBroker)
@receiver(pre_delete, sender=MQTTVariable)
@receiver(pre_delete, sender=ExtendedMQTTBroker)
@receiver(pre_delete, sender=ExtendedMQTTVariable)
def _del_daq_daemons(sender, instance, **kwargs):
    """
    update the daq daemon configuration when changes be applied in the models
    """
    if type(instance) is MQTTBroker:
        pre_delete.send_robust(sender=Device, instance=instance.mqtt_broker)
    elif type(instance) is MQTTVariable:
        pre_delete.send_robust(sender=Variable, instance=instance.mqtt_variable)
    elif type(instance) is ExtendedMQTTVariable:
        pre_delete.send_robust(
            sender=Variable, instance=Variable.objects.get(pk=instance.pk)
        )
    elif type(instance) is ExtendedMQTTDevice:
        pre_delete.send_robust(
            sender=Device, instance=Device.objects.get(pk=instance.pk)
        )

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.mqtt import PROTOCOL_ID
from pyscada.mqtt.models import MQTTBroker, ExtendedMQTTBroker
from pyscada.mqtt.models import MQTTVariable, ExtendedMQTTVariable
from pyscada.admin import DeviceAdmin
from pyscada.admin import CoreVariableAdmin
from pyscada.admin import admin_site
from pyscada.models import Device, DeviceProtocol
from django.contrib import admin
import logging

logger = logging.getLogger(__name__)


class MQTTBrokerAdminInline(admin.StackedInline):
    model = MQTTBroker


class MQTTBrokerAdmin(DeviceAdmin):
    list_display = DeviceAdmin.list_display + (
        "mqttbroker__ip_address",
        "mqttbroker__port",
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "protocol":
            kwargs["queryset"] = DeviceProtocol.objects.filter(pk=PROTOCOL_ID)
            db_field.default = PROTOCOL_ID
        return super(ModbusDeviceAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )

    def get_queryset(self, request):
        """Limit Pages to those that belong to the request's user."""
        qs = super(MQTTBRockerAdmin, self).get_queryset(request)
        return qs.filter(protocol_id=PROTOCOL_ID)

    inlines = [MQTTBrokerAdminInline]


class MQTTVariableAdminInline(admin.StackedInline):
    model = MQTTVariable


class MQTTVariableAdmin(CoreVariableAdmin):
    list_display = CoreVariableAdmin.list_display  # + ()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "device":
            kwargs["queryset"] = Device.objects.filter(protocol=PROTOCOL_ID)
        return super(ModbusVariableAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )

    def get_queryset(self, request):
        """Limit Pages to those that belong to the request's user."""
        qs = super(MQTTVariableAdmin, self).get_queryset(request)
        return qs.filter(device__protocol_id=PROTOCOL_ID)

    inlines = [MQTTVariableAdminInline]


# admin_site.register(ExtendedModbusDevice, ModbusDeviceAdmin)
# admin_site.register(ExtendedModbusVariable, ModbusVariableAdmin)

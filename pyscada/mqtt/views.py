# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import traceback

from django.conf import settings
from django.shortcuts import render
from django.http import Http404
from django.views.decorators.csrf import requires_csrf_token
from django.template.loader import get_template
from django.template.response import TemplateResponse

from pyscada.core import version as core_version

import logging

logger = logging.getLogger(__name__)

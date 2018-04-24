# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import json
import subprocess
import glob
import yaml
import time

from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.utils.safestring import mark_safe
from django.views.decorators.http import condition
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import HtmlFormatter
from subprocess import call

from django_sse.views import BaseSseView

def index(request):
    output_files = []

    os.chdir('/Users/matt/framework_output/')
    for item in glob.glob("*.json"):
        json_data = json.load(open(item))
        result = json_data["result"]
        output_files.append({
            "file_name": os.path.abspath(item),
            "result": result
        })

    template = loader.get_template('frontend/index.html')
    context = {
        "output_files": output_files
    }

    return HttpResponse(template.render(context, request))


def retrieve(request):
    if request.method == "POST":
        json_file_name = request.POST.get('json_file_name', None)
        json_data = json.load(open(json_file_name))

        json_data = json.dumps(json_data, sort_keys=True, indent=4)
        formatter = HtmlFormatter(style='colorful')
        response = highlight(json_data, JsonLexer(), formatter)
        style = "<style>" + formatter.get_style_defs() + "</style><br>"

        template = loader.get_template('frontend/retrieve.html')
        context = {
            "json_file_name": json_file_name,
            "json_data": mark_safe(style + response),
            "json_data_unformatted": json.loads(json_data)
        }

        return HttpResponse(template.render(context, request))


def run(request):
    template = loader.get_template('frontend/run.html')
    context = {}
    return HttpResponse(template.render(context, request))


def task(request):
    if request.method == "POST":
        task_directory_path = request.POST.get('task_directory_path', None)

        task_file_data = _read_file(task_directory_path, '/task.yml')
        targets_file_data = _read_file(task_directory_path, '/targets.yml')

        template = loader.get_template('frontend/task.html')
        context = {
            "task_directory_path": task_directory_path,
            "task_file_data": task_file_data,
            "targets_file_data": targets_file_data
        }
        return HttpResponse(template.render(context, request))


def _read_file(path, file_name):
    with open(path + file_name, 'r') as yaml_file:
        json_data = json.dumps(yaml.load(yaml_file), sort_keys=True, indent=4)
        formatter = HtmlFormatter(style='colorful')
        response = highlight(json_data, JsonLexer(), formatter)
        style = "<style>" + formatter.get_style_defs() + "</style><br>"
        return mark_safe(style + response)


def execute_task(request):
    if request.is_ajax():
        path = request.GET.get('path', '')
        task = subprocess.Popen('cd {}; mcli run'.format(path), stdout=subprocess.PIPE, shell=True)
        return HttpResponse
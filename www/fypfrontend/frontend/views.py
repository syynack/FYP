# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import json
import subprocess
import glob
import yaml
import time
import signal

from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.utils.safestring import mark_safe
from django.views.decorators.http import condition
from pygments import highlight
from pygments.lexers import JsonLexer, PythonLexer
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

        unpretty_task = {}
        with open(task_directory_path + '/task.yml', 'r') as task_file:
            unpretty_task = yaml.load(task_file)

        module_data = []
        for module in unpretty_task["task"]:
            with open(task_directory_path + module + '.py', 'r') as module_file:
                temp_mod = {}
                temp_mod["module"] = module
                module_code = module_file.read()
                formatter = HtmlFormatter(style='colorful')
                response = highlight(module_code, PythonLexer(), formatter)
                style = "<style>" + formatter.get_style_defs() + "</style><br>"
                temp_mod["data"] = mark_safe(style + response)
                module_data.append(temp_mod)

        template = loader.get_template('frontend/task.html')
        context = {
            "task_directory_path": task_directory_path,
            "task_file_data": task_file_data,
            "targets_file_data": targets_file_data,
            "module_data": module_data
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
        current_path = os.path.dirname(os.path.abspath(__file__))

        open("{}/static/task_output.txt".format(current_path), 'w').close()
        task = subprocess.Popen('cd {}; unbuffer mcli run --web > {}/static/task_output.txt'.format(path, current_path), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        return HttpResponse()


def kill_task(request):
    if request.is_ajax():
        for line in os.popen("ps ax | grep " + "mcli" + " | grep -v grep"):
            fields = line.split()
            pid = fields[0]
            os.kill(int(pid), signal.SIGKILL)

    return HttpResponse()
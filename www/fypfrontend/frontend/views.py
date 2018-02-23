# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os
import glob

from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import HtmlFormatter

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

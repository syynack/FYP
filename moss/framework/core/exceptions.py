#!/usr/bin/env python

class Error(Exception):
    pass


class ModuleResultError(Error):
    pass


class RegisteredModuleError(Error):
    pass

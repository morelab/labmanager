# -*-*- encoding: utf-8 -*-*-
# 
# gateway4labs is free software: you can redistribute it and/or modify
# it under the terms of the BSD 2-Clause License
# gateway4labs is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

import sys
import threading

from .base import register_blueprint, BaseRLMS, BaseFormCreator, Capabilities, Versions
from .caches import GlobalCache, VersionCache, get_cached_session

assert BaseFormCreator or register_blueprint or Versions or Capabilities or BaseRLMS or True # Avoid pyflakes warnings

# 
# Add the proper managers by pointing to a module
# 

_RLMSs = {
    # "RLMS type" :  <module>, 

    # e.g.
    # "WebLab-Deusto" : ( labmanager.rlms.ext.weblabdeusto, ['4.0'] ),
}

class Laboratory(object):
    def __init__(self, name, laboratory_id, description = None, autoload = False):
        self.name          = name
        self.laboratory_id = laboratory_id
        self.description   = description
        self.autoload      = autoload

    def __repr__(self):
        return "Laboratory(%r, %r, %r, %r)" % (self.name, self.laboratory_id, self.description, self.autoload)

    def __hash__(self):
        return hash(self.laboratory_id)

class RegistrationRecord(object):
    def __init__(self, name, versions):
        global_key = '%s - %s' % (name, ', '.join(versions))
        self.cache = GlobalCache(global_key)
        self.per_version_cache = {}
        for version in versions:
            # If a single version it's supported, the global cache is the same as the per version cache
            version_key = '%s - %s' % (name, version)
            self.per_version_cache[version] = VersionCache(version_key)
        
        self.per_thread = threading.local()

    def get_cache(self, version = None):
        if version is None:
            return self.cache
        else:
            return self.version_cache[version]

    @property
    def cached_session(self):
        cached_session = getattr(self.per_thread, 'cached_session', None)
        if cached_session:
            return cached_session

        cached_session = get_cached_session()
        self.per_thread.cached_session = cached_session
        return cached_session

def register(name, versions, module_name):
    _RLMSs[name] = (module_name, versions)
    return RegistrationRecord(name, versions)

def get_supported_types():
    return _RLMSs.keys()
        
def get_supported_versions(rlms_type):
    if rlms_type in _RLMSs:
        _, versions = _RLMSs[rlms_type]
        return versions
    return []

def is_supported(rlms_type, rlms_version):
    _, versions = _RLMSs.get(rlms_type, (None, []))
    return rlms_version in versions

def _get_module(rlms_type, rlms_version):
    module_name, versions = _RLMSs.get(rlms_type, (None, []))
    if rlms_version in versions:
        if hasattr(sys.modules[module_name], 'get_module'):
            return sys.modules[module_name].get_module(rlms_version)
        else:
            return sys.modules[module_name]
    else:
        raise Exception(u"Misconfiguration: %(rlmstype)s %(rmlsversion)s does not exist" % dict(rlmstype = rlms_type, rmlsversion = rlms_version))

def _get_form_creator(rlms_type, rlms_version):
    return _get_module(rlms_type, rlms_version).FORM_CREATOR

def get_form_class(rlms_type, rlms_version):
    form_creator = _get_form_creator(rlms_type, rlms_version)
    return form_creator.get_add_form()

def get_permissions_form_class(rlms_type, rlms_version):
    form_creator = _get_form_creator(rlms_type, rlms_version)
    return form_creator.get_permission_form()

def get_lms_permissions_form_class(rlms_type, rlms_version):
    form_creator = _get_form_creator(rlms_type, rlms_version)
    return form_creator.get_lms_permission_form()

def get_manager_class(rlms_type, rlms_version):
    module = _get_module(rlms_type, rlms_version)
    return module.RLMS

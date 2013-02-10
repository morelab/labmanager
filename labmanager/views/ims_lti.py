# -*-*- encoding: utf-8 -*-*-
#
# lms4labs is free software: you can redistribute it and/or modify
# it under the terms of the BSD 2-Clause License
# lms4labs is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

"""
  :copyright: 2012 Sergio Botero
  :license: BSD, see LICENSE for more details
"""

from sets import Set
from yaml import load as yload

from flask import render_template, request, redirect

from labmanager.models import LMS, Credential, RLMS, Permission, Course, PermissionOnLaboratory

from labmanager.ims_lti import lti_blueprint as lti
from labmanager.rlms import get_manager_class

config = yload(open('labmanager/config.yaml'))

@lti.route('/admin/request_permission/', methods = ['POST'])
def permission_request():
    data = {}
    choice_data = []

    for labs in request.form.getlist('rlmslaboratories'):
        split_choice = labs.split(':')
        rlms_id, exp_id = int(split_choice[0]), int(split_choice[1])
        choice_data.append((rlms_id, exp_id))

    lms_id = int(request.form['lms_id'])
    context_id = request.form['context_id']
    context_label = request.form['context_label']
    incoming_lms = LMS.find(lms_id)

    local_context = Course.find_or_create(lms = incoming_lms,
                                             context = context_id,
                                             name = context_label)

    if 'rlmslaboratories' in request.form:
        for rlms_id, exp_id in choice_data:
            # TODO: pass this to the Laboratory
            experiment = Experiment.find_with_id_and_rlms_id(exp_id, rlms_id)
            Permission.find_or_create(lms = incoming_lms, experiment = experiment,
                                      context = local_context)

    exp_status = Permission.find_all_with_lms_and_context(lms = incoming_lms, context = local_context)
    data['context_laboratories'] = exp_status

    return render_template('lti/experiments.html', info=data)


@lti.route("/", methods = ['POST'])
def start_ims():
    response = None

    consumer_key = request.form['oauth_consumer_key']
    auth = Credential.find_by_key(consumer_key)

    current_role = Set(request.form['roles'].split(','))
    req_course_data = request.form['lis_result_sourcedid']

    data = { 'user_agent' : request.user_agent,
             'origin_ip' : request.remote_addr,
             'lms' : auth.lms.name,
             'lms_id' : auth.lms.id,
             'context_label' : request.form['context_label'],
             'context_id' : request.form['context_id'],
             'access' : False
             }

    local_context = Course.find_or_create(lms = auth.lms,
                                          context = data['context_id'],
                                          name = data['context_label'])

    context_laboratories = Permission.find_all_for_context(local_context)
    if context_laboratories:
        data['context_laboratories'] = context_laboratories

    if ('Instructor' in current_role):
        data['role'] = 'Instructor'
        data['rlms'] = {}
        data['rlms_ids'] = {}

        lms_laboratories = PermissionOnLaboratory.find_all_for_lms(auth.lms)

        for allowed_lab in lms_laboratories:
            laboratory = allowed_lab.laboratory
            owner_rlms = laboratory.rlms
            if( owner_rlms.kind in data['rlms'] ):
                data['rlms'][owner_rlms.kind].append(laboratory)
            else:
                data['rlms'][owner_rlms.kind] = [laboratory]
                data['rlms_ids'][owner_rlms.kind] = owner_rlms.id

        if lms_laboratories:
            response = render_template('lti/administrator_tool_setup.html', info=data)
        else:
            response = render_template('lti/instructions.html', info=data)

    elif ('Learner' in current_role):
        data['role'] = 'Learner'

        if context_laboratories:
            wo_denied = []
            for exp in context_laboratories:
                if exp.access != 'denied':
                    wo_denied.append(exp)
            data['context_laboratories'] = wo_denied

            response = render_template('lti/experiments.html', info=data)
        else:
            response = render_template('lti/no_experiments_info.html', info=data)

    else:
        data['role'] = split_roles[0]
        response = render_template('lti/unknown_role.html', info=data)

    return response

@lti.route("/experiment/<experiment>", methods = ['GET'])
def launch_experiment(experiment=None):
    response = ""

    if (experiment):
        response = experiment

    else:
        response = "No soup for you!"

    return response

import json

from flasgger import swag_from
from flask_restful import Resource
from flask import request
from util.format import format
from util.dynamic_imp import check_module, dynamic_imp

import os
import logging

current_folder = os.path.dirname(os.path.dirname(__file__))

class AiProcessResource(Resource):
    @staticmethod
    @swag_from("../swagger/ai_process.yml")
    def post(process_name):
        body = json.loads(request.data)
        response = main(body, process_name)

        if (response['errorMessage'] == None):
            return format.success(data=response['result'])
        else: 
            return format.badRequest(data=response['result'], message=response['errorMessage'])
        

def main(body, process_name):
    input = body['input']
    processes = body['processes']
    process_name = process_name.replace('-','_')
    response = {}
    result = {
        'records': []
    }

    # dynamic load module and execute funtions sequentially
    try:
        # validate input
        check_process_route(process_name)
        check_processes_datatype(processes)
        validate_processes(process_name, processes)
        
        for process in processes:
            record = {
                'process': process,
                'result': None                 
            }
            result['records'].append(record)

            module_path = os.path.join(current_folder, 'functions', process_name,  process)
            myModule = dynamic_imp('handler', [module_path])
            func_result = myModule.handler.execute(input)
               
            logging.info('Process name: %s' % process)
            logging.info('Output:')
            logging.info(func_result)

            input = func_result
            result['records'][len(result['records']) - 1]['result']= 'OK'

            if process == processes[len(processes) - 1]:
                result['result'] = func_result

            response['result'] = result
            response['errorMessage'] = None
        return response
    except Exception as e:
        logging.error(e)
        response['result'] = result
        response['errorMessage'] = str(e)

        return response

def check_process_route(process_name):
    if not process_name in ['pre_process', 'post_process']:
        raise Exception('invalid route name. options: pre-process, post-process')

def check_processes_datatype(processes):
    if not isinstance(processes, list):
        raise Exception('processes must be an array')

def validate_processes(process_name, processes):
    invalid_processes = []
    for process in processes:
        module_path = os.path.join(current_folder, 'functions', process_name,  process)
        if not check_module('handler', [module_path,]):
            invalid_processes.append(process)

    if(len(invalid_processes) > 0):
        raise Exception('invalid process:  %s' % ', '.join(invalid_processes))
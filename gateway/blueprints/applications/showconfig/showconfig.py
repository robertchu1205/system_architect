from flask import Blueprint, current_app, jsonify
import sys, json, yaml

# Blueprint Configuration
showconfig_bp = Blueprint('showconfig_bp', __name__, 
                        static_url_path='showconfig')

@showconfig_bp.route('', methods=['GET'])
def show_config():
    # global vars from config or yaml, yaml first
    try:
        with open('/config/config.yaml', 'r') as stream: 
            try:
                config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                try:
                    with open('/config/config.json', 'r') as f: 
                        config = json.load(f)
                except Exception as e:
                    sys.exit(f'config.json defined above does not exist. Except: {e}')
    except Exception as e:
        try:
            with open('/config/config.json', 'r') as f: 
                config = json.load(f)
        except Exception as e:
            sys.exit(f'config.json defined above does not exist. Except: {e}')

    # check config content 
    try:
        x = config['env_setting']['project_code']
        if config['env_setting']['project_code'] == '' or config['env_setting']['project_code'] == None:
            return jsonify({'config error': 'project_code should be defined for log'})
    except:
        return jsonify({'config error': 'project_code should be defined for log'})
    try:
        x = config['env_setting']['tfs_method']
        if (config['env_setting']['tfs_method'] != 'rest') and (config['env_setting']['tfs_method'] != 'grpc'):
            return jsonify({'config error': 'tfs_method unsupported'})
    except:
        return jsonify({'config error': 'tfs_method unsupported'})
    try:
        x = config['env_setting']['image_format']
        if (config['env_setting']['image_format'] != 'array') and (config['env_setting']['image_format'] != 'b64'):
            return jsonify({'config error': 'image_format unsupported'})
    except:
        return jsonify({'config error': 'image_format unsupported'})
    try:
        x = config['env_setting']['signature_name']
        if config['env_setting']['signature_name'] == '' or config['env_setting']['signature_name'] == None:
            return jsonify({'config error': 'signature_name should be defined for tfserving'})
    except:
        return jsonify({'config error': 'signature_name should be defined for tfserving'})
    try:
        x = config['env_setting']['model_input_name']
        y = config['env_setting']['model_output_name']
        if (type(config['env_setting']['model_input_name']) != list) or (type(config['env_setting']['model_output_name']) != list):
            return jsonify({'config error': 'model_input_name and model_output_name have to be list'})
    except:
        return jsonify({'config error': 'model_input_name and model_output_name have to be list'})
    try:
        x = str(config['env_setting']['request_post_file'])
        if (str(config['env_setting']['request_post_file']) != 'True') and (str(config['env_setting']['request_post_file']) != 'False'):
            return jsonify({'config error': 'request_post_file has to be True or False in String or Boolean format'})
    except:
        return jsonify({'config error': 'request_post_file has to be True or False in String or Boolean format'})
    try:
        x = str(config['env_setting']['check_checkpoint'])
        if (str(config['env_setting']['check_checkpoint']) != 'True') and (str(config['env_setting']['check_checkpoint']) != 'False'):
            return jsonify({'config error': 'check_checkpoint has to be True or False in String or Boolean format'})
    except:
        return jsonify({'config error': 'check_checkpoint has to be True or False in String or Boolean format'})
    try:
        x = str(config['env_setting']['image_saving'])
        if str(config['env_setting']['image_saving']) == '' or str(config['env_setting']['image_saving']) == None:
            return jsonify({'config error': 'image_saving should be defined'})
    except:
        return jsonify({'config error': 'image_saving should be defined'})
    # assert (type(config['env_setting']['comps_to_match_m1_color']) == list) and (type(config['env_setting']['comps_to_match_m1']) == list), \
    # 'comps_to_match_m1_color and comps_to_match_m1 have to be list'

    # check specific config which maybe would affect gateway
    if config['env_setting']['image_format'] == 'array':
        try:
            x = int(config['env_setting']['image_input_height'])
            y = int(config['env_setting']['image_input_width']) 
            if int(config['env_setting']['image_input_height']) <= 0:
                return jsonify({'config error': 'image_input_height should be defined'})
            if int(config['env_setting']['image_input_width']) <= 0:
                return jsonify({'config error': 'image_input_width should be defined'})
        except:
            return jsonify({'config error': 'image_input_width & image_input_height should be defined'})
    if config['env_setting']['tfs_method'] == 'grpc':
        try:
            x = int(config['env_setting']['grpc_batch']) 
            if int(config['env_setting']['grpc_batch']) <= 1:
                return jsonify({'config error': 'grpc_batch should be defined and larger than 1'})
        except:
            return jsonify({'config error': 'grpc_batch should be defined and larger than 1'})
        try:
            x = config['env_setting']['tfserving_grpc']
            if len(config['env_setting']['tfserving_grpc'].split(':')) != 2:
                return jsonify({'config error': 'tfserving_grpc should be defined and url, port included'})
        except:
            return jsonify({'config error': 'tfserving_grpc should be defined and url, port included'})
    elif config['env_setting']['tfs_method'] == 'rest':
        try:
            x = config['env_setting']['tfserving_rest']
            if len(config['env_setting']['tfserving_rest'].split(':')) != 2:
                return jsonify({'config error': 'tfserving_rest should be defined and url, port included'})
        except:
            return jsonify({'config error': 'tfserving_rest should be defined and url, port included'})
    if str(config['env_setting']['image_saving']) != 'False':
        try: 
            x = config['env_setting']['image_saving_ext']
            if config['env_setting']['image_saving_ext'] == '' or config['env_setting']['image_saving_ext'] == None:
                return jsonify({'config error': 'image_saving should be defined'})
        except:
            return jsonify({'config error': 'image_saving should be defined'})

    # try & catch check
    try:
        test = config['env_setting']['extra_infos_to_return']
        if type(test) != list:
            return jsonify({'config error': 'extra_infos_to_return has to be list'})
    except KeyError:
        current_app.logger.info('extra_infos_to_return is not defined')
    try:
        test = config['env_setting']['login_token']
        if test == '' or test == None:
            return jsonify({'config error': 'login_token is empty'})
    except KeyError:
        current_app.logger.info('login_token is not defined')
    try:
        test = config['env_setting']['register_token']
        if test == '' or test == None:
            return jsonify({'config error': 'register_token is empty'})
    except KeyError:
        current_app.logger.info('register_token is not defined')

    # process_api
    try:
        test = config['env_setting']['process_api']
        try:
            x = test['protocol']
            if (test['protocol'] != 'rest') and (test['protocol'] != 'grpc'):
                return jsonify({'config error': 'protocol in process_api has to be rest or grpc'})
        except:
            return jsonify({'config error': 'protocol in process_api has to be rest or grpc'})
        if test['protocol'] == 'grpc':
            try:
                x = test['grpc_url']
                if len(test['grpc_url'].split(':')) != 2:
                    return jsonify({'config error': 'grpc_url in process_api should be defined and url, port included'})
            except:
                return jsonify({'config error': 'grpc_url in process_api should be defined and url, port included'})
        elif test['protocol'] == 'rest':
            try:
                x = test['rest_url']
                if len(test['rest_url'].split(':')) != 2: 
                    return jsonify({'config error': 'rest_url in process_api should be defined and url, port included'})
            except:
                return jsonify({'config error': 'rest_url in process_api should be defined and url, port included'})
        try:
            x = test['pre_process']
            y = test['post_process']
            if (type(test['pre_process']) != list) or (type(test['post_process']) != list):
                return jsonify({'config error': 'pre_process and post_process in process_api have to be list'})
        except:
            return jsonify({'config error': 'pre_process and post_process in process_api have to be list'})
    except KeyError:
        current_app.logger.info('process_api is not applied')

    # model_setting
    for comps in list(dict(config['model_setting']).keys()):
        try:
            x = config['model_setting'][comps]['model_name']
            if type(config['model_setting'][comps]['model_name']) != list:
                return jsonify({'config error': f'model_name of {comps} has to be list'})
        except:
            return jsonify({'config error': f'model_name of {comps} has to be list'})
        model_count = len(config['model_setting'][comps]['model_name'])
        try:
            specific_url = config['model_setting'][comps]['specific_url']
            if (type(specific_url) != list) and (specific_url != '') and (specific_url != None):
                return jsonify({'config error': f'specific_url of {comps} has to be list'})
            if type(specific_url) == list:
                if len(specific_url) != model_count:
                    return jsonify({'config error': f'specific_url of {comps} has to be the same length as model_name'})
        except KeyError:
            current_app.logger.info(f'specific_url of {comps} is not applied')
        try:
            version_label = config['model_setting'][comps]['version_label']
            if (type(version_label) != list) and (version_label != '') and (version_label != None): 
                return jsonify({'config error': f'version_label of {comps} has to be list'})
            if type(version_label) == list:
                if len(version_label) != model_count:
                    return jsonify({'config error': f'version_label of {comps} has to be the same length as model_name'})
        except KeyError:
            current_app.logger.info(f'version_label of {comps} is not applied')
        try:
            con_threshold = config['model_setting'][comps]['con_threshold']
            if (type(con_threshold) != list) and (con_threshold != '') and (con_threshold != None):
                return jsonify({'config error': f'con_threshold of {comps} has to be list'})
            if type(con_threshold) == list:
                if len(con_threshold) != model_count:
                    return jsonify({'config error': f'con_threshold of {comps} has to be the same length as model_name'})
        except KeyError:
            current_app.logger.info(f'con_threshold of {comps} is not applied')
        try:
            data_type = config['model_setting'][comps]['data_type']
            if (type(data_type) != list) and (data_type != '') and (data_type != None):
                return jsonify({'config error': f'data_type of {comps} has to be list'})
            if type(data_type) == list:
                if len(data_type) != model_count:
                    return jsonify({'config error': f'data_type of {comps} has to be the same length as model_name'})
        except KeyError:
            current_app.logger.info(f'data_type of {comps} is not applied')
    
    # update current_app.config as in wsgi.py
    current_app.config.update(config)
    try:
        config_dict = {
            'env_setting': current_app.config['env_setting'], 
            'model_setting': current_app.config['model_setting'],
            'test_model_setting': current_app.config['test_model_setting'],
        }
    except:
        config_dict = {
            'env_setting': current_app.config['env_setting'], 
            'model_setting': current_app.config['model_setting'],
        }   
    return jsonify(config_dict)
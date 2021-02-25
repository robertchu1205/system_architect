import logging, json, sys, prometheus_client, yaml
from applications import create_app
from flask import Flask, g
from applications.prometheus import init_prometheus_client
# from prometheus_client import multiprocess

print('=== log in wsgi ===')
# global vars from config or yaml, yaml first
try:
    with open('/config/config.yaml', 'r') as stream: 
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(f'config.yaml yaml.YAMLError. Except: {exc}')
            try:
                with open('/config/config.json', 'r') as f: 
                    config = json.load(f)
            except Exception as e:
                sys.exit(f'config.json defined above does not exist. Except: {e}')
except Exception as e:
    print(f'config.yaml defined above does not exist. Except: {e}')
    try:
        with open('/config/config.json', 'r') as f: 
            config = json.load(f)
    except Exception as e:
        sys.exit(f'config.json defined above does not exist. Except: {e}')

# prometheus REGISTRY
try:
    REGISTRY = prometheus_client.CollectorRegistry(auto_describe=False)
    # multiprocess.MultiProcessCollector(REGISTRY)
    prome_dict = init_prometheus_client(REGISTRY)
    # prometheus_client.generate_latest(REGISTRY)
except Exception as e:
    sys.exit(f'REGISTRY for prometheus failed. Except: {e}')

app = create_app()
app.config.from_pyfile('config.py')

# check config content 
assert config['env_setting']['project_code'] != '' and config['env_setting']['project_code'] != None, 'project_code should be defined for log'
assert (config['env_setting']['tfs_method'] == 'rest') or (config['env_setting']['tfs_method'] == 'grpc'), 'tfs_method unsupported'
assert (config['env_setting']['image_format'] == 'array') or (config['env_setting']['image_format'] == 'b64'), 'image_format unsupported'
assert config['env_setting']['signature_name'] != '' and config['env_setting']['signature_name'] != None, 'signature_name should be defined for tfserving'
assert (type(config['env_setting']['model_input_name']) == list) and (type(config['env_setting']['model_output_name']) == list), \
    'model_input_name and model_output_name have to be list'
assert (str(config['env_setting']['request_post_file']) == 'True') or (str(config['env_setting']['request_post_file']) == 'False'), \
    'request_post_file has to be True or False in String or Boolean format'
assert (str(config['env_setting']['check_checkpoint']) == 'True') or (str(config['env_setting']['check_checkpoint']) == 'False'), \
    'check_checkpoint has to be True or False in String or Boolean format'
assert str(config['env_setting']['image_saving']) != '' and str(config['env_setting']['image_saving']) != None, 'image_saving should be defined'
# assert (type(config['env_setting']['comps_to_match_m1_color']) == list) and (type(config['env_setting']['comps_to_match_m1']) == list), \
# 'comps_to_match_m1_color and comps_to_match_m1 have to be list'

# check specific config which maybe would affect gateway
if config['env_setting']['image_format'] == 'array':
    assert int(config['env_setting']['image_input_height']) > 0, 'image_input_height should be defined'
    assert int(config['env_setting']['image_input_width']) > 0, 'image_input_width should be defined'
if config['env_setting']['tfs_method'] == 'grpc':
    assert int(config['env_setting']['grpc_batch']) > 1, 'grpc_batch should be defined and larger than 1'
    assert len(config['env_setting']['tfserving_grpc'].split(':'))==2, 'tfserving_grpc should be defined and url, port included'
elif config['env_setting']['tfs_method'] == 'rest':
    assert len(config['env_setting']['tfserving_rest'].split(':'))==2, 'tfserving_rest should be defined and url, port included'
if str(config['env_setting']['image_saving']) != 'False':
    assert config['env_setting']['image_saving_ext'] != '' and config['env_setting']['image_saving_ext'] != None, 'image_saving should be defined'

# try & catch check
try:
    test = config['env_setting']['extra_infos_to_return']
    assert type(test) == list, 'extra_infos_to_return has to be list'
except KeyError:
    print('extra_infos_to_return is not defined')
try:
    test = config['env_setting']['login_token']
    assert test != '' and test != None, 'login_token is empty'
except KeyError:
    print('login_token is not defined')
try:
    test = config['env_setting']['register_token']
    assert test != '' and test != None, 'register_token is empty'
except KeyError:
    print('register_token is not defined')

# process_api
try:
    test = config['env_setting']['process_api']
    assert (test['protocol'] == 'rest') or (test['protocol'] == 'grpc'), 'protocol in process_api has to be rest or grpc'
    if test['protocol'] == 'grpc':
        assert len(test['grpc_url'].split(':'))==2, 'grpc_url in process_api should be defined and url, port included'
    elif test['protocol'] == 'rest':
        assert len(test['rest_url'].split(':'))==2, 'rest_url in process_api should be defined and url, port included'
    assert (type(test['pre_process']) == list) and (type(test['post_process']) == list), \
        'pre_process and post_process in process_api have to be list'
except KeyError:
    print('process_api is not applied')

# model_setting
for comps in list(dict(config['model_setting']).keys()):
    assert (type(config['model_setting'][comps]['model_name']) == list), f'model_name of {comps} has to be list'
    model_count = len(config['model_setting'][comps]['model_name'])
    try:
        specific_url = config['model_setting'][comps]['specific_url']
        assert (type(specific_url) == list) or (specific_url == '') or (specific_url == None), f'specific_url of {comps} has to be list'
        if type(specific_url) == list:
            assert len(specific_url) == model_count, f'specific_url of {comps} has to be the same length as model_name'
    except KeyError:
        print(f'specific_url of {comps} is not applied')
    try:
        version_label = config['model_setting'][comps]['version_label']
        assert (type(version_label) == list) or (version_label == '') or (version_label == None), f'version_label of {comps} has to be list'
        if type(version_label) == list:
            assert len(version_label) == model_count, f'version_label of {comps} has to be the same length as model_name'
    except KeyError:
        print(f'version_label of {comps} is not applied')
    try:
        con_threshold = config['model_setting'][comps]['con_threshold']
        assert (type(con_threshold) == list) or (con_threshold == '') or (con_threshold == None), f'con_threshold of {comps} has to be list'
        if type(con_threshold) == list:
            assert len(con_threshold) == model_count, f'con_threshold of {comps} has to be the same length as model_name'
    except KeyError:
        print(f'con_threshold of {comps} is not applied')
    try:
        data_type = config['model_setting'][comps]['data_type']
        assert (type(data_type) == list) or (data_type == '') or (data_type == None), f'data_type of {comps} has to be list'
        if type(data_type) == list:
            assert len(data_type) == model_count, f'data_type of {comps} has to be the same length as model_name'
    except KeyError:
        print(f'data_type of {comps} is not applied')

print('=====================')
app.config.update(config)
# app.config.update(prome_dict)

@app.before_request
def before_request():
    if not hasattr(g,'REGISTRY'):
        setattr(g,'REGISTRY', REGISTRY)
    if not hasattr(g,'prome_dict'):
        setattr(g,'prome_dict', prome_dict)
    for comp in config['model_setting']:
        for mn in config['model_setting'][comp]['model_name']:
            g.prome_dict['outline_img_counter'].labels(mn).inc(0)

if __name__ == '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
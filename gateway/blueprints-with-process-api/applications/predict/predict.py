import time, datetime, json, threading, multiprocessing, grpc, requests, base64
from flask import Blueprint, current_app, jsonify, abort, request
# from applications.functions import request_to_data, to_request_json, to_response_json
from applications.functions import print_logger_json, iterdict
from applications.prometheus import read_checkpoint, check_checkpoint, prometheus_data
from applications.gateway import predict_and_saveimages
# import applications.parse_request as parse_request
import applications.ai_process_pb2 as ai_process_pb2
import applications.ai_process_pb2_grpc as ai_process_pb2_grpc
# import concurrent.futures

# Blueprint Configuration
predict_bp = Blueprint('predict_bp', __name__, 
                        static_url_path='predict')

def pool_map(function_name, argument, processes = multiprocessing.cpu_count()):
    return multiprocessing.Pool(processes).map(function_name, argument)

@predict_bp.route('', methods=['POST'])
def receive_info():
    # t = threading.Thread(target = predict_and_saveimages, args = (data,))
    # t.start()
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     future = executor.submit(predict_and_saveimages, data)
    #     (softmax_ary, instances) = future.result()
    except_data = {'predictions': ''}
    request_time = time.time()
    try:
        input = {
            # "request": request.json,
            # "config": current_app.config,
            "env_setting": iterdict(current_app.config['env_setting']),
            "model_setting": current_app.config['model_setting'],
            # "online_models": list(dict(current_app.config['model_setting']).keys()),
        }
        if input['env_setting']['request_post_file'] == 'True':
            input['form_dict'] = request.form.to_dict(flat=False) # key: img_name, img_info
            input['post_file_dict'] = {}
            for img in request.files.getlist('img_file'):
                input['post_file_dict'].update({img.filename: base64.b64encode(img.read()).decode("utf-8")})
            default_ans = [{'confidence': -2.0, 'pred_class': 'NG'} for i in request.files.getlist('img_file')]
        elif input['env_setting']['request_post_file'] == 'False':
            input['request'] = request.json
            default_ans = [{'confidence': -2.0, 'pred_class': 'NG'} for i in input['request']['instances']]
        else:
            current_app.logger.error('request_post_file of env_setting unsupported')
            print_logger_json('error', 'request_post_file of env_setting unsupported')
            return jsonify(except_data)
        except_data = {'predictions': default_ans}
        input = json.dumps(input)
        # communiate with process api
        process_api_var = current_app.config['env_setting']['process_api']
        if process_api_var['protocol']=='rest':
            process_address = f"http://{process_api_var['rest_url']}/v1/oneai/pre-process"
            processes = json.dumps(process_api_var['pre_process'])
            datas = f'"input": {input}, "processes": {processes}'
            datas = "{" + datas + "}"
            response = requests.post(process_address, data=datas)
            if not response.status_code in [200, 201]:
                current_app.logger.error(f'pre-process status_code: {response.status_code}, msg: {response.reason}')
                print_logger_json('error', f'pre-process status_code: {response.status_code}, msg: {response.reason}')
                return jsonify(except_data)
            else:    
                response = json.loads(response.text)
                result = {
                    "error": response['error'],
                    "data": response['data'],
                    "message": response['message']
                }  
        elif process_api_var['protocol']=='grpc':
            MAX_MESSAGE_LENGTH = 1000 * 1024 * 1024 # 1G
            options = [
                ('grpc.max_message_length', MAX_MESSAGE_LENGTH), 
                ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
                ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH),
            ]
            with grpc.insecure_channel(process_api_var['grpc_url'], options = options) as channel:
                stub = ai_process_pb2_grpc.AIProcessStub(channel)
                response = stub.PreProcess(ai_process_pb2.ProcessRequest(input=input, processes=process_api_var['pre_process']))
            result = {
                'error': response.error,
                'data': json.loads(response.data),
                'message': response.message
            }
        else:
            current_app.logger.error('protocol of process_api in env_setting not supported')
            print_logger_json('error', 'protocol of process_api in env_setting not supported')
            return jsonify(except_data)
        # data = parse_request.execute(input)
        if result['error'] == True:
            current_app.logger.error(result['message'])
            print_logger_json('error', f"""communicate with pre_process error: {result['message']}""")
            return jsonify(except_data)
        else:
            data = result['data']['result']
            if 'error' in data:
                current_app.logger.error(data['error'])
                print_logger_json('error', f"""parse_request.py error: {data['error']}""")
                return jsonify(except_data)
            else:
                if (data['env_setting']['image_format'] == 'b64') and (data['env_setting']['tfs_method'] == 'grpc'):
                    for r in data['request']:
                        r['image'] = r['image'].encode('latin-1')
                if current_app.config['env_setting']['check_checkpoint']=='True' or current_app.config['env_setting']['check_checkpoint']==True:
                    try:
                        checkpoint_dict = read_checkpoint()
                        if type(checkpoint_dict) == str:
                            current_app.logger.error(checkpoint_dict)
                            print_logger_json('error', checkpoint_dict)
                        else:
                            check_checkpoint(checkpoint_dict, data['request'])
                    except:
                        current_app.logger.error(f'checkpoints judging errors.')
                        print_logger_json('error', f'checkpoints judging errors.')
                for dr in data['request']:
                    dr['client_ip'] = request.remote_addr
                (data['request'], instances) = predict_and_saveimages(data['request'])
    except Exception as e:
        current_app.logger.error(f'''pre-process: {str(current_app.config['env_setting']['process_api']['pre_process'])} failed, msg: {e}''')
        print_logger_json('error', f'''pre-process: {str(current_app.config['env_setting']['process_api']['pre_process'])} failed, msg: {e}''')
        return jsonify(except_data)
    # t.join()
    # concurrent.futures.wait(fs, timeout=None, return_when=ALL_COMPLETED)
    req_secs_taken = time.time() - request_time
    res_time = str(datetime.datetime.now())
    try:
        for idx, d in enumerate(data['request']):
            data['res_time'] = res_time
            data['req_secs_taken'] = str(req_secs_taken)
            response_json = json.dumps(d)
            print(response_json, flush=True)
    except:
        current_app.logger.error(f'response_json log error')
        print_logger_json('error', f'response_json log error')
    try:
        prome_data = prometheus_data(req_secs_taken, data['request'])
        if prome_data != True:
            current_app.logger.error(prome_data)
            print_logger_json('error', prome_data)
    except:
        current_app.logger.error(f'prometheus_data error')
        print_logger_json('error', f'prometheus_data error')
    if instances == '':
        return jsonify(except_data)
    else:
        payload = {'predictions': instances}
        return jsonify(payload)
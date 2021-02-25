# from applications.component import Merge
from flask import current_app, g
from applications.functions import print_logger_json, iterdict
import json, grpc, requests
import applications.ai_process_pb2 as ai_process_pb2
import applications.ai_process_pb2_grpc as ai_process_pb2_grpc

def If_None_Exist(pred_softmax, msn):
    check_if_None_exists = True
    for key, value in pred_softmax.items():
        if value == [None] and key in msn:
            check_if_None_exists = key
    return check_if_None_exists
    
def main(comp, pred_softmax, own_model_setting, this_infos):
    ori_msn = current_app.config['model_setting'][comp]['model_name'] 
    ori_dt = current_app.config['model_setting'][comp]['data_type'] 
    try:
        if (current_app.config['model_setting'][comp]['con_threshold']==[]) or (current_app.config['model_setting'][comp]['con_threshold']==None):
            con_threshold = ['None' for c in ori_msn]
        else:
            con_threshold = current_app.config['model_setting'][comp]['con_threshold']
    except:
        con_threshold = ['None' for c in ori_msn]
    if If_None_Exist(pred_softmax, ori_msn) != True:
        return {'con':-2.0,'pred':'NG','ng_parts':f'{comp}-{If_None_Exist(pred_softmax, ori_msn)}-tfs-error'}
    check_if_append = False
    # check outcome choice 
    # assert (outcome_choice == 'consider') or (outcome_choice == 'background') or (outcome_choice == 'exclusion'), \
    #     'ownmodel["outcome_choice"] is not consider or background or exclusion in config.json'
    if own_model_setting != {}:
        append_msn = ori_msn
        append_dt = ori_dt
        append_ct = con_threshold
        for oms_comps in list(dict(own_model_setting['model_setting']).keys()):
            for oc in oms_comps.split('/'):
                if oc == comp:
                    check_if_append = True
                    append_msn = append_msn + \
                        own_model_setting['model_setting'][oms_comps]['model_name']
                    if len(current_app.config['env_setting']['model_output_name']) == 1:
                        append_dt = append_dt + \
                            own_model_setting['model_setting'][oms_comps]['data_type']
                    try:
                        if (own_model_setting['model_setting'][oms_comps]['con_threshold']==[]) or (own_model_setting['model_setting'][oms_comps]['con_threshold']==None):
                            append_ct = append_ct + \
                                ['None' for c in own_model_setting['model_setting'][oms_comps]['model_name']]
                        else:
                            append_ct = append_ct + \
                                own_model_setting['model_setting'][oms_comps]['con_threshold']
                    except:
                        append_ct = append_ct + \
                            ['None' for c in own_model_setting['model_setting'][oms_comps]['model_name']]
    try:
        outcome_choice = current_app.config['test_model_setting']['outcome_choice']
    except:
        outcome_choice = None
    # communiate with process api
    try:
        if check_if_append == True:
            input = {
                "comp": comp,
                "con_threshold": append_ct,
                "pred_softmax": pred_softmax,
                "append_msn": append_msn,
                "ori_dt": append_dt,
                "this_infos": this_infos,
                "outcome_choice": outcome_choice,
                "env_setting": iterdict(current_app.config['env_setting']),
                # "model_setting": iterdict(current_app.config['model_setting']),
                "model_setting": current_app.config['model_setting'],
                "ori_msn": ori_msn,
            }
        else:
            input = {
                "comp": comp,
                "con_threshold": con_threshold,
                "pred_softmax": pred_softmax,
                "append_msn": ori_msn,
                "ori_dt": ori_dt,
                "this_infos": this_infos,
                "outcome_choice": outcome_choice,
                "env_setting": iterdict(current_app.config['env_setting']),
                # "model_setting": iterdict(current_app.config['model_setting']),
                "model_setting": current_app.config['model_setting'],
            }
        input = json.dumps(input)
        process_api_var = current_app.config['env_setting']['process_api']
        if process_api_var['protocol']=='rest':
            process_address = f"http://{process_api_var['rest_url']}/v1/oneai/post-process"
            processes = json.dumps(process_api_var['post_process'])
            datas = f'"input": {input}, "processes": {processes}'
            datas = "{" + datas + "}"
            response = requests.post(process_address, data=datas)
            if not response.status_code in [200, 201]:
                current_app.logger.error(f'post_process status_code: {response.status_code}, msg: {response.reason}')
                print_logger_json('error', f'post_process status_code: {response.status_code}, msg: {response.reason}')
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
                response = stub.PostProcess(ai_process_pb2.ProcessRequest(input=input, processes=process_api_var['post_process']))
            result = {
                'error': response.error,
                'data': json.loads(response.data),
                'message': response.message
            }
        else:
            current_app.logger.error('protocol of process_api in env_setting not supported')
            print_logger_json('error', 'protocol of process_api in env_setting not supported')
        if result['error'] == True:
            current_app.logger.error(result['message'])
            print_logger_json('error', f"""communicate with post_process error: {result['message']}""")
        else:
            for er in result['data']['result']['error_msg']:
                current_app.logger.error(er)
                print_logger_json('error', er)
            for k, value in result['data']['result']['prome_dict'].items():
                for v in value:
                    g.prome_dict[v[0]].labels(k, v[1]).inc(v[2])
            return result['data']['result']['output_dict']
    except Exception as e:
        current_app.logger.error(f'''post-process: {str(current_app.config['env_setting']['process_api']['post_process'])} failed, msg: {e}''')
        print_logger_json('error', f'''post-process: {str(current_app.config['env_setting']['process_api']['post_process'])} failed, msg: {e}''')
    # if check_if_append == True:
    #     return Merge(comp, append_ct, pred_softmax, append_msn, append_dt, this_infos, ori_msn)
    # elif (check_if_append == False) or (own_model_setting=={}):
    #     return Merge(comp, con_threshold, pred_softmax, ori_msn, ori_dt, this_infos)
    # else:
    #     return Merge(comp, con_threshold, pred_softmax, ori_msn, ori_dt, this_infos)
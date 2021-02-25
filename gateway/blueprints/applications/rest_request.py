import base64, time, json, requests, prometheus_client, types
import applications.classify as classify
from flask import current_app, g
from applications.functions import calculate_secs_taken, print_logger_json

def query_serving_with_version_label(vl, url_to_query, msn, data):
    try: 
        model_version = int(vl)
        url = f'''http://{url_to_query}/v1/models/{msn}/versions/{vl}:predict'''
    except:
        url = f'''http://{url_to_query}/v1/models/{msn}/labels/{vl}:predict'''
    ini_time = time.time()
    response = requests.post(url, data=data, timeout=time_out)
    if response.status_code in [200, 201]:
        g.prome_dict['predicts_duration_secs'].labels(
                msn).inc(calculate_secs_taken(ini_time))
        return response.json()['predictions']
    else:
        url = f'''http://{url_to_query}/v1/models/{msn}:predict'''
        response = requests.post(url, data=data, timeout=time_out)
        if response.status_code in [200, 201]:
            g.prome_dict['predicts_duration_secs'].labels(
                    msn).inc(calculate_secs_taken(ini_time))
            return response.json()['predictions']
        else:
            raise Exception((f'Error code: {response.status_code}, ' 
                            f'Content: {response.content}'))
            return None

def query_latest_available_serving(url_to_query, msn, data):
    ini_time = time.time()
    url = f'''http://{url_to_query}/v1/models/{msn}:predict'''
    response = requests.post(url, data=data, timeout=time_out)
    if response.status_code in [200, 201]:
        g.prome_dict['predicts_duration_secs'].labels(
                msn).inc(calculate_secs_taken(ini_time))
        return response.json()['predictions']
    else:
        raise Exception((f'Error code: {response.status_code}, ' 
                        f'Content: {response.content}'))
        return None

# def saiap_coding(img_resized):
#     image = base64.urlsafe_b64encode(img_resized)
#     return base64.b64encode(image).decode('utf-8')

# def own_coding(img_resized):
#     return base64.b64encode(img_resized).decode('utf-8')

def restful_request_server( 
    only_one_flag, component, img_resized, all_infos, if_test_model=True):
    if if_test_model:
        component_dict = model_setting[component]
        model_spec_name = component_dict['model_name'] 
        version_label = component_dict['version_label']
        model_input_name = env_setting['model_input_name']
        model_url = env_setting['tfserving_rest']
    else:
        component_dict = own_model_setting['model_setting'][component]
        model_spec_name = component_dict['model_name']
        version_label = component_dict['version_label']
        model_input_name = component_dict['model_input_name']
        model_url = own_model_setting['tfserving_rest']
    if only_one_flag is True:
        if (env_setting['image_format'] == 'b64') and len(model_input_name) == 1:
            instance = {model_input_name[0]: {'b64': img_resized},}
        elif (env_setting['image_format'] == 'b64') and len(model_input_name) > 1:
            for i, mi in enumerate(model_input_name):
                if i == 0:
                    instance = {mi: {'b64': img_resized},}
                else:
                    instance[mi] = all_infos[mi][0]
        elif (env_setting['image_format'] == 'array') and len(own_min) == 1:
            instance = [{model_input_name[0]: img_resized}]
        elif (env_setting['image_format'] == 'array') and len(model_input_name) > 1:
            for i, mi in enumerate(model_input_name):
                if i == 0:
                    instance = {mi: img_resized}
                else:
                    instance[mi] = all_infos[mi][0]
        else:
            return None
        instances = [instance]
    else:
        if (env_setting['image_format'] == 'b64') and len(model_input_name) == 1:
            instances = [{model_input_name[0]: {'b64': ir},} for ir in img_resized]
        elif (env_setting['image_format'] == 'b64') and len(model_input_name) > 1:
            instances = []
            for ir in img_resized:
                for i, mi in enumerate(model_input_name):
                    if i == 0:
                        instance = {mi: {'b64': ir},}
                    else:
                        instance[mi] = all_infos[mi][img_resized.index(ir)]
                instances.append(instance)
        elif (env_setting['image_format'] == 'array') and len(own_min) == 1:
            instances = [{model_input_name[0]: ir,} for ir in img_resized] 
        elif (env_setting['image_format'] == 'array') and len(model_input_name) > 1:
            instances = []
            for ir in img_resized:
                for i, mi in enumerate(model_input_name):
                    if i == 0:
                        instance = {mi: ir}
                    else:
                        instance[mi] = all_infos[mi][img_resized.index(ir)]
                instances.append(instance)
        else:
            return None
    payload = {'signature_name': env_setting['signature_name'], 'instances': instances}
    data = json.dumps(payload)

    pred_softmax = {}
    for idx, msn in enumerate(model_spec_name):
        try:
            if (isinstance(version_label, list) != True) or (version_label[idx] == None):
                try:
                    pred_softmax[msn] = query_latest_available_serving(component_dict['specific_url'][idx], msn, data)
                except:
                    pred_softmax[msn] = query_latest_available_serving(model_url, msn, data)
            else:
                try:
                    pred_softmax[msn] = query_serving_with_version_label(version_label[idx], component_dict['specific_url'][idx], msn, data)
                except:
                    pred_softmax[msn] = query_serving_with_version_label(version_label[idx], model_url, msn, data)
            if pred_softmax[msn] == None:
                current_app.logger.error('Request TF RESTful server error.')
                print_logger_json('error', 'Request TF RESTful server error.')
                if len(env_setting['model_output_name']) == 1:
                    if only_one_flag is False:
                        pred_softmax[msn] = [['None'] for _ in range(len(img_resized))]
                    else:
                        pred_softmax[msn] = ['None']
            else:
                if only_one_flag is True:
                    pred_softmax[msn] = pred_softmax[msn][0]
        except Exception as e: 
            current_app.logger.error(f'Request TF RESTful server error. message: {e}')
            print_logger_json('error', f'Request TF RESTful server error. message: {e}')
            if len(env_setting['model_output_name']) == 1:
                if only_one_flag is False:
                    pred_softmax[msn] = [['None'] for _ in range(len(img_resized))]
                else:
                    pred_softmax[msn] = ['None']
    # own model inference
    try:
        if if_test_model and own_model_setting!={}:
            if own_model_setting['outcome_choice']=='consider' or own_model_setting['outcome_choice']=='background':
                for oms_comps in list(dict(own_model_setting['model_setting']).keys()):
                    for oc in oms_comps.split('/'):
                        if oc == component:
                            own_outcome_dict = restful_request_server( 
                                only_one_flag, oms_comps, img_resized, all_infos, if_test_model=False)
                            for oo_key in list(dict(own_outcome_dict).keys()):
                                pred_softmax[oo_key] = own_outcome_dict[oo_key]
    except Exception as e:
        current_app.logger.error(f'Request TEST TF RESTful server error. message: {e}')
        print_logger_json('error', f'Request TEST TF RESTful server error. message: {e}') 
    return pred_softmax

def img_format_array(softmax_ary, ImgBatchByComp, oms):
    # comp_fullname = list(dict(model_setting).keys())
    global time_out, own_model_setting, env_setting, model_setting
    env_setting = current_app.config['env_setting']
    model_setting = current_app.config['model_setting']
    own_model_setting = oms
    for comp in ImgBatchByComp:
        if len(ImgBatchByComp[comp]['putback_idx'])==0:
            continue
        elif len(ImgBatchByComp[comp]['putback_idx'])==1:
            time_out = 0.5 * len(ImgBatchByComp[comp]['image'][0])
            pred_softmax = restful_request_server(
                True, comp, ImgBatchByComp[comp]['image'][0], ImgBatchByComp[comp])
            if pred_softmax is None:
                return None 
            this_infos = {}
            for k in ImgBatchByComp[comp].keys():
                this_infos[k] = ImgBatchByComp[comp][k][0]
            softmax_ary[ImgBatchByComp[comp]['putback_idx'][0]] = classify.main(
                comp, pred_softmax, own_model_setting, this_infos)
        else: 
            time_out = 0.5 * len(ImgBatchByComp[comp]['image'])
            pred_softmax = restful_request_server(
                False, comp, ImgBatchByComp[comp]['image'], ImgBatchByComp[comp])
            if pred_softmax is None:
                return None 
            this_infos = {}
            for k in ImgBatchByComp[comp].keys():
                this_infos[k] = ImgBatchByComp[comp][k][img_count]
            for img_count, putback_idx in enumerate(ImgBatchByComp[comp]['putback_idx']):
                each_pred_softmax = {k:pred_softmax[k][img_count] 
                                            for k in list(dict(pred_softmax).keys())}
                softmax_ary[putback_idx] = classify.main(
                    comp, each_pred_softmax, own_model_setting, this_infos)
    return softmax_ary
    
def img_format_b64(softmax_ary, ImgBatchByComp, oms):
    # comp_fullname = list(dict(model_setting).keys())
    global time_out, own_model_setting, env_setting, model_setting
    env_setting = current_app.config['env_setting']
    model_setting = current_app.config['model_setting']
    own_model_setting = oms
    for comp in ImgBatchByComp:
        # logging.warning(comp) #'AluCap','ElecCap'
        if len(ImgBatchByComp[comp]['putback_idx'])==0:
            continue
        elif len(ImgBatchByComp[comp]['putback_idx'])==1: # Only one in this comp
            time_out = 0.5 * len(ImgBatchByComp[comp]['image'][0])
            pred_softmax = restful_request_server(
                True, comp, ImgBatchByComp[comp]['image'][0], ImgBatchByComp[comp])
            if pred_softmax is None:
                return None
            this_infos = {}
            for k in ImgBatchByComp[comp].keys():
                this_infos[k] = ImgBatchByComp[comp][k][0]
            softmax_ary[ImgBatchByComp[comp]['putback_idx'][0]] = classify.main(
                comp, pred_softmax, own_model_setting, this_infos)
        else: # More than one counts in this comp
            time_out = 0.5 * len(ImgBatchByComp[comp]['image'])
            pred_softmax = restful_request_server(
                False, comp, ImgBatchByComp[comp]['image'], ImgBatchByComp[comp])
            if pred_softmax is None:
                return None
            for img_count, putback_idx in enumerate(ImgBatchByComp[comp]['putback_idx']):
                each_pred_softmax = {k:pred_softmax[k][img_count] 
                                            for k in list(dict(pred_softmax).keys())}
                this_infos = {}
                for k in ImgBatchByComp[comp].keys():
                    this_infos[k] = ImgBatchByComp[comp][k][img_count]
                softmax_ary[putback_idx] = classify.main(
                    comp, each_pred_softmax, own_model_setting, this_infos)
    return softmax_ary
import requests, datetime, os, base64, time, json
from flask import current_app

def print_logger_json(sev, msg):
    js = {'severity': str(sev), 
            'project': str(current_app.config['env_setting']['project_code']),
            'msg': str(msg), 
            'time': str(datetime.datetime.now())}
    print(json.dumps(js), flush=True)

def tf_addr_health(addr):
    try:
        res = requests.get(addr, timeout=1)
        error_message = ''
        if res.status_code in [200, 201]:
            model_version_status = json.loads(res.text)['model_version_status']
            for mvs in model_version_status:
                if mvs['state']=='AVAILABLE' and mvs['status']['error_code']=='OK' and mvs['status']['error_message']=='':
                    return 1
                elif mvs['status']['error_message'] != '':
                    error_message = str(mvs['version']) + ': ' + str(mvs['status']['error_message'])
        if error_message != '':
            current_app.logger.error((
                f'tf_addr_health requests.get Failed! '
                f'When {datetime.datetime.now()} '
                f'At link: {addr}'
                f'error_msg: {error_message}'
            ))
            print_logger_json('error', f'tf_addr_health requests.get Failed! With error_msg: {error_message} At link: {addr}')
        else:
            current_app.logger.error((
                f'tf_addr_health requests.get Failed! '
                f'When {datetime.datetime.now()} '
                f'At link: {addr}'
            ))
            print_logger_json('error', f'tf_addr_health requests.get Failed! At link: {addr}')
        return 0
    except:
        current_app.logger.error((
            f'tf_addr_health requests.get Failed! '
            f'When {datetime.datetime.now()} '
            f'At link: {addr}'
        ))
        print_logger_json('error', f'tf_addr_health requests.get Failed! At link: {addr}')
        return 0

def save_image_to_local(data, index=0):
    image_saving_dir = current_app.config['env_setting']['image_saving']
    try:
        production_date = datetime.datetime.now().date()
        component = data['component']
        filename = data['filename']
        imgdata = base64.b64decode(data['saved_image'])
        target_folder1 = f'''/{image_saving_dir}/'''
        if not os.path.exists(target_folder1):
            os.makedirs(target_folder1)
        target_folder2 = f'''/{image_saving_dir}/{production_date}/'''
        if not os.path.exists(target_folder2):
            os.makedirs(target_folder2)
        target_folder3 = f'''/{image_saving_dir}/{production_date}/{component}/'''
        if not os.path.exists(target_folder3):
            os.makedirs(target_folder3)
        target_folder = f'''/{image_saving_dir}/{production_date}/{component}/{data['pred_class']}/'''
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
        if os.path.splitext(filename)[-1] == "":
            ext = current_app.config['env_setting']['image_saving_ext']
            target_dir = f'''{target_folder}{filename}.{ext}'''
        else:
            target_dir = f'''{target_folder}{filename}'''
        with open(target_dir, 'wb') as fs:
            fs.write(imgdata)
        return True
    except Exception as e:
        return e

def calculate_secs_taken(previous_time):
    return time.time() - previous_time

def iterdict(d):
    for k, v in d.items():
        if isinstance(v, dict):
            iterdict(v)
        else:
            if type(v) == list:
                new_list = []
                for vv in v:
                    if (type(vv) != str) and (type(vv) != int):
                        new_list.append(str(vv))
                    else:
                        new_list.append(vv)
                d.update({k: new_list})
            elif (type(v) != str) and (type(v) != int):
                v = str(v)
                d.update({k: v})
    return d

########################### funcitons below cleaned to process py #################################

def final_outcome_judge(ori_result, new_result, confidence):
    if new_result == 'OK':
        if (ori_result['pred'] == 'OK') and (confidence < ori_result['con']):
            ori_result.update({'con':confidence})
    else:
        if ori_result['pred'] == 'OK':
            ori_result.update({'con':confidence})
            ori_result.update({'pred':new_result})
        else:
            if confidence < ori_result['con']:
                ori_result.update({'con':confidence})
    return ori_result

def apply_con_threshold(ori_prediction, con_threshold):
    (OKornot, confidence) = ori_prediction
    if confidence < con_threshold:
        confidence = (-1) * confidence
        if (con_threshold >= 0) and (con_threshold <= 1) and (OKornot == 'OK'):
            OKornot = 'NG-BelowThreshold'
    return (OKornot, confidence)

def parse_image_filename(filename):
    # CN0RM5DRWS20007600PAA00_355_0DJ01_0001_TC9401_ElecCap_270_220_NA_0.png
    symbols = {}
    possible_comps = ['AluCap', 'ElecCap', 'acpi', 'Ins', 'SATA', 'L', 'BH', 'Jumper', 'PCI', 'Aud', 'Stud', 'NI', 'DimSoc', 'CONN', 'USB', 'VGA']
    possible_bool = False
    for c in possible_comps:
        if c in filename.split('_'):
            possible_bool = True
            symbols.update({'component': c})
            filename = filename.split('.')[0] # CN0RM5DRWS20007600PAA00_355_0DJ01_0001_TC9401_ElecCap_270_220_NA_0
            symbols.update({'filename': filename})
            splited_filename = filename.split(f'_{c}_')
            back_filename = splited_filename[-1] # 270_220_NA_0
            front_filename = splited_filename[0] # CN0RM5DRWS20007600PAA00_355_0DJ01_0001_TC9401
            symbols.update({'SN': front_filename})
            symbols.update({'PanelNo': front_filename.split('_')[0]})
            front_filename = front_filename.replace(f'{symbols["PanelNo"]}_', '') # 355_0DJ01_0001_TC9401
            symbols.update({'location': front_filename.split('_')[-1]})
            front_filename = front_filename.replace(f'_{symbols["location"]}', '') # 355_0AH01_B002
            symbols.update({'eagle': front_filename.replace('_', '')})
            symbols.update({'degree': back_filename.split('_')[0]})
            symbols.update({'capacity': back_filename.split('_')[1]})
            symbols.update({'voltage': back_filename.split('_')[2]})
            symbols.update({'index': back_filename.split('_')[3]})            
    if possible_bool == False:
        current_app.logger.error('parsing image filenames occurs error!')
        print_logger_json('error', 'parsing image filenames occurs error!')
        return {}
    return symbols

def request_to_data(request):
    if request.method == 'POST':
        if current_app.config['env_setting']['request_post_file']=='False' or current_app.config['env_setting']['request_post_file']==False:
            # client request post header with 'content-type': 'application/json'
            if (not request.json) or ('instances' not in request.json):
                return 400
            data = request.json
            # data = request.data
            # data = json.loads(data)
        elif current_app.config['env_setting']['request_post_file']=='True' or current_app.config['env_setting']['request_post_file']==True:
            # client request post header without 'content-type': 'application/json'
            # print(request.environ)
            # print(request.form.to_dict(flat=False))
            # print(request.form.getlist('img_name'))
            # print(request.form.getlist('img_info'))
            # print(request.files.getlist('img_file'))
            data = request
            print(data)
        else:
            current_app.logger.error('request_post_file in config.json must be True or False')
            print_logger_json('error', 'request_post_file in config.json must be True or False')
            return {'predictions': ''}
    elif request.method == 'GET':
        if (not request.args) or ('folder' not in request.args): 
            current_app.logger.error('No expected key in args, folder should be included!')
            print_logger_json('error', 'No expected key in args, folder should be included!')
            return {'predictions': ''}
        try:
            if 'folder' in request.args:
                folder = request.args.get('folder')
                with open('/data/'+folder+'/data.json', 'r') as f: 
                    data = json.load(f)
            elif 'file' in request.args:
                file = request.args.get('file')
                with open('/tf/notebook/'+file, 'r') as f:
                    data = json.load(f)
            else:
                app.logger.error('neither folder nor file in request.args')
                print_logger_json('error', 'neither folder nor file in request.args')
                return {'predictions': ''}
        except:
        # Exception says : local variable 'data' referenced before assignment if directory is wrong
            current_app.logger.error((
                f'data.json defined above does not exist. '
                f'When {datetime.datetime.now()} '
                f'Request content: {request.args}'
            ))
            print_logger_json('error', f'data.json defined above does not exist. Request content: {request.args}.')
            return {'predictions': ''}
    return data

def to_request_json(data, request_now, index=0):
    data_dict = {'logger': 'request', 
                'severity': 'debug', 
                'req_time': str(request_now),
                'date': str(request_now).split(' ')[0]}
    if current_app.config['env_setting']['request_post_file']=='False' or current_app.config['env_setting']['request_post_file']==False:
        data_keys = list(dict(data).keys())
        for dk in data_keys:
            if dk != 'image':
                data_dict.update({dk: data[dk]})
            if dk == 'eagle':
                data_dict.update({dk: data[dk].replace('_', '')})
            elif dk == 'SN':
                data_dict.update({'PanelNo': data[dk].split('_')[0]})
                data_dict.update({'location': data[dk].split('_')[-1]})
            elif dk == 'capvalue':
                data_dict.update({'capacity': data[dk]})
        if data['component'] not in list(dict(current_app.config['model_setting']).keys()):
            data_dict.update({'severity': 'info'})
        if 'filename' not in data_keys:
            if 'SN' not in data_keys:
                # data_dict.update({'PanelNo': None})
                # data_dict.update({'location': None})
                current_app.logger.error((
                    f'SN is not in instances '
                    f'When {request_now}'
                ))
                print_logger_json('error', 'SN is not in instances')
            if 'eagle' not in data_keys:
                data_dict.update({'eagle': None})
            else:
                data_dict.update(
                    {'SN': f'{data_dict["PanelNo"]}_{data_dict["eagle"]}_{data_dict["location"]}'})
        else: 
            if data['component'] in data['filename'].split('_'):
                splited_filename = data['filename'].split(f'_{data["component"]}_')
                back_filename = splited_filename[-1] # 0_270_NA_0
                front_filename = splited_filename[0] # CN0HMX8DWS20006A03RDA01_355_0AH01_B002_PT4
                data_dict.update({'SN': front_filename})
                data_dict.update({'PanelNo': front_filename.split('_')[0]})
                front_filename = front_filename.replace(f'{data_dict["PanelNo"]}_', '') # 355_0AH01_B002_PT4
                data_dict.update({'location': front_filename.split('_')[-1]})
                front_filename = front_filename.replace(f'_{data_dict["location"]}', '') # 355_0AH01_B002
                data_dict.update({'eagle': front_filename.replace('_', '')})
                try: 
                    if back_filename.split('_')[0] != str(data['degree']):
                        data_dict.update({'severity': 'warning'})
                        current_app.logger.error((
                            f'degree in "filename" key is not the same as "degree" key '
                            f'When {request_now}'
                        ))
                        print_logger_json('error', 'degree in "filename" key is not the same as "degree" key')
                    if back_filename.split('_')[1] != str(data['capacity']):
                        data_dict.update({'severity': 'warning'})
                        current_app.logger.error((
                            f'capacity in "filename" key is not the same as "capacity" key '
                            f'When {request_now}'
                        ))
                        print_logger_json('error', 'capacity in "filename" key is not the same as "capacity" key')
                    if back_filename.split('_')[2] != str(data['voltage']):
                        data_dict.update({'severity': 'warning'})
                        current_app.logger.error((
                            f'voltage in "filename" key is not the same as "voltage" key '
                            f'When {request_now}'
                        ))
                        print_logger_json('error', 'voltage in "filename" key is not the same as "voltage" key')
                    data_dict.update({'index': back_filename.split('_')[-1]})
                except:
                    data_dict.update({'severity': 'warning'})
                    current_app.logger.error((
                        f'either degree, capacity or voltage key no in request json '
                        f'When {request_now}'
                    ))
                    print_logger_json('error', 'either degree, capacity or voltage key no in request json')
    elif current_app.config['env_setting']['request_post_file']=='True' or current_app.config['env_setting']['request_post_file']==True:
        form_keys = list(dict(data).keys())
        for fk in form_keys:
            data_dict.update({fk: data[fk][index]})
        img_name = data['img_name'][index]
        symbols = parse_image_filename(img_name)
        if symbols['component'] not in list(dict(current_app.config['model_setting']).keys()):
            data_dict.update({'severity': 'info'})
        for key, value in symbols.items():
            data_dict.update({key: value})
    return data_dict

def to_response_json(secs_taken, data_dict, softmax):
    data_dict['logger'] = 'predict'
    data_dict['res_time'] = str(datetime.datetime.now())
    data_dict['req_secs_taken'] = str(secs_taken)
    data_dict['pred_class'] = softmax['pred']
    data_dict['confidence'] = softmax['con']
    data_dict['ng_model_name'] = softmax['ng_parts']
    try:
        outcome_choice = current_app.config['own_model_setting']['outcome_choice']
        if (outcome_choice == 'background') or (outcome_choice == 'consider'):
            try: 
                data_dict['own_pred_class'] = softmax['ownmodel_pred']
                data_dict['own_confidence'] = softmax['ownmodel_con']
            except Exception as e:
                print(f'ownmodel_pred & ownmodel_con does not exist. Except: {e}')
                # current_app.logger.error((
                #     f'ownmodel_pred & ownmodel_con does not exist.\n'
                #     f'Except: {e}'
                # ))
    except:
        current_app.logger.info('own_model_setting in config.json empty.')
        print_logger_json('info', 'own_model_setting in config.json empty.')
    if 'capacity' not in data_dict:
        data_dict['capacity'] = 'NA'
        data_dict['voltage'] = 'NA'
        data_dict['index'] = 'NA'
    elif 'voltage' not in data_dict:
        data_dict['voltage'] = 'NA'
        data_dict['index'] = 'NA'
    elif 'index' not in data_dict:
        data_dict['index'] = 'NA'
    if 'filename' not in data_dict:
        data_dict['filename'] = (
            f'{data_dict["SN"]}_'
            f'{data_dict["component"]}_'
            f'{data_dict["degree"]}_'
            f'{data_dict["capacity"]}_'
            f'{data_dict["voltage"]}_'
            f'{data_dict["index"]}'
        )
    return data_dict
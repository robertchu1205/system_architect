# collections for append list in dict
import os, collections, datetime
import applications.grpc_request as gr
import applications.rest_request as rr
# import applications.classify as classify
from flask import current_app
from applications.functions import print_logger_json, save_image_to_local

def batch_same_comp(data):
    # Filter input json to the its belonged array or dict
    # {'AluCap': defaultdict(list, {}),'ElecCap': defaultdict(list, {})...}
    # comp changes by config model setting
    ImgBatchByComp = {k:collections.defaultdict(list) for k in list(dict(current_app.config['model_setting']).keys())}
    try:
        for idx, d in enumerate(data):
            try:
                component = d['component']
                # ImgBatchByComp[component]['degree'].append(d['degree'])
                # ImgBatchByComp[component]['voltage'].append(d['voltage'])
                # ImgBatchByComp[component]['img'].append(d['image'])
                # try:
                #     ImgBatchByComp[component]['capacity'].append(d['capacity'])
                # except:
                #     ImgBatchByComp[component]['capacity'].append(d['capvalue'])
                ImgBatchByComp[component]['putback_idx'].append(idx)
                for k, v in d.items():
                    ImgBatchByComp[component][k].append(v)
            except Exception as e: 
                current_app.logger.error(f'component {e} not in model_setting')
                print_logger_json('error', f'component {e} not in model_setting')
        return ImgBatchByComp
    except: 
        current_app.logger.error(f'Filter attributes from json error.')
        print_logger_json('error', f'Filter attributes from json error.')
        return None

def predict_and_saveimages(data):
    try:
        softmax_ary = main(data)
    except Exception as e:
        current_app.logger.error(f'gateway.py exists error. msg: {e}')
        print_logger_json('error', f'gateway.py exists error. msg: {e}')
        instances = ''
        softmax_ary = ''
    try:
        x = instances
        return (softmax_ary, instances)
    except NameError:
        # instances = [{'pred_class': sa['pred'] if sa['pred'][0:2]!='NG' else 'NG', 
        #                 'confidence': sa['con']} for sa in softmax_ary]
        # Transfer detailed pred_class to OK/NG
        try:
            instances = []
            for idx, sa in enumerate(softmax_ary):
                data[idx]['logger'] = 'predict'
                data[idx]['pred'] = sa['pred']
                data[idx]['ng_model_name'] = sa['ng_parts']
                data[idx]['date'] = str(datetime.datetime.now()).split(' ')[0]
                if str(current_app.config['env_setting']['request_post_file']) == 'True':
                    data[idx]['ai_score'] = sa['con']
                    if sa['pred'][0:2] != 'NG':
                        data[idx]['ai_result'] = sa['pred']
                    else:
                        data[idx]['ai_result'] = 'NG'
                    ins = {'ai_result':data[idx]['ai_result'],'ai_score': sa['con']}
                    if 'timestamp' in list(dict(data[idx]).keys()):
                        ins.update({'timestamp':data[idx]['timestamp']})
                    if 'kb_id' in list(dict(data[idx]).keys()):
                        ins.update({'kb_id':data[idx]['kb_id']})
                    if 'PanelNo' in list(dict(data[idx]).keys()):
                        ins.update({'kb_id':data[idx]['PanelNo']})
                    if 'key_name' in list(dict(data[idx]).keys()):
                        ins.update({'key_name':data[idx]['key_name']})
                    if 'location' in list(dict(data[idx]).keys()):
                        ins.update({'key_name':data[idx]['location']})
                    if 'extra_infos_to_return' in list(dict(current_app.config['env_setting']).keys()):
                        for ei in current_app.config['env_setting']['extra_infos_to_return']:
                            ins.update({ei:data[idx][ei]})
                    instances.append(ins)
                else:
                    data[idx]['confidence'] = sa['con']
                    if sa['pred'][0:2] != 'NG':
                        instances.append({'pred_class':sa['pred'],'confidence': sa['con']})
                        data[idx]['pred_class'] = sa['pred']
                    else:
                        instances.append({'pred_class':'NG','confidence': sa['con']})
                        data[idx]['pred_class'] = 'NG'
                try:
                    if current_app.config['test_model_setting'] == {}:
                        continue
                    outcome_choice = current_app.config['test_model_setting']['outcome_choice']
                    if (outcome_choice == 'background') or (outcome_choice == 'consider'):
                        try: 
                            data[idx]['test_pred_class'] = sa['ownmodel_pred']
                            data[idx]['test_confidence'] = sa['ownmodel_con']
                        except Exception as e:
                            check_if_append = False
                            for oms_comps in list(dict(current_app.config['test_model_setting']['model_setting']).keys()):
                                for oc in oms_comps.split('/'):
                                    if oc == comp:
                                        check_if_append = True
                            if check_if_append == False:
                                current_app.logger.error(f'ownmodel_pred & ownmodel_con does not exist. Except: {e}')
                                print_logger_json('error', f'ownmodel_pred & ownmodel_con does not exist. Except: {e}')
                except:
                    continue
        except:
            current_app.logger.error(f'softmax_ary to instances error')
            print_logger_json('error', f'softmax_ary to instances error')
        try:
            for idx, d in enumerate(data):
                if str(current_app.config['env_setting']['image_saving']) != 'False':
                    save_bool = save_image_to_local(d)
                    if save_bool != True:
                        current_app.logger.error(f'{save_bool} save_image_to_local errors.')
                        print_logger_json('error', f'{save_bool} save_image_to_local errors.')
                d.pop('image')
                d.pop('saved_image')
        except:
            current_app.logger.error(f'save_image_to_local errors.')
            print_logger_json('error', f'save_image_to_local errors.')
    return (data, instances)

def main(data):
    ImgBatchByComp = batch_same_comp(data)
    # Put NG, con:-2.0 in array to insert value to exact position we want
    output_dict = {'con':-2.0, 'pred': 'NG', 'ng_parts': 'comp-not-online'}
    softmax_ary = [output_dict for _ in range(len(data))]
    after_classify = None
    if ImgBatchByComp is None:
        return softmax_ary
    try:
        own_model_setting = current_app.config['test_model_setting']
    except:
        own_model_setting = {}
    if current_app.config['env_setting']['tfs_method'] == 'grpc':
        if current_app.config['env_setting']['image_format'] == 'array':
            after_classify = gr.img_format_array(softmax_ary, ImgBatchByComp, own_model_setting)
        elif current_app.config['env_setting']['image_format'] == 'b64':
            after_classify = gr.img_format_b64(softmax_ary, ImgBatchByComp, own_model_setting)
        else:
            current_app.logger.error(f'image_format in config is not accurate, only could be array or b64.')
            print_logger_json('error', f'image_format in config is not accurate, only could be array or b64.')
            for s in softmax_ary:
                s['ng_parts'] = 'wrong-image_format'
    elif current_app.config['env_setting']['tfs_method'] == 'rest':
        if current_app.config['env_setting']['image_format'] == 'array':
            after_classify = rr.img_format_array(softmax_ary, ImgBatchByComp, own_model_setting)
        elif current_app.config['env_setting']['image_format'] == 'b64':
            after_classify = rr.img_format_b64(softmax_ary, ImgBatchByComp, own_model_setting)
        else:
            current_app.logger.error(f'image_format in config is not accurate, only could be array or b64.')
            print_logger_json('error', f'image_format in config is not accurate, only could be array or b64.')
            for s in softmax_ary:
                s['ng_parts'] = 'wrong-image_format'
    else:
        current_app.logger.error(f'tfs_method in config is not accurate, only could be grpc or rest.')
        print_logger_json('error', f'tfs_method in config is not accurate, only could be grpc or rest.')
        for s in softmax_ary:
            s['ng_parts'] = 'wrong-tfs_method'
    if after_classify == None:
        return softmax_ary
    else:
        return after_classify
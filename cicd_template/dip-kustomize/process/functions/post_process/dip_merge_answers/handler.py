import numpy as np

# NG has the highest priority, and lower confidence is next
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

# answers from inference lower than threshold changed to negative here
def apply_con_threshold(ori_prediction, con_threshold):
    (OKornot, confidence) = ori_prediction
    if confidence < con_threshold:
        confidence = (-1) * confidence
        if (con_threshold >= 0) and (con_threshold <= 1) and (OKornot == 'OK'):
            OKornot = 'NG-BelowThreshold'
    return (OKornot, confidence)

# special condition: AluCap
def AluCap(pred_mn, pred_lookup, degree, capacity):
    OKornot = pred_lookup
    if pred_mn == model_setting['AluCap']['model_name'][0]:
        OKornot = pred_lookup # Output NG Category
    elif pred_mn == model_setting['AluCap']['model_name'][1]: # and (output_dict['pred'] == 'OK')
        if int(pred_lookup) == int(degree):
            OKornot = 'OK'
        else:
            OKornot = 'NG-InversePolarity'
    elif pred_mn == model_setting['AluCap']['model_name'][2]: # and (output_dict['pred'] == 'OK')
        if int(pred_lookup) == int(capacity):
            OKornot = 'OK'
        else:
            OKornot = 'NG-WrongOCV'
    # elif (int(ocv_degree)!=int(degree)) and (int(ocv_capacity)==int(capacity)):
    #     OKornot = 'NG-InversePolarityinOCV'
    return OKornot

# special condition: ElecCap
def ElecCap(pred_mn, pred_lookup, degree):
    OKornot = pred_lookup
    if pred_mn == model_setting['ElecCap']['model_name'][0]:
        OKornot = pred_lookup # Output NG Category
    elif pred_mn == model_setting['ElecCap']['model_name'][1]: # and (output_dict['pred'] == 'OK')
        if int(pred_lookup) == int(degree):
            OKornot = 'OK'
        else:
            OKornot = 'NG-InversePolarity'
    return OKornot

# special condition: m1_color
def m1_color(comp, pred_mn, pred_lookup, capacity):
    OKornot = pred_lookup
    color_dict = {'1':'Black', '2':'Blue', '3':'White'}
    if capacity == 'NA':
        if pred_lookup != 'NG':
            OKornot = 'OK'
        else:
            OKornot = pred_lookup # Output NG Category
    else:
        try:
            supposed_color = color_dict[str(capacity)]
        except:
            supposed_color = 'NoColour'
            error_msg.append(f'capacity: {str(capacity)} of {comp} could not be matched by color_dict')
        if pred_lookup == 'NG':
            OKornot = pred_lookup # Output NG Category
        elif pred_lookup == supposed_color:
            OKornot = 'OK'
        else:
            OKornot = 'NG-WrongColor'
    return OKornot

def distribution(input, pred_mn, pred):
    idx = input['append_msn'].index(pred_mn)
    if len(env_setting['model_output_name']) == 1:
        pred_lookup = input['ori_dt'][idx][str(np.argmax(pred))]
        confidence = np.max(pred)
        if input['comp']=='AluCap':
            OKornot = AluCap(pred_mn, pred_lookup, input['this_infos']['degree'], input['this_infos']['capacity'])
        elif input['comp']=='ElecCap':
            OKornot = ElecCap(pred_mn, pred_lookup, input['this_infos']['degree'])
        elif input['comp'] in env_setting['comps_to_match_m1_color']:
            OKornot = m1_color(input['comp'], pred_mn, pred_lookup, input['this_infos']['capacity'])
        elif input['comp'] in env_setting['comps_to_match_m1']:
            OKornot = pred_lookup
        else:
            OKornot = pred
    else:
        for m in env_setting['model_output_name']:
            if m == 'pred_class':
                OKornot = pred[m]
            elif m == 'confidence':
                confidence = pred[m]
            else:
                output_dict.update({m:pred[m]})
    # Add Threshold cuz performance is bad while con below threshold
    try:
        if type(input['con_threshold'][idx]) == int or type(input['con_threshold'][idx]) == float:
            (OKornot, confidence) = apply_con_threshold((OKornot, confidence), float(input['con_threshold'][idx]))
    except Exception as e:
        return f'con_threshold of {pred_mn} error. msg: {e}'
    return (OKornot, confidence)

def prometheus_metrics(input, index, pred_mn, prome_pred_class, confidence):
    # model_name label of prometheus metrics should be {model_name:version_label} or {model_name:specific_url}
    try:
        version_label = model_setting[input['comp']]['version_label'][index]
        if type(version_label) != int and type(version_label) != float:
            raise TypeError("decent version_label is int or float")
        pred_mn = f'{pred_mn}:{version_label}'
    except:
        specific_url = model_setting[input['comp']]['specific_url'][index]
        pred_mn = f'{pred_mn}:{specific_url}'
    return (pred_mn, [['confidence_sum', prome_pred_class, abs(confidence)], 
                            ['predicts_img_counter', prome_pred_class, 1]])
    # g.prome_dict['confidence_sum'].labels(pred_mn, prome_pred_class).inc(abs(confidence))
    # g.prome_dict['predicts_img_counter'].labels(pred_mn, prome_pred_class).inc()

# input: comp, con_threshold, pred_softmax, append_msn, ori_dt, this_infos, outcome_choice, env_setting, model_setting, ori_msn
class handler:
    def execute(input): 
        global env_setting, model_setting, error_msg
        env_setting = input['env_setting']
        model_setting = input['model_setting']
        try:
            ori_msn = input['ori_msn']
            output_dict = {'con':2.0,'pred':'OK','ng_parts':[],'ownmodel_pred':'','ownmodel_con':''}
        except:
            ori_msn = []
            output_dict = {'con':2.0,'pred':'OK','ng_parts':[]}
        ng_msn = []         # model names are ng
        error_msg = []      # concat error message
        prome_dict = {}     # promethues metrics to return
        # for pred_mn in list(dict(input['pred_softmax']).keys()):
        for index, pred in enumerate(input['pred_softmax']):
            pred_mn = input['append_msn'][index]
            if pred == ['None']:
                ng_msn.append(f'tfs-error-{pred_mn}')
                error_msg.append(f'pred_mn: {pred_mn} SERVING ERROR.')
                continue
            try:
                mapped_answers = distribution(input, pred_mn, pred)
                if type(mapped_answers) == str:
                    error_msg.append(mapped_answers)
                else:
                    (OKornot, confidence) = mapped_answers
            except Exception as e:
                ng_msn.append(f'parse-error-{pred_mn}')
                error_msg.append(f'''parsing {input['comp']} info wrong since {e}''')
                continue
            # con output lower / NG one
            if (ori_msn == []) or (pred_mn in ori_msn):
                output_dict = final_outcome_judge(output_dict, OKornot, confidence)
            else:
                # ownmodel outcome
                # OKornot = pred_lookup # Output NG Category
                if input['outcome_choice'] == 'consider':
                    output_dict = final_outcome_judge(output_dict, OKornot, confidence)
                elif input['outcome_choice'] == 'background':
                    output_dict['ownmodel_pred'] = OKornot
                    output_dict['ownmodel_con'] = confidence
            # save pred_class as "NG" for prometheus label
            if OKornot[0:2] != 'NG':
                prome_pred_class = OKornot
            else:
                prome_pred_class = 'NG'
            # prometheus metrics
            (prom_mn, metrics_list) = prometheus_metrics(input, index, pred_mn, prome_pred_class, confidence)
            prome_dict[prom_mn] = metrics_list
            # save ng models
            if OKornot != 'OK':
                ng_msn.append(prom_mn)
        output_dict.update({'ng_parts':'&'.join(ng_msn)})
        if output_dict['con'] == 2.0 and output_dict['pred'] == 'OK':
            output_dict['pred'] = 'NG'
            output_dict['con'] = -2.0
        output = {
            "output_dict": output_dict,
            "error_msg": error_msg,
            "prome_dict": prome_dict,
        }
        return output
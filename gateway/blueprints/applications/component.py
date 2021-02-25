from flask import current_app, g
import numpy as np
from applications.functions import final_outcome_judge, apply_con_threshold, print_logger_json

def Merge(comp, con_threshold, pred_softmax, append_msn, append_dt, this_infos, ori_msn=[]):
    output_dict = {'con':2.0,'pred':'OK','ng_parts':[],'ownmodel_pred':'','ownmodel_con':''}
    try:
        outcome_choice = current_app.config['test_model_setting']['outcome_choice']
    except:
        outcome_choice = None
    ng_msn = []
    for pred_mn in list(dict(pred_softmax).keys()):
        if pred_softmax[pred_mn] == ['None']:
            ng_msn.append(f'tfs-error-{pred_mn}')
            current_app.logger.error(f'pred_mn: {pred_mn} SERVING ERROR.')
            print_logger_json('error', f'pred_mn: {pred_mn} SERVING ERROR.')
            continue
        try:
            idx = append_msn.index(pred_mn)
            if len(current_app.config['env_setting']['model_output_name']) == 1:
                pred_lookup = append_dt[idx][str(np.argmax(pred_softmax[pred_mn]))]
                confidence = np.max(pred_softmax[pred_mn])
                if comp=='AluCap':
                    OKornot = AluCap(pred_mn, pred_lookup, this_infos['degree'], this_infos['capacity'])
                elif comp=='ElecCap':
                    OKornot = ElecCap(pred_mn, pred_lookup, this_infos['degree'])
                elif comp in current_app.config['env_setting']['comps_to_match_m1_color']:
                    OKornot = m1_color(comp, pred_mn, pred_lookup, this_infos['capacity'])
                elif comp in current_app.config['env_setting']['comps_to_match_m1']:
                    OKornot = pred_lookup
                else:
                    OKornot = pred_softmax[pred_mn]
            else:
                for m in current_app.config['env_setting']['model_output_name']:
                    if m == 'pred_class':
                        OKornot = pred_softmax[pred_mn][m]
                    elif m == 'confidence':
                        confidence = pred_softmax[pred_mn][m]
                    else:
                        output_dict.update({m:pred_softmax[pred_mn][m]})
                # current_app.logger.info(f'There is an unknown comp: {comp} returned pred_class')
                # print_logger_json('info', f'There is an unknown comp: {comp} returned pred_class')
            # Add Threshold cuz performance is bad while con below threshold
            try:
                if con_threshold[idx] != 'None':
                    (OKornot, confidence) = apply_con_threshold((OKornot, confidence), float(con_threshold[idx]))
            except Exception as e:
                current_app.logger.debug(f'con_threshold of {pred_mn} error. msg: {e}')
                print_logger_json('debug', f'con_threshold of {pred_mn} error. msg: {e}')    
        except Exception as e:
            ng_msn.append(f'parse-error-{pred_mn}')
            current_app.logger.error(f'parsing {comp} info wrong since {e}')
            print_logger_json('error', f'parsing {comp} info wrong since {e}')
            continue
        # con output lower / NG one
        if (ori_msn == []) or (pred_mn in ori_msn):
            output_dict = final_outcome_judge(output_dict, OKornot, confidence)
        else:
            # ownmodel outcome
            # OKornot = pred_lookup # Output NG Category
            if outcome_choice == 'consider':
                output_dict = final_outcome_judge(output_dict, OKornot, confidence)
            elif outcome_choice == 'background':
                output_dict['ownmodel_pred'] = OKornot
                output_dict['ownmodel_con'] = confidence
        # save ng models
        if OKornot != 'OK':
            ng_msn.append(pred_mn)
        # save pred_class as "NG" for prometheus label
        if OKornot[0:2] != 'NG':
            prome_pred_class = OKornot
        else:
            prome_pred_class = 'NG'
        g.prome_dict['confidence_sum'].labels(pred_mn, prome_pred_class).inc(abs(confidence))
        g.prome_dict['predicts_img_counter'].labels(pred_mn, prome_pred_class).inc()
    output_dict.update({'ng_parts':'&'.join(ng_msn)})
    if output_dict['con'] == 2.0 and output_dict['pred'] == 'OK':
        output_dict['pred'] = 'NG'
        output_dict['con'] = -2.0
    return output_dict

def AluCap(pred_mn, pred_lookup, degree, capvalue):
    OKornot = pred_lookup
    if pred_mn == current_app.config['model_setting']['AluCap']['model_name'][0]:
        OKornot = pred_lookup # Output NG Category
    elif pred_mn == current_app.config['model_setting']['AluCap']['model_name'][1]: # and (output_dict['pred'] == 'OK')
        if int(pred_lookup) == int(degree):
            OKornot = 'OK'
        else:
            OKornot = 'NG-InversePolarity'
    elif pred_mn == current_app.config['model_setting']['AluCap']['model_name'][2]: # and (output_dict['pred'] == 'OK')
        if int(pred_lookup) == int(capvalue):
            OKornot = 'OK'
        else:
            OKornot = 'NG-WrongOCV'
    # elif (int(ocv_degree)!=int(degree)) and (int(ocv_capvalue)==int(capvalue)):
    #     OKornot = 'NG-InversePolarityinOCV'
    return OKornot

def ElecCap(pred_mn, pred_lookup, degree):
    OKornot = pred_lookup
    if pred_mn == current_app.config['model_setting']['ElecCap']['model_name'][0]:
        OKornot = pred_lookup # Output NG Category
    elif pred_mn == current_app.config['model_setting']['ElecCap']['model_name'][1]: # and (output_dict['pred'] == 'OK')
        if int(pred_lookup) == int(degree):
            OKornot = 'OK'
        else:
            OKornot = 'NG-InversePolarity'
    return OKornot

def m1_color(comp, pred_mn, pred_lookup, capvalue):
    OKornot = pred_lookup
    color_dict = {'1':'Black', '2':'Blue', '3':'White'}
    if capvalue == 'NA':
        if pred_lookup != 'NG':
            OKornot = 'OK'
        else:
            OKornot = pred_lookup # Output NG Category
    else:
        try:
            supposed_color = color_dict[str(capvalue)]
        except:
            supposed_color = 'NoColour'
            current_app.logger.error(f'capacity: {str(capvalue)} of {comp} could not be matched by color_dict')
            print_logger_json('error', f'capacity: {str(capvalue)} of {comp} could not be matched by color_dict')
        if pred_lookup == 'NG':
            OKornot = pred_lookup # Output NG Category
        elif pred_lookup == supposed_color:
            OKornot = 'OK'
        else:
            OKornot = 'NG-WrongColor'
    return OKornot
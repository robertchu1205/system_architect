import io
import re
import base64
import logging
from functions.post_process.convert.util.rule_util import *

GROUP_JSON_PATH = "./src/functions/post_process/convert/group.json"

class handler:
    @staticmethod
    def execute(input):
        model_res    = res2list(input['model_result'])
        convert_res  = model_res.copy()
        group_helper = Group_Config(GROUP_JSON_PATH)
        for res in convert_res:
            if res["model_name"] == input["model_name"]:
                model_config = group_helper.group_config[input['roi_name']][input['model_name']]
                thres_dict  = model_config['Threshold']
                thres_label = model_config['threshold_label']

                for ind_str in thres_dict:
                    score = thres_dict[ind_str]
                    if res["model_output"][int(ind_str)] < score:
                        res["model_label"][int(ind_str)] = thres_label
                break

        input['model_result'] = str(convert_res)
        return input

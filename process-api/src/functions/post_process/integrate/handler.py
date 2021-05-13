import io
import re
import numpy as np
import base64
import logging
from functions.post_process.convert.util.rule_util import *
from collections import OrderedDict

GROUP_JSON_PATH = "./src/functions/post_process/convert/group.json"

def set_sort_order(ans_dict, prior_rule):
    sort_order = {}
    for label in ans_dict.keys():
        if not label in prior_rule["high_priority_label"]:
            sort_order[label] = 0
        else:
            sort_order[label] = len(prior_rule["high_priority_label"]) - \
                                prior_rule["high_priority_label"].index(label)
    return sort_order

class handler:
    @staticmethod
    def execute(input):
        model_res    = res2list(input['model_result'])
        answer_dict  = {}
        group_helper = Group_Config(GROUP_JSON_PATH)
        prior_rule   = group_helper.get_model_priority_rule(input['roi_name'])

        # compute score
        for res in model_res:
            model_id = res["model_name"]
            weight = group_helper.get_model_weight(input['roi_name'], model_id)
            pred_index = np.argmax(res["model_output"])
            pred_label = res["model_label"][pred_index]
            pred_score = 1 * weight
            # pred_score = res["model_output"][pred_index]
            if not pred_label in answer_dict:
                answer_dict[pred_label] = 0
            answer_dict[pred_label] += pred_score

        sort_order = set_sort_order(answer_dict, prior_rule)

        if prior_rule["overwrite_weight"]:
            answer_dict = OrderedDict(sorted(answer_dict.items(),
                key=lambda item: item[1], reverse=True))
            answer_dict = OrderedDict(sorted(answer_dict.items(),
                key=lambda item: sort_order[item[0]], reverse=True))

        else:
            # sort by priority before value
            answer_dict = OrderedDict(sorted(answer_dict.items(),
                key=lambda item: sort_order[item[0]], reverse=True))
            answer_dict = OrderedDict(sorted(answer_dict.items(),
                key=lambda item: item[1], reverse=True))

        # return ans by first_element
        input['ai_result'] = next(iter(answer_dict.keys()))
        input['ai_score']  = next(iter(answer_dict.values()))
        return input

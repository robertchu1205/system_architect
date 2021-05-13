import ast
import json

def order_key(dict):
    return dict["order"]

def res2list(s):
    return ast.literal_eval(s)

class Group_Config(object):
    def __init__(self, group_path):
        self.group_path = group_path
        self.rule_dict = {}
        self.group_config = {}
        self.config_loader()

    def config_loader(self):
        config_file = json.load(open(self.group_path))
        for roi_id in config_file:
            roi_config = config_file[roi_id].copy()
            model_list = roi_config.pop("models")
            self.rule_dict[roi_id] = roi_config
            model_list.sort(key=order_key)
            tmp_config = {}
            for model in model_list:
                model_id = model["name"]
                tmp_config[model_id] = model

            self.group_config[roi_id] = tmp_config

    def get_model_weight(self, roi_id, model_id):
        weight = self.group_config[roi_id][model_id]['weight']
        return weight

    def get_model_priority_rule(self, roi_id):
        priority_rule = self.rule_dict[roi_id]
        return priority_rule

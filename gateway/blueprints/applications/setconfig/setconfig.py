from flask import Blueprint, current_app, jsonify, request, render_template
import yaml

# Blueprint Configuration
config_bp = Blueprint('config_bp', __name__, 
                        static_url_path='config')

data = [
         {'name':'aaa','0Y-5Y':100,'5Y-25Y':50,'total':150}
        ,{'name':'bbb','0Y-5Y':10,'5Y-25Y':125,'total':135}
    ]

@config_bp.route('', methods=['GET', 'POST'])
def set_config():
    # config_dict = {'env_setting': current_app.config['env_setting'], 
    #     'model_setting': current_app.config['model_setting']}
    # return jsonify(config_dict)
    if request.method == 'GET':
        # return render_template('test.html', data=data)
        comps = list(current_app.config['model_setting'].keys())
        try:
            x = current_app.config['test_model_setting']
            return render_template('form_with_test.html', 
                modelsetting=current_app.config['model_setting'], 
                testmodelsetting=current_app.config['test_model_setting'])
        except:
            return render_template('form.html', 
                modelsetting=current_app.config['model_setting'])
    elif request.method == 'POST':
        returned_dict = request.form.to_dict(flat=False)
        # to_return = {}
        for key, value in returned_dict.items():
            if value[0] == "":
                continue
            which_model_setting = key.split('_')[0] # ms, tms
            which_comp = key.split('_')[1] 
            which_model_name = key.split('_')[2]
            if which_model_setting == 'ms':
                index = current_app.config['model_setting'][which_comp]['model_name'].index(which_model_name)
                if type(current_app.config['model_setting'][which_comp]['con_threshold']) != list:
                    new_ct_list = [None for i in range(len(current_app.config['model_setting'][which_comp]['model_name']))]
                    current_app.config['model_setting'][which_comp].update({'con_threshold': new_ct_list})
                try:
                    current_app.config['model_setting'][which_comp]['con_threshold'][index] = float(value[0])
                except:
                    con_threshold = current_app.config['model_setting'][which_comp]['con_threshold']
                    con_threshold.append(float(value[0]))
                    current_app.config['model_setting'][which_comp].update({'con_threshold': con_threshold})
            elif which_model_setting == 'tms':
                index = current_app.config['test_model_setting']['model_setting'][which_comp]['model_name'].index(which_model_name)
                if type(current_app.config['test_model_setting']['model_setting'][which_comp]['con_threshold']) != list:
                    new_ct_list = [None for i in range(len(current_app.config['test_model_setting']['model_setting'][which_comp]['model_name']))]
                    current_app.config['test_model_setting']['model_setting'][which_comp].update({'con_threshold': new_ct_list})
                try:
                    current_app.config['test_model_setting']['model_setting'][which_comp]['con_threshold'][index] = float(value[0])
                except:
                    con_threshold = current_app.config['test_model_setting']['model_setting'][which_comp]['con_threshold']
                    con_threshold.append(float(value[0]))
                    current_app.config['test_model_setting']['model_setting'][which_comp].update({'con_threshold': con_threshold})
            # to_return.update({key: value})
        try:
            config_dict = {
                'env_setting': current_app.config['env_setting'], 
                'model_setting': current_app.config['model_setting'],
                'test_model_setting': current_app.config['test_model_setting'],
            }
        except:
            config_dict = {
                'env_setting': current_app.config['env_setting'], 
                'model_setting': current_app.config['model_setting'],
            }
        with open('/config/config.yaml', 'w') as yaml_file: 
            yaml.dump(config_dict, yaml_file, default_flow_style=False)
        return jsonify(config_dict)
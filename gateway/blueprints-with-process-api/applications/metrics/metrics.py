import prometheus_client
from flask import Blueprint, current_app, jsonify, g
from applications.functions import tf_addr_health
# from applications import prome_dict, REGISTRY

# Blueprint Configuration
metrics_bp = Blueprint('metrics_bp', __name__, 
                        static_url_path='metrics')

@metrics_bp.route('', methods=['GET'])
def show_metrics():
    # result = []
    # for rt in current_app.url_map.iter_rules():
    #     result.append({
    #         "methods": list(rt.methods),
    #         "route": str(rt)
    # })
    # return jsonify({"routes": result, "total": len(result)})
    model_setting = current_app.config['model_setting']
    for comp in model_setting:
        for mn in model_setting[comp]['model_name']:
            base_url = current_app.config['env_setting']['tfserving_rest']
            mn_url = f'http://{base_url}/v1/models/{mn}'
            g.prome_dict['model_health'].labels(mn).set(tf_addr_health(mn_url))
            # if tf_addr_health(mn_url) == 1:
            #     g.prome_dict['model_health'].labels(comp+'-'+mn).state('healthy')
            # elif tf_addr_health(mn_url) == 0:
            #     g.prome_dict['model_health'].labels(comp+'-'+mn).state('error')
    if 'test_model_setting' in current_app.config.keys():
        test_model_setting = current_app.config['test_model_setting']['model_setting']
        for comps in test_model_setting:
            for tmn in test_model_setting[comps]['model_name']:
                base_url = current_app.config['test_model_setting']['tfserving_rest']
                tmn_url = f'http://{base_url}/v1/models/{tmn}'
                g.prome_dict['model_health'].labels(tmn).set(tf_addr_health(tmn_url))
    return prometheus_client.generate_latest(g.REGISTRY)
import os, glob
import prometheus_client
from flask import current_app, g
from applications.functions import print_logger_json

def create_bucket_tuple(maximum=0.6,minimum=1e-4):
    bucket_list = []
    while True:
        if minimum <= maximum:
            bucket_list.append(minimum)
        else:
            break
        minimum*=2
    return tuple(bucket_list)

def init_prometheus_client(REGISTRY):
    prome_dict = {}
    prome_dict['image_counter'] = prometheus_client.Counter(
        'image_counter', 'all inferred images counter by component', 
        ['component', 'pred_class'], registry=REGISTRY)
    # prome_dict['model_health'] = prometheus_client.Enum(
    #     'model_health', 'model_health return post status code', ['model_name'], 
    #     states=['healthy', 'error'], registry=REGISTRY)
    prome_dict['model_health'] = prometheus_client.Gauge(
        'model_health', 'model_health return post status code',
        ['model_name'], registry=REGISTRY)
    prome_dict['sec_perimg_his'] = prometheus_client.Histogram(
        'sec_perimg_Histogram', 'Histogram of time taken quantity per request',
        buckets=create_bucket_tuple(0.6,1e-3),registry=REGISTRY) #loop
    prome_dict['sec_perimg_gau'] = prometheus_client.Gauge(
        'sec_perimg_Gauge', 'Gauge of time taken  quantity per request', 
        registry=REGISTRY) # For every speed on GPU/CPU through grpc/restful
    prome_dict['total_res_img_counter'] = prometheus_client.Counter(
        'total_res_img_counter', 'Total requested/responded images', 
        registry=REGISTRY) # For know how many images processed, knowing efficiency of gateway
    prome_dict['req_counter'] = prometheus_client.Counter(
        'req_counter', 'Count of requests', 
        registry=REGISTRY) # For know how many requests is, knowing efficiency of gateway
    prome_dict['pro_time_counter'] = prometheus_client.Counter(
        'pro_time_counter', 'Count of time taken every request', 
        registry=REGISTRY) # For know how long every request took, knowing efficiency of gateway
    prome_dict['no_infer_img_counter'] = prometheus_client.Counter(
        'no_infer_img_counter', 'Count of total no inferred images', 
        registry=REGISTRY) # For know how many not online components requested
    prome_dict['total_inferred_img_counter'] = prometheus_client.Counter(
        'total_inferred_img_counter', 'Count of total inferred images ignoring kinds of images', 
        registry=REGISTRY) # For know how many images processed
    prome_dict['inferred_img_counter'] = prometheus_client.Counter(
        'inferred_img_counter', 'Count of inferred images with final outcome by model_name', 
        ['model_name'], registry=REGISTRY) # For dividing other metrics such as predicts_duration_secs
    prome_dict['predicts_img_counter'] = prometheus_client.Counter(
        'predicts_img_counter', 'Count of inferred images with preditions by model_name & pred_class', 
        ['model_name', 'pred_class'], registry=REGISTRY) # For dividing other metrics such as confidence_sum
    prome_dict['outline_img_counter'] = prometheus_client.Counter(
        'outline_img_counter', 'outline image counter by model name judged by checkpoints', 
        ['model_name'], registry=REGISTRY)
    prome_dict['predicts_duration_secs'] = prometheus_client.Counter(
        'predicts_duration_secs', 'predicts_duration_secs by each online model',
        ['model_name'], registry=REGISTRY)
    prome_dict['confidence_sum'] = prometheus_client.Counter(
        'confidence_sum', 'sum of confidences by each online model',
        ['model_name', 'pred_class'], registry=REGISTRY)
    prome_dict['inference_version'] = prometheus_client.Gauge(
        'inference_version', 'current inference version by each online model',
        ['model_name'], registry=REGISTRY)
    return prome_dict

def read_checkpoint():
    try:
        checkpoint_dict = {}
        cp_locs = glob.glob('/checkpoint/*.cp')
        for cpl in cp_locs:
            which_model = cpl.split(os.path.sep)[-1].split('.')[0]
            cp_content = open(cpl, 'r').read().split('\n')[0].split('\t')
            checkpoint_dict[which_model] = cp_content
    except:
        return f'Loading checkpoint infos in /checkpoint failed in prometheus.py.'
    return checkpoint_dict

def check_checkpoint(checkpoint_dict, all_dd_list):
    for data in all_dd_list:
        try:
            data_comp = data['component']
            if data_comp not in list(dict(current_app.config['model_setting']).keys()):
                continue
            cp_attribute = f'{data["eagle"]}_{data["location"]}'
            mn_list = current_app.config['model_setting'][data_comp]['model_name'] # to judge
            for mn in mn_list:
                if cp_attribute not in checkpoint_dict[mn]:
                    g.prome_dict['outline_img_counter'].labels(mn).inc()
        except:
            current_app.logger.error(f'check_checkpoint occured error.')
            print_logger_json('error', f'check_checkpoint occured error.')
    # prometheus_client.generate_latest(g.REGISTRY)

# Log
def prometheus_data(secs_taken, data):
    try:
        req_img_count = len(data) # total requested images number
        g.prome_dict['req_counter'].inc()
        g.prome_dict['pro_time_counter'].inc(secs_taken)
        g.prome_dict['sec_perimg_his'].observe(secs_taken/req_img_count)
        g.prome_dict['sec_perimg_gau'].set(secs_taken/req_img_count)
        total_inferred_img = 0 # requested image count in online models 
        for idx, d in enumerate(data):
            if d['component'] in list(dict(current_app.config['model_setting']).keys()): 
                if str(current_app.config['env_setting']['request_post_file']) == 'False':
                    confidence = d['confidence']
                    pred_class = d['pred_class']
                elif str(current_app.config['env_setting']['request_post_file']) == 'True':
                    confidence = d['ai_score']
                    pred_class = d['ai_result']
                if abs(float(confidence)) <= 1.0:
                    g.prome_dict['image_counter'].labels(d['component'], pred_class).inc()
                    mn_list = current_app.config['model_setting'][d['component']]['model_name']
                    for mn in mn_list:
                        g.prome_dict['inferred_img_counter'].labels(mn).inc()
                    total_inferred_img += 1
        g.prome_dict['total_inferred_img_counter'].inc(total_inferred_img)
        g.prome_dict['no_infer_img_counter'].inc(req_img_count - total_inferred_img)
    except Exception as e:
        return f'There is no request content in prometheus_data. Exception: {e}'
    # prometheus_client.generate_latest(g.REGISTRY)
    return True
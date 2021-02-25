from protos.tensorflow_serving.apis import predict_pb2
from protos.tensorflow_serving.apis import prediction_service_pb2
from protos.tensorflow_serving.apis import prediction_service_pb2_grpc
from protos.tensorflow.core.framework import tensor_pb2
from protos.tensorflow.core.framework import tensor_shape_pb2
from protos.tensorflow.core.framework import types_pb2
import numpy as np
import base64, time, grpc, prometheus_client, types
import applications.classify as classify
from applications.functions import calculate_secs_taken, print_logger_json
from flask import current_app, g

# For chunking list of protobuf to small piece which is the same as the final dense of softmax
def chunks(unchunks_list, size_after):
    # For item i in a range that is a length of size_after,
    for i in range(0, len(unchunks_list), size_after):
        # Create an index range for unchunks_list of size_after items:
        yield unchunks_list[i:i+size_after]

# def saiap_coding(img_resized):
#     return base64.urlsafe_b64encode(img_resized)

# def own_coding(img_resized):
#     return img_resized

def for_copy_from(data, dtype='STRING'):
    tensor_shape = list(np.array(data).shape)
    dims = [tensor_shape_pb2.TensorShapeProto.Dim(size=dim) for dim in tensor_shape]
    tensor_shape = tensor_shape_pb2.TensorShapeProto(dim=dims)
    if dtype=='FLOAT':
        tensor = tensor_pb2.TensorProto(
                dtype=types_pb2.DT_FLOAT,
                tensor_shape=tensor_shape,
                float_val=data)
    else:
        tensor = tensor_pb2.TensorProto(
                    dtype=types_pb2.DT_STRING,
                    tensor_shape=tensor_shape,
                    string_val=data)
    return tensor

def grpc_request_server(
    component, img_resized, all_infos, batch_index=None, batch_end=None, if_test_model=True): 
    try:
        # if env_setting['image_format'] == 'b64':
        #     if env_setting['image_coding'] == 'saiap_coding':
        #         coded_img_resized = [saiap_coding(ir) for ir in img_resized]
        #     elif env_setting['image_coding'] == 'own_coding':
        #         coded_img_resized = [own_coding(ir) for ir in img_resized]
        #     else:
        #         current_app.logger.error(f'image_coding in env_setting of config.json not supported!')
        #         print_logger_json('error', f'image_coding in env_setting of config.json not supported!')
        #         return None
        if if_test_model:
            component_dict = model_setting[component]
            model_spec_name = component_dict['model_name'] 
            # got a list of types of model for this comp
            data_type = component_dict['data_type'] 
            # got a list of lookup tables of these models for this comp
            version_label = component_dict['version_label']
            model_url = env_setting['tfserving_grpc']
            model_input_name = env_setting['model_input_name']
        else:
            component_dict = own_model_setting['model_setting'][component]
            model_spec_name = component_dict['model_name']
            data_type = component_dict['data_type']
            version_label = component_dict['version_label']
            model_url = own_model_setting['tfserving_grpc']
            model_input_name = component_dict['model_input_name']
        pred_softmax = {}
        for idx, msn in enumerate(model_spec_name):
            # Final dense of model, to divide the prediciton to dense length, return softmax
            if len(env_setting['model_output_name']) == 1:
                pred_dense = len(data_type[idx]) 
            try: 
                ini_time = time.time()
                try:
                    try:
                        channel = grpc.insecure_channel(component_dict['specific_url'][idx])
                    except:    
                        channel = grpc.insecure_channel(model_url)
                    stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)
                    request = predict_pb2.PredictRequest()
                    request.model_spec.signature_name = env_setting['signature_name']  # signature name
                    request.model_spec.name = msn  # model name
                    if isinstance(version_label, list) and version_label[idx] != None:
                        try:
                            model_version = int(version_label[idx])
                            request.model_spec.version.value = model_version
                        except:
                            request.model_spec.version_label = version_label[idx]
                        # comp_count = coded_img_resized.shape[0]
                        # request.inputs[model_input_name].CopyFrom(
                        #     tf.make_tensor_proto(img_resized, dtype=tf.float32))
                        # request.inputs[model_input_name].CopyFrom(
                        #     tf.make_tensor_proto(coded_img_resized, shape=[comp_count]))
                    for i, mi in enumerate(model_input_name):
                        if i == 0:
                            if env_setting['image_format'] == 'array':
                                request.inputs[mi].CopyFrom(for_copy_from(img_resized), 'FLOAT')
                            elif env_setting['image_format'] == 'b64':
                                request.inputs[mi].CopyFrom(for_copy_from(img_resized))
                        else:
                            if (batch_index == None) and (batch_end == None):
                                request.inputs[mi].CopyFrom(for_copy_from([ai.encode("utf-8") for ai in all_infos[mi]]))
                            else:
                                request.inputs[mi].CopyFrom(for_copy_from([ai.encode("utf-8") for ai in all_infos[mi][batch_index:batch_end]]))
                    # Faster?
                    result_future = stub.Predict.future(request, time_out)
                    response = result_future.result()
                except Exception as e:
                    current_app.logger.error(f'request {msn} with {str(version_label[idx])} failed. message: {e}')
                    print_logger_json('error', f'request {msn} with {str(version_label[idx])} failed. message: {e}')
                    try:
                        channel = grpc.insecure_channel(component_dict['specific_url'][idx])
                    except:    
                        channel = grpc.insecure_channel(model_url)
                    stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)
                    request = predict_pb2.PredictRequest()
                    request.model_spec.signature_name = env_setting['signature_name']  # signature name
                    request.model_spec.name = msn  # model name
                    for i, mi in enumerate(model_input_name):
                        if i == 0:
                            if env_setting['image_format'] == 'array':
                                request.inputs[mi].CopyFrom(for_copy_from(img_resized), 'FLOAT')
                            elif env_setting['image_format'] == 'b64':
                                request.inputs[mi].CopyFrom(for_copy_from(img_resized))
                        else:
                            if (batch_index == None) and (batch_end == None):
                                request.inputs[mi].CopyFrom(for_copy_from([ai.encode("utf-8") for ai in all_infos[mi]]))
                            else:
                                request.inputs[mi].CopyFrom(for_copy_from([ai.encode("utf-8") for ai in all_infos[mi][batch_index:batch_end]]))
                    result_future = stub.Predict.future(request, time_out)
                    response = result_future.result()
                g.prome_dict['predicts_duration_secs'].labels(
                        msn).inc(calculate_secs_taken(ini_time))
                g.prome_dict['inference_version'].labels(
                        msn).set(response.model_spec.version.value)
                # response = stub.Predict(request, time_out)
                if (batch_index == None) and (batch_end == None):
                    if len(env_setting['model_output_name']) == 1:
                        pred_softmax[msn] = list(response.outputs[env_setting['model_output_name'][0]].float_val)
                    else:
                        pred_dict = {}
                        for mo in env_setting['model_output_name']:
                            if mo == 'confidence':
                                pred_dict[mo] = list(response.outputs[mo].float_val)[0]
                            else:
                                pred_dict[mo] = list(response.outputs[mo].string_val)[0].decode()
                        pred_softmax[msn] = pred_dict
                else:
                    if len(env_setting['model_output_name']) == 1:
                        res_chunked_ary = list(chunks(
                            np.array(response.outputs[env_setting['model_output_name'][0]].float_val).tolist(), 
                            pred_dense))
                        pred_softmax[msn] = res_chunked_ary
                    else:
                        pred_dict = {}
                        for mo in env_setting['model_output_name']:
                            if mo == 'confidence':
                                pred_dict[mo] = [sv for sv in list(response.outputs[mo].float_val)]
                            else:
                                pred_dict[mo] = [sv.decode()for sv in list(response.outputs[mo].string_val)]
                        pred_softmax[msn] = pred_dict
                # print(response.outputs[env_setting['model_output_name']].float_val) 
                # all prediction are in the protobuf, len will be batch_size * classification categories
                # print(type(response.outputs[env_setting['model_output_name']].float_val)) 
                # <class 'google.protobuf.pyext._message.RepeatedScalarContainer'> 
            except Exception as e:
                current_app.logger.error(f'request {msn} failed. message: {e}')
                print_logger_json('error', f'request {msn} failed. message: {e}')
                if (batch_index == None) and (batch_end == None):
                    pred_softmax[msn] = ['None']
                else:
                    pred_softmax[msn] = [['None'] for _ in range(len(img_resized))]
        # own model inference
        try:
            if if_test_model and own_model_setting!={}:
                if own_model_setting['outcome_choice']=='consider' or own_model_setting['outcome_choice']=='background':
                    for oms_comps in list(dict(own_model_setting['model_setting']).keys()):
                        for oc in oms_comps.split('/'):
                            if oc == component:
                                own_outcome_dict = grpc_request_server(
                                    oms_comps, img_resized, all_infos, batch_index, batch_end, if_test_model=False)
                                for oo_key in list(dict(own_outcome_dict).keys()):
                                    pred_softmax[oo_key] = own_outcome_dict[oo_key]
        except Exception as e:
            current_app.logger.error(f'Request TEST TF gRPC server error. message: {e}')
            print_logger_json('error', f'Request TEST TF gRPC server error. message: {e}')    
        return pred_softmax
    except Exception as e:
        current_app.logger.error(f'Request TF gRPC server error. message: {e}')
        print_logger_json('error', f'Request TF gRPC server error. message: {e}')
        return None

def img_format_array(softmax_ary, ImgBatchByComp, oms):
    # comp_fullname = list(dict(model_setting).keys())
    global time_out, own_model_setting, env_setting, model_setting
    env_setting = current_app.config['env_setting']
    model_setting = current_app.config['model_setting']
    own_model_setting = oms
    for comp in ImgBatchByComp:
        # if comp in comp_fullname: 
        if len(ImgBatchByComp[comp]['putback_idx'])==0:
            continue
        elif len(ImgBatchByComp[comp]['putback_idx'])==1: 
            time_out = 0.5 * np.array(ImgBatchByComp[comp]['image']).shape[0] 
            # expand_dims cos it's only one
            pred_softmax = grpc_request_server( 
                comp, np.array(ImgBatchByComp[comp]['image'], dtype=np.float32), ImgBatchByComp[comp])
            if pred_softmax is None:
                return None
            this_infos = {}
            for k in ImgBatchByComp[comp].keys():
                if k != 'image':
                    this_infos[k] = ImgBatchByComp[comp][k][0]
            softmax_ary[ImgBatchByComp[comp]['putback_idx'][0]] = classify.main(
                comp, pred_softmax, own_model_setting, this_infos)
        else:
            batch_index = 0 
            Flag = True
            batch_count = 0
            while Flag:
                Flag = True
                batch_end = batch_index + env_setting['grpc_batch']
                if batch_end >= len(ImgBatchByComp[comp]['image']):
                    batch_end = batch_index + len(ImgBatchByComp[comp]['image'])- \
                                (env_setting['grpc_batch'] * batch_count)
                    Flag = False
                time_out = 0.5 * np.array(ImgBatchByComp[comp]['image'][batch_index:batch_end]).shape[0] 
                pred_softmax = grpc_request_server( 
                    comp, np.array(ImgBatchByComp[comp]['image'][batch_index:batch_end], dtype=np.float32), 
                    ImgBatchByComp[comp], batch_index, batch_end)
                if pred_softmax is None:
                    return None
                for img_count, putback_idx in enumerate(ImgBatchByComp[comp]['putback_idx'][batch_index:batch_end]):
                    each_pred_softmax = {k:pred_softmax[k][img_count] 
                                            for k in list(dict(pred_softmax).keys())}
                    this_infos = {}
                    for k in ImgBatchByComp[comp].keys():
                        if k != 'image':
                            this_infos[k] = ImgBatchByComp[comp][k][img_count]
                    softmax_ary[putback_idx] = classify.main(
                        comp, each_pred_softmax, own_model_setting, this_infos)
                batch_count+=1
                batch_index+=env_setting['grpc_batch']
    return softmax_ary

def img_format_b64(softmax_ary, ImgBatchByComp, oms):
    # comp_fullname = list(dict(model_setting).keys())
    global time_out, own_model_setting, env_setting, model_setting
    env_setting = current_app.config['env_setting']
    model_setting = current_app.config['model_setting']
    own_model_setting = oms
    for comp in ImgBatchByComp:
        # logging.warning(comp) # 'AluCap','ElecCap'
        if len(ImgBatchByComp[comp]['putback_idx'])==0:
            continue
        elif len(ImgBatchByComp[comp]['putback_idx'])==1: # Only one in this comp
            time_out = 0.5 * len(ImgBatchByComp[comp]['image'])
            pred_softmax = grpc_request_server( 
                comp, ImgBatchByComp[comp]['image'], ImgBatchByComp[comp])
            if pred_softmax is None:
                return None
            this_infos = {}
            for k in ImgBatchByComp[comp].keys():
                if k != 'image':
                    this_infos[k] = ImgBatchByComp[comp][k][0]
            softmax_ary[ImgBatchByComp[comp]['putback_idx'][0]] = classify.main(
                comp, pred_softmax, own_model_setting, this_infos)
        else: # More than one counts in this comp
        # batch index for handling predict over 3000 images in grpc
            batch_index = 0 
            Flag = True
            batch_count = 0
            while Flag:
                batch_end = batch_index + env_setting['grpc_batch']
                if batch_end >= len(ImgBatchByComp[comp]['image']):
                    batch_end = batch_index + len(ImgBatchByComp[comp]['image'])- \
                                (env_setting['grpc_batch'] * batch_count)
                    Flag = False
                time_out = 0.5 * len(ImgBatchByComp[comp]['image'][batch_index:batch_end])
                pred_softmax = grpc_request_server( 
                    comp, ImgBatchByComp[comp]['image'][batch_index:batch_end], 
                    ImgBatchByComp[comp], batch_index, batch_end)
                if pred_softmax is None:
                    return None
                for img_count, putback_idx in enumerate(
                    ImgBatchByComp[comp]['putback_idx'][batch_index:batch_end]):
                    if len(env_setting['model_output_name']) == 1:
                        each_pred_softmax = {k:pred_softmax[k][img_count] 
                                            for k in list(dict(pred_softmax).keys())}
                    else:
                        each_pred_softmax = {}
                        for k in list(dict(pred_softmax).keys()):
                            pred_dict = {}
                            for mo in env_setting['model_output_name']:
                                pred_dict[mo] = pred_softmax[k][mo][img_count]
                            each_pred_softmax[k] = pred_dict
                    this_infos = {}
                    for k in ImgBatchByComp[comp].keys():
                        if k != 'image':
                            this_infos[k] = ImgBatchByComp[comp][k][img_count]
                    softmax_ary[putback_idx] = classify.main(
                        comp, each_pred_softmax, own_model_setting, this_infos)
                batch_count+=1
                batch_index+=env_setting['grpc_batch']
    return softmax_ary
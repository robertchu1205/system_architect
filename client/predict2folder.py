import os
import glob
import time
import grpc
import tensorflow as tf
# from PIL import Image
import numpy as np
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc
import argparse
import base64
import io
from shutil import copyfile
import re

BATCH_SIZE = 300
index_dict={ 
    "0" : "0-270",
    "1" : "0-820",
    "2" : "270-270",
    "3" : "270-820" }

# TFSERVER_URL_GRPC = {host address}:{port for grpc}
parser = argparse.ArgumentParser(description="link & image amount")
parser.add_argument("-l", "--link", dest="TFSERVER_URL", help="link of tfserving")
parser.add_argument("-p", "--RE_PATTERN", dest="RE_PATTERN", help="RE_PATTERN to glob")
parser.add_argument("-d", "--destination_path", dest="D_PATH", help="D_PATH ends with /")
parser.add_argument("-n", "--model_name", dest="MODEL_NAME", help="MODEL_NAME")
args = parser.parse_args()
RE_PATTERN = args.RE_PATTERN
TFSERVER_URL = args.TFSERVER_URL
# images in the assigned directory less than Batch size below would use all the images
D_PATH = args.D_PATH
MODEL_NAME = args.MODEL_NAME

def open_image(filename):
    with open(filename, "rb") as f:
        image = f.read()
        image = base64.b64encode(image).decode("utf-8") # base64 string
        image = image.encode()
        image = base64.decodebytes(image)
        image = base64.urlsafe_b64encode(image)
        # ff = io.BytesIO(base64.b64decode(image))
        # img = Image.open(ff)
        # img = img.resize((96, 96), Image.NEAREST)
        # buffered = io.BytesIO()
        # img.save(buffered, format="PNG")
        # image = base64.urlsafe_b64encode(buffered.getvalue())
    return image

def generate_angle(f): #get angle info from file name
    x=f.split('/')[-2].split('-')[0].split('e')[-1]
    try:
        s = int(x)
    except ValueError:
        x = '0' #not all images includes angle
    return x

def predict2result(image_data, link, model_name, index_dict):
    # setup grpc channel
    channel = grpc.insecure_channel(link)
    stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)
    request = predict_pb2.PredictRequest()
    request.model_spec.name = model_name
    request.model_spec.signature_name = "classification"
    request.inputs["string_array"].CopyFrom(
        tf.compat.v1.make_tensor_proto(image_data, shape=[len(image_data)])
        # tf.contrib.util.make_tensor_proto(image_data, shape=[len(image_data)])
    )
    response = stub.Predict(request, 5.0) # 5 secs timeout
    results = {}
    for key in response.outputs:
        tensor_proto = response.outputs[key]
        results[key] = tf.make_ndarray(tensor_proto)
    return results[key]


if __name__ == "__main__":
    filenames = []
    # for root, dirs, files in os.walk(IMAGE_PATH):
    #    for img_file in files:
    #         if img_file.endswith('.png'):
    #            filenames.append(os.path.join(root, img_file))
    #         if img_file.endswith('.bmp'):
    #            filenames.append(os.path.join(root, img_file))
    # regex = re.compile('/data/AIimg2020/.+/AluCap/.+\\-2/OK/.+png') # OK
    # regex = re.compile('/data/AIimg2020/.+/AluCap/.+/AluCap/.+/.+png')
    # regex = re.compile('/data/AIimg2020/.+/AluCapacitor/.+\\-2/OK/.+png') # OK

    # regex = re.compile('/data/AIimg2020/.+/AluCap/.+\\-2/TimeOut/.+png') # TimeOut
    rootdir = '/data/'
    regex = re.compile(RE_PATTERN)
    for root, dirs, files in os.walk(rootdir):
        for f in files:
            whole_fn = os.path.join(root,f)
            if regex.match(whole_fn):
                filenames.append(whole_fn)   
    for iINd in index_dict:
        if not os.path.exists(D_PATH+index_dict[iINd]):
            os.makedirs(D_PATH+index_dict[iINd])
    count = 0
    while count<len(filenames):
        image_data = [open_image(f) for f in filenames[count:count+BATCH_SIZE]]
        resultskey = predict2result(image_data, TFSERVER_URL, MODEL_NAME, index_dict)
        pred_folder = ""
        # print(resultskey)
        if count+BATCH_SIZE>len(filenames):
            print("finalone")
            for index_batch in range((len(filenames)%BATCH_SIZE)):
                pred_folder = index_dict[str(np.argmax(resultskey[index_batch]))]
                # print(pred_folder)
                copyfile(filenames[count+index_batch], D_PATH+pred_folder+'/'+filenames[count+index_batch].split('/')[-1])
        else:
            for index_batch in range(BATCH_SIZE):
                pred_folder = index_dict[str(np.argmax(resultskey[index_batch]))]
                # print(pred_folder)
                copyfile(filenames[count+index_batch], D_PATH+pred_folder+'/'+filenames[count+index_batch].split('/')[-1])
        count+=BATCH_SIZE



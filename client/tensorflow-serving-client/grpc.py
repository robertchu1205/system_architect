import os, grpc, argparse, base64, io, sys, time
import grpc
import tensorflow as tf
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc
import numpy as np
# import cv2

ini_sec = time.time()
image_width = 224
# TFSERVER_URL_GRPC = {host address}:{port for grpc}
# For example: 10.41.65.77:8590
parser = argparse.ArgumentParser(description='link & image amount')
parser.add_argument('-l', '--link', dest='TFSERVER_URL', help='link of tfserving')
parser.add_argument('-i', '--image_path', dest='IMAGE_PATH', help='IMAGE_PATH')
parser.add_argument('-b', '--batch_size', dest='BATCH_SIZE', help='BATCH_SIZE')
parser.add_argument('-n', '--model_name', dest='MODEL_NAME', help='MODEL_NAME')
parser.add_argument('-m', '--mode', default='saiap', dest='MODE', help='saiap OR normal OR image')
parser.add_argument('-s', '--signature', default='classification', dest='SIG', help='Default classification')
args = parser.parse_args()
IMAGE_PATH = args.IMAGE_PATH
TFSERVER_URL = args.TFSERVER_URL
BATCH_SIZE = args.BATCH_SIZE
MODEL_NAME = args.MODEL_NAME
MODE = args.MODE
SIG = args.SIG
# images in the assigned directory less than Batch size below would use all the images

# grpc method would serialize image input automatically
# def image_array(filename):
#     img = cv2.imread(filename)
#     roi_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#     # img_height, img_width = model.layers[0].input_shape[1:3]
#     pltimg = cv2.resize(roi_img, (image_width, image_width))
#     imlist = np.array(pltimg,dtype=np.float32)/255
#     imlist = imlist.tolist()

#     # img = Image.open(filename)
#     # img = img.resize((image_width, image_width), Image.BILINEAR)
#     # img = np.array(img, dtype=np.float32).tolist()
#     return imlist

def open_image(filename):
    with open(filename, 'rb') as f:
        image = f.read() # without decode_base64
    return image

def saiap_open_image(filename):
    image = open(filename, 'rb').read()
    image = base64.urlsafe_b64encode(image)
    return image

def generate_angle(f): #get angle info from file name
    x=f.split('/')[-2].split('-')[0].split('e')[-1]
    try:
        s = int(x)
    except ValueError:
        x = '0' #not all images includes angle
    return x

if __name__ == '__main__':
    filenames = []
    for root, dirs, files in os.walk(IMAGE_PATH):
       for img_file in files:
            if img_file.endswith('.png'):
               filenames.append(os.path.join(root, img_file))
            if img_file.endswith('.bmp'):
               filenames.append(os.path.join(root, img_file))
            if img_file.endswith('.jpg'):
               filenames.append(os.path.join(root, img_file))
    filenames = filenames[:int(BATCH_SIZE)]
    for f in filenames:
        print(f)
    # put required data in 
    degree_data = ['0' for f in filenames]
    if MODE == 'normal':
        image_data = [open_image(f) for f in filenames]
    elif MODE == 'image':
        image_data = [image_array(f) for f in filenames]
        if len(image_data) > 1:
            image_data = np.array(image_data[0:len(image_data)], dtype=np.float32)
        else:
            image_data = np.array(image_data, dtype=np.float32)
    elif MODE == 'saiap':
        image_data = [saiap_open_image(f) for f in filenames]
    else:
        sys.exit('args "-m" is typed wrong. it needs to be normal or saiap or image')
    # setup grpc channel
    channel = grpc.insecure_channel(TFSERVER_URL)
    stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)
    request = predict_pb2.PredictRequest()
    # names below is default, so it needs to change if defination is different
    # Default
    # request.model_spec.name = 'model'
    # request.model_spec.signature_name = 'serving_default'
    # SAIAP
    # request.model_spec.version_label='stable'
    # request.model_spec.version.value=1595841209
    request.model_spec.name = MODEL_NAME
    request.model_spec.signature_name = SIG
    # pass all the necessary images below
    if MODE == 'normal':
        request.inputs['image'].CopyFrom(
            tf.make_tensor_proto(image_data, shape=[len(image_data)])
            # tf.contrib.util.make_tensor_proto(image_data, shape=[len(image_data)])
        )
        request.inputs['degree'].CopyFrom(
            tf.make_tensor_proto(degree_data, shape=[len(degree_data)])
        )
        request.inputs['capacity'].CopyFrom(
            tf.make_tensor_proto(degree_data, shape=[len(degree_data)])
        )
        request.inputs['component'].CopyFrom(
            tf.make_tensor_proto(degree_data, shape=[len(degree_data)])
        )
        request.inputs['SN'].CopyFrom(
            tf.make_tensor_proto(degree_data, shape=[len(degree_data)])
        )
        request.inputs['voltage'].CopyFrom(
            tf.make_tensor_proto(degree_data, shape=[len(degree_data)])
        )
    elif MODE == 'saiap':
        request.inputs['string_array'].CopyFrom(
            tf.make_tensor_proto(image_data, shape=[len(image_data)])
            # tf.contrib.util.make_tensor_proto(image_data, shape=[len(image_data)])
        )
    elif MODE == 'image':
        request.inputs['input_1'].CopyFrom(
            tf.make_tensor_proto(image_data, dtype=tf.float32)
            # tf.contrib.util.make_tensor_proto(image_data, shape=[len(image_data)])
        )
    # response = stub.Predict(request, 5.0) # 5 secs timeout

    #Faster?
    result_future = stub.Predict.future(request, 1)  # 10 secs timeout
    result = result_future.result()

    # outputs = response.outputs['combined_outcome'].string_val -> also works
    
    results = {}
    for key in result.outputs:
        tensor_proto = result.outputs[key]
        results[key] = tf.make_ndarray(tensor_proto)
    print(results)

    sec_taken = time.time() - ini_sec
    print(f'client request to receive:{sec_taken} secs')
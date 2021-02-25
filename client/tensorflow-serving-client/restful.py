import os, requests, argparse
import json, base64, sys, time
# import cv2
import numpy as np
ini_sec = time.time()

parser = argparse.ArgumentParser(description='link & image amount')
parser.add_argument('-l', '--link', dest='TFSERVER_URL', help='link of tfserving')
parser.add_argument('-i', '--image_path', dest='IMAGE_PATH', help='IMAGE_PATH')
parser.add_argument('-b', '--batch_size', dest='BATCH_SIZE', help='BATCH_SIZE, all for test below dir')
parser.add_argument('-n', '--model_name', dest='MODEL_NAME', help='MODEL_NAME')
parser.add_argument('-m', '--mode', dest='MODE', help='saiap OR normal or image')
parser.add_argument('-a', '--answer', dest='ANSWER', help='current ANSWER to test')
parser.add_argument('-s', '--signature', default='serving_default', dest='SIG', help='Default classification')
parser.add_argument('-o', '--origin_index', default='0', dest='origin_index', help='all starts from')
args = parser.parse_args()
IMAGE_PATH = args.IMAGE_PATH
TFSERVER_URL = args.TFSERVER_URL
BATCH_SIZE = args.BATCH_SIZE
MODEL_NAME = args.MODEL_NAME
MODE = args.MODE
SIG = args.SIG
origin_index = args.origin_index
ANSWER = args.ANSWER
url = f'http://{TFSERVER_URL}/v1/models/{MODEL_NAME}:predict'
# url = f'http://{TFSERVER_URL}/v1/models/{MODEL_NAME}/versions/1595841209:predict'
# url = f'http://{TFSERVER_URL}/v1/models/{MODEL_NAME}/labels/latest:predict' # tf2.3 serving WORKs

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

def open_and_serialize_image(filename):
    with open(filename, 'rb') as f:
        image = f.read()
    return base64.b64encode(image).decode('utf-8')

def saiap_open_image(filename):
    image = open(filename, 'rb').read() 
    image = base64.urlsafe_b64encode(image)
    #     # ff = io.BytesIO(base64.b64decode(image))
    #     # img = Image.open(ff)
    #     # img = img.resize((96, 96), Image.NEAREST)
    #     # buffered = io.BytesIO()
    #     # img.save(buffered, format='PNG')
    #     # image = base64.urlsafe_b64encode(buffered.getvalue())
    # return image.decode() # without 'b64' in instances
    return base64.b64encode(image).decode('utf-8')

def generate_angle(f): #get angle info from file name
    x=f.split('/')[-2].split('-')[0].split('e')[-1]
    try:
        s = int(x)
    except ValueError: #not all images includes angle
        x = '0'
    return x

def rotate_degree(path, degree=90):
    rotated = str((int(path.split('_')[2])+degree)%360)
    if len(rotated) == 1:
        rotated = '00' + rotated
    elif len(rotated) == 2:
        rotated = '0' + rotated
    return rotated

def to_instances(MODE, filenames):
    if MODE == 'normal':
        instances = [{
                'image': {'b64': open_and_serialize_image(f)}, 
                'degree': f.split('_')[2], 
                'capacity': f.split('_')[3],
                'component': f.split('_')[1],
                'voltage': f.split('_')[4],
                'SN': f.split('_')[0]
            }
            for f in filenames
        ] 
    elif MODE == 'saiap':
        instances = [{
            'string_array': {'b64': saiap_open_image(f)}, } 
            for f in filenames
        ] 
        # instances = [{'string_array': saiap_open_image(f)}]
    elif MODE == 'image':
        instances = [{
            'input_1': image_array(f), } 
            for f in filenames
        ] 
    else:
        sys.exit('args "-m" is typed wrong. it needs to be normal or saiap')
    return instances

def payload_request(MODE, SIG, filenames):
    # for idx, f in enumerate(filenames):
        # print(idx, f)
        # print(rotate_degree(f))
    payload = {'signature_name':SIG, 'instances':to_instances(MODE, filenames)}
    data = json.dumps(payload)
    # print(data)
    # with open('/tf/robertnb/test-data.json', 'w') as f:
    #     json.dump(payload, f)

    response = requests.post(url, data=data)
    print('response ok: {}'.format(response.ok))
    # print('outputs: {}'.format(response.text))
    # inputs = [np.asarray(Image.open(f)) for f in filenames]
    outputs = response.json()['predictions']
    print("predictions")
    if BATCH_SIZE=='all':
        for idx, o in enumerate(outputs):
            # if o['pred_class']!=filenames[idx].split(os.path.sep)[-2]:
            if o['pred_class']!=ANSWER:
                print(filenames[idx])
                print(o)
    else: 
        for idx, o in enumerate(outputs):
            print(filenames[idx])
            print(o)
    sec_taken = time.time() - ini_sec
    print(f'client request to receive:{sec_taken} secs')

if __name__ == '__main__':
    filenames = []
    for root, dirs, files in os.walk(IMAGE_PATH):
       for img_file in files:
            if img_file.endswith('.jpg') or img_file.endswith('.png') or img_file.endswith('.bmp'):
               filenames.append(os.path.join(root, img_file))
    if BATCH_SIZE=='all':
        batch = 50
        total_num = len(filenames)
        pointer = int(origin_index)
        while pointer<=total_num:
            if pointer+batch>total_num:
                print(pointer, total_num)
                tojudge = filenames[int(pointer):int(total_num)]
            else:
                print(pointer, pointer+batch)
                tojudge = filenames[int(pointer):int(pointer+batch)]
            payload_request(MODE, SIG, tojudge)    
            pointer+=50
        # filenames = filenames[:int(BATCH_SIZE)]
    else:
        filenames = filenames[:int(BATCH_SIZE)]
        payload_request(MODE, SIG, filenames)
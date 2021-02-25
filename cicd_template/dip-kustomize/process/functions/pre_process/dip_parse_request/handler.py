# ( input: data, project, tfs_method, request_method, image_format, image_coding; 
# output: all_dd_list with image which could be used by serving )
import numpy as np
from PIL import Image
import base64, io, os, json
import cv2

def saiap_image_array(b64img):
    # b64img = base64.b64decode(b64img)
    f = io.BytesIO(b64img)
    img = Image.open(f)
    after_resize = img.resize((int(env_setting['image_input_width']), int(env_setting['image_input_height'])), Image.BILINEAR)
    # buffered = io.BytesIO()
    # after_resize.save(buffered, format="PNG")
    # b64urlsafeimg = base64.urlsafe_b64encode(buffered.getvalue())
    npimg = np.array(after_resize, dtype=np.float32).tolist()
    return npimg

def oneai_image_array_postdata(readed_img):
    # img = cv2.imread(filename)
    b_readed_img = bytearray(readed_img)
    numpyarray = np.asarray(b_readed_img, dtype=np.uint8)
    bgrImage = cv2.imdecode(numpyarray, cv2.IMREAD_UNCHANGED)
    roi_img = cv2.cvtColor(bgrImage, cv2.COLOR_BGR2RGB)
    # img_height, img_width = model.layers[0].input_shape[1:3]
    pltimg = cv2.resize(roi_img, (int(env_setting['image_input_height']), int(env_setting['image_input_width'])))
    imlist = np.array(pltimg,dtype=np.float32)/255
    imlist = imlist.tolist()
    return imlist

def oneai_image_array(b64img):
    # img = cv2.imread(filename)
    imgString = base64.b64decode(b64img)
    nparr = np.fromstring(imgString,np.uint8)  
    img = cv2.imdecode(nparr,cv2.IMREAD_COLOR)
    roi_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # img_height, img_width = model.layers[0].input_shape[1:3]
    pltimg = cv2.resize(roi_img, (int(env_setting['image_input_height']), int(env_setting['image_input_width'])))
    imlist = np.array(pltimg,dtype=np.float32)/255
    imlist = imlist.tolist()
    return imlist


def image_b64_coding(b64_image):
    try:
        if env_setting['image_format'] == 'array':
            if env_setting['image_coding'] == 'oneai_image_array':
                image = oneai_image_array(b64_image)
            elif env_setting['image_coding'] == 'oneai_image_array_postdata':
                image = oneai_image_array_postdata(b64_image)
            elif env_setting['image_coding'] == 'saiap_image_array':
                image = saiap_image_array(b64_image)
            else:
                return f'ERROR: image_coding in env_setting not supported!'
        elif env_setting['image_format'] == 'b64':
            if env_setting['image_coding'] == 'saiap_coding':
                b64_image = base64.decodebytes(b64_image.encode()) # b64 string to image byte
                image = base64.urlsafe_b64encode(b64_image)
                if env_setting['tfs_method'] == 'rest':
                    image = base64.b64encode(image).decode('utf-8')
                elif env_setting['tfs_method'] == 'grpc':
                    image = image.decode('latin-1')
            elif env_setting['image_coding'] == 'b64_coding':
                if env_setting['tfs_method'] == 'rest':
                    image = b64_image
                elif env_setting['tfs_method'] == 'grpc':
                    image = base64.decodebytes(b64_image.encode()).decode('latin-1') # image byte to b64 string
            else:
                return f'ERROR: image_coding in env_setting not supported!'
        else:
            return f'ERROR: image_format in env_setting not supported!'
        return image
    except Exception as e:
        return f'ERROR: {e}'

def file_in_body_request(request):
    try:
        if (not request) or ('instances' not in request):
            return (False, 'instances not in request.json')
        data = request
        for idx, d in enumerate(data['instances']):
            data_dict = {
                'logger'  : 'predict', 
                'severity': 'debug', 
                'project' : str(env_setting['project_code']),
            }
            for index, (key, value) in enumerate(dict(d).items()):
                if key == 'eagle':
                    data_dict.update({key: value.replace('_', '')})
                # elif key == 'SN':
                #     data_dict.update({'PanelNo': value.split('_')[0]})
                #     data_dict.update({'location': value.split('_')[-1]})
                elif key == 'capvalue':
                    data_dict.update({'capacity': value})
                elif key == 'image':
                    data_dict.update({'saved_image': value['b64']})
                    image = image_b64_coding(value['b64'])
                    if (type(image) == str) and (image[0:5] == 'ERROR'):
                        return (False, image)
                    else:
                        data_dict.update({'image': image})
                else:
                    data_dict.update({key: value})
            if data_dict['component'] not in list(dict(model_setting).keys()):
                data_dict.update({'severity': 'info'})
            all_dd_list.append(data_dict)
    except Exception as e:
        return (False, e)
    return (True, all_dd_list)

class handler:
    @staticmethod
    def execute(input): # keys: request, env_setting, model_setting
        if 'error' in input.keys():
            return input
        global model_setting, env_setting, all_dd_list
        all_dd_list = []
        # input = json.loads(input)
        env_setting = input['env_setting']
        model_setting = input['model_setting']
        (error_exists, parsed) = file_in_body_request(input['request'])
        if error_exists:
            input['request'] = parsed
        else:
            input['error'] = parsed
        return input
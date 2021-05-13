import base64
import re
import io
from PIL import Image

import numpy as np
import pandas as pd
from  functions.pre_process.region_of_interest.util.lala import OneAIRegionOfInterest
from  functions.pre_process.region_of_interest.util.lala import OneAIImageProcessing

class handler:
    def execute(input):
        kb_model, file_name = input['kb_model'], input['file_name']
        
        #################
        # Define output #
        #################
        input['image_roi'] = None
        input['x1'] = None
        input['x2'] = None
        input['y1'] = None
        input['y2'] = None
        input['central_crop_height'] = None
        input['central_crop_width'] = None
        
        ###########################
        # Decode image - method 1 #
        ###########################
        image = input['image']
        # image = re.sub('^data:image/.+;base64,', '', image)
        # image = Image.open(io.BytesIO(base64.b64decode(image)))

        # # JpegImageFile to array
        # image = np.array(image)
        
        ###########################
        # Decode image - method 2 #
        ###########################
        np_bytes = base64.b64decode(image.encode("UTF-8"))
        tmp_io = io.BytesIO(np_bytes)
        image = np.load(tmp_io)

        #####################
        # ROI mapping table #
        #####################
        mapping_table = pd.read_csv('./src/functions/pre_process/region_of_interest/ROI.csv')

        ######################
        # Region Of Interest #
        ######################
        roi = OneAIRegionOfInterest()
        
        # Get mapping table
        roi.read_mapping_table(mapping_table)
        roi.set_default()
        roi.check_dtype()

        # Mapping kb_model & file_name
        roi.mapping(kb_model, file_name)
        print('Mapping result: %s > Reason: %s\n' %(roi.mapping_result, roi.reason))

        if roi.index is not None:
            print(roi.mapping_table.loc[roi.index])

        if roi.mapping_result:
            # Image Processing
            imgp = OneAIImageProcessing()
            # Get image
            imgp.read(image)
            print('\nOriginal image size ...', imgp.image.shape)

            # Cut with coordinate
            imgp.cut_with_coordinate(roi.coordinate.x1, roi.coordinate.y1, roi.coordinate.x2, roi.coordinate.y2)
            print('Cut with coordinate ...', imgp.image.shape)
            # cv2.imwrite('./cut_with_coordinate.jpg', imgp.image)
            
            # Rotating
            if roi.angle != 0:
                imgp.rotating(roi.angle)
                print('Rotating            ...', imgp.image.shape)
                # cv2.imwrite('./rotating.jpg', imgp.image)

            # Cut with center
            if roi.central_crop.height > 0 or roi.central_crop.width > 0:
                imgp.cut_with_center(roi.central_crop.height, roi.central_crop.width)
                print('Cut with center     ...', imgp.image.shape)
                # cv2.imwrite('./cut_with_center.jpg', imgp.image)
            
            image = imgp.image

            # array to PIL.Image.Image
            image = Image.frombytes('RGB', image.shape[:2], image.tostring())
            
            ###########################
            # Encode image - method 1 #
            ###########################
            # buffered = io.BytesIO()
            # image.save(buffered, format="PNG")
            # image = str(base64.b64encode(buffered.getvalue()))
            # image = image.replace("b'","").replace("'", "")

            ###########################
            # Encode image - method 2 #
            ###########################
            tmp_io = io.BytesIO()
            np.save(tmp_io, image)
            np_bytes = tmp_io.getvalue()
            image = base64.b64encode(np_bytes).decode("UTF-8")

            #################
            # Update output #
            #################
            input['image_roi'] = image
            input['x1'] = roi.coordinate.x1
            input['y1'] = roi.coordinate.y1
            input['x2'] = roi.coordinate.x2
            input['y2'] = roi.coordinate.y2
            input['central_crop_height'] = roi.central_crop.height
            input['central_crop_width'] = roi.central_crop.width
        return input

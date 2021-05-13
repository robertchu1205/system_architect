#!/usr/bin/env python
# coding: utf-8

# In[1]:


import re
import pandas as pd
import numpy as np
import cv2
import os


# In[2]:


from math import fabs, sin, cos, radians


# In[3]:


class RegionOfInterest():
    
    def __init__(self):
        components = [
            'kb_model',
            'location',
            'maximum_long_side',
            'minimum_long_side',
            'maximum_short_side',
            'minimum_short_side',
            'maximum_aspect_ratio',
            'minimum_aspect_ratio',
            'accept_angle',
            'keep',
            'extend_pixel_above',
            'extend_pixel_below',
            'extend_pixel_left',
            'extend_pixel_right',
            'central_crop_height',
            'central_crop_width'
        ]
        columns = components
        
        defaults = [
            '.*',
            '.*',
            10000,
            1,
            10000,
            1,
            1,
            0,
            'all',
            True,
            0,
            0,
            0,
            0,
            -1,
            -1
        ]
        assert len(components) == len(columns) == len(defaults)
        
        series = []
        for i in range(len(components)):
            series.append(pd.Series([columns[i], defaults[i]], ['column_name', 'default_value']))
        self.components = pd.Series(series, components)

    def get_location(self, file_name):
        return file_name.split('_')[2]
    
    def get_angle(self, file_name):
        return int(file_name.split('_')[-6])
    
    def get_x1(self, file_name):
        return int(file_name.split('_')[-5])
    
    def get_y1(self, file_name):
        return int(file_name.split('_')[-4])
    
    def get_x2(self, file_name):
        return int(file_name.split('_')[-3])
    
    def get_y2(self, file_name):
        return int(file_name.split('_')[-2])
    
    def read_mapping_table(self, path):
        self.mapping_table = pd.read_csv(path)
    
    def set_default(self):
        if len(self.mapping_table) == 0:
            self.mapping_table.loc[0] = [np.nan] * len(self.mapping_table.keys())
        for i in self.components.keys():
            column_name = self.components[i]['column_name']
            default_value = self.components[i]['default_value']
            
            self.mapping_table[column_name] = self.mapping_table[
                column_name].replace(np.nan, default_value)
    
    def check_dtype(self):
        object_dtype = [
            self.components.kb_model.column_name,
            self.components.location.column_name
        ]
        for i in self.components.keys():
            column_name = self.components[i]['column_name']
            
            if column_name == self.components.accept_angle.column_name:
                continue
            
            if column_name == self.components.keep.column_name:
                if self.mapping_table[column_name].dtypes == bool:
                    continue
            else:
                if column_name in object_dtype:
                    if self.mapping_table[column_name].dtypes == object:
                        continue
                if not column_name in object_dtype:
                    if self.mapping_table[column_name].dtypes == float:
                        continue
                    if self.mapping_table[column_name].dtypes == int:
                        continue
            raise ValueError('Incorrect format: ', column_name)
    
    def match(self, kb_model, file_name, index):
        reason_1 = '"%s" does not match'
        reason_2 = '"%s" & "%s" does not match'
        reason_3 = 'reject with "%s"'
        
        # match kb_model
        if not re.fullmatch(self.mapping_table[self.components.kb_model.column_name][index], kb_model):
            self.reason = reason_1 % self.components.kb_model.column_name
            return False
        # match location
        location = self.get_location(file_name)
        if not re.fullmatch(self.mapping_table[self.components.location.column_name][index], location):
            self.reason = reason_1 % self.components.location.column_name
            return False
        
        # get long and short sides of bounding box
        x1, y1 = self.get_x1(file_name), self.get_y1(file_name)
        x2, y2 = self.get_x2(file_name), self.get_y2(file_name)
        
        sides = (x2-x1, y2-y1)
        long_side, short_side = max(sides), min(sides)
        
        # match long_side
        maximum_long_side = self.mapping_table[self.components.maximum_long_side.column_name][index]
        minimum_long_side = self.mapping_table[self.components.minimum_long_side.column_name][index]
        if not minimum_long_side <= long_side <= maximum_long_side:
            self.reason = reason_2 %(
                self.components.maximum_long_side.column_name,
                self.components.minimum_long_side.column_name)
            return False
        
        # match short_side
        maximum_short_side = self.mapping_table[self.components.maximum_short_side.column_name][index]
        minimum_short_side = self.mapping_table[self.components.minimum_short_side.column_name][index]
        if not minimum_short_side <= short_side <= maximum_short_side:
            self.reason = reason_2 %(
                self.components.maximum_short_side.column_name,
                self.components.minimum_short_side.column_name)
            return False
        
        # match aspect_ratio
        aspect_ratio = short_side / long_side
        maximum_aspect_ratio = self.mapping_table[self.components.maximum_aspect_ratio.column_name][index]
        minimum_aspect_ratio = self.mapping_table[self.components.minimum_aspect_ratio.column_name][index]
        if not minimum_aspect_ratio <= aspect_ratio <= maximum_aspect_ratio:
            self.reason = reason_2 %(
                self.components.maximum_aspect_ratio.column_name,
                self.components.minimum_aspect_ratio.column_name)
            return False
        
        # match angle
        angle = self.get_angle(file_name)
        accept_angle = str(self.mapping_table[self.components.accept_angle.column_name][index])
        if accept_angle != 'all':
            accept_angle = np.array(accept_angle.split(' '), dtype=float)
            if not angle in accept_angle:
                self.reason = reason_1 % self.components.accept_angle.column_name
                return False
        
        # reject or not with "keep"
        keep = self.mapping_table[self.components.keep.column_name][index]
        if not keep:
            self.reason = reason_3 % self.components.keep.column_name
            return True
        
        # get coordinate
        coordinate = [
            x1-self.mapping_table[self.components.extend_pixel_left.column_name][index],
            y1-self.mapping_table[self.components.extend_pixel_below.column_name][index],
            x2+self.mapping_table[self.components.extend_pixel_right.column_name][index],
            y2+self.mapping_table[self.components.extend_pixel_above.column_name][index]
        ]
        self.coordinate = pd.Series(coordinate, ['x1', 'y1', 'x2', 'y2'])
        self.angle = angle
        
        # get height & width
        central_crop_height = self.mapping_table[self.components.central_crop_height.column_name][index]
        central_crop_width = self.mapping_table[self.components.central_crop_width.column_name][index]
        self.central_crop = pd.Series([central_crop_height, central_crop_width], ['height', 'width'])
        
        # match successfully
        self.reason = 'match successfully'
        return True
    
    def mapping(self, kb_model, file_name):
        self.mapping_result, self.index = False, None
        for i in self.mapping_table.index:
            try:
                if not self.match(kb_model, file_name, i):
                    continue
                self.index = i
                if self.reason == 'match successfully':
                    self.mapping_result = True
                break
            except:
                pass


# In[4]:


class ImageProcessing():

    def read(self, path):
        self.image = cv2.imdecode(np.fromfile(path, dtype=np.uint8), -1)
        if type(self.image) == type(None):
            raise ValueError('Image is empty.')
    
    def cut_with_coordinate(self, x1, y1, x2, y2):
        self.image = self.image[int(y1):int(y2), int(x1):int(x2)]
        if not self.image.size or self.image.shape == (0, 0, 3):
            raise ValueError('Failed to cut image.')
    
    def cut_with_center(self, height, width):
        h, w = self.image.shape[:2]
        if height > h or height <= 0:
            height = h
        if width > w or width <= 0:
            width = w
        x, y = int(w/2), int(h/2)
        self.image = self.image[
            y-int(height/2): y+int((height+1)/2),
            x-int(width/2): x+int((width+1)/2), :
        ]
        if not self.image.size:
            raise ValueError('Failed to cut image.')
    
    def rotating(self, angle):
        h, w = self.image.shape[:2]
        rotate_h = int(w*fabs(sin(radians(angle))) + h*fabs(cos(radians(angle))))
        rotate_w = int(h*fabs(sin(radians(angle))) + w*fabs(cos(radians(angle))))
        mat_rotation = cv2.getRotationMatrix2D((w/2, h/2), -angle, 1)
        mat_rotation[0, 2] += (rotate_w-w)/2
        mat_rotation[1, 2] += (rotate_h-h)/2
        self.image = cv2.warpAffine(self.image, mat_rotation, (rotate_w, rotate_h), borderValue=(0, 0, 0))


# In[5]:


class OneAIRegionOfInterest(RegionOfInterest):
    
    def read_mapping_table(self, mapping_table):
        self.mapping_table = mapping_table


# In[6]:


class OneAIImageProcessing(ImageProcessing):
    
    def read(self, image):
        self.image = image
        if type(self.image) == type(None):
            raise ValueError('Image is empty.')


# ## Example for a image

# In[7]:


if __name__ == '__main__':
    roi_path = './roi.csv'
    kb_model = 'PWSUKB1WGE209A'
    image_path = './20200810164943_PWSUKB1WGE209A_R70_1_SolderLight_0_239_106_401_374_POLARITY.jpg'

    # get file name
    file_name = os.path.basename(image_path)
    
    # read CSV file (OneAI)
    mapping_table = pd.read_csv(roi_path)
    
    # read image (OneAI)
    image = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), -1)

    # create RegionOfInterest 
    roi = OneAIRegionOfInterest()
    # read CSV file
    roi.read_mapping_table(mapping_table)
    roi.set_default()
    roi.check_dtype()
    # mapping kb_model & file_name
    roi.mapping(kb_model, file_name)

    print('Mapping result: %s > Reason: %s\n' %(roi.mapping_result, roi.reason))
    if roi.index != None:
        print(roi.mapping_table.loc[roi.index])

    if roi.mapping_result:
        # create ImageProcessing 
        imgp = OneAIImageProcessing()
        # read image
        imgp.read(image)
        print('\nOriginal image size ...', imgp.image.shape)

        # cut with coordinate
        imgp.cut_with_coordinate(roi.coordinate.x1, roi.coordinate.y1, roi.coordinate.x2, roi.coordinate.y2)
        print('Cut with coordinate ...', imgp.image.shape)
        cv2.imwrite('./cut_with_coordinate.jpg', imgp.image)

        # rotating
        if roi.angle != 0:
            imgp.rotating(roi.angle)
            print('Rotating            ...', imgp.image.shape)
            cv2.imwrite('./rotating.jpg', imgp.image)

        # cut with center
        if roi.central_crop.height > 0 or roi.central_crop.width > 0:
            imgp.cut_with_center(roi.central_crop.height, roi.central_crop.width)
            print('Cut with center     ...', imgp.image.shape)
            cv2.imwrite('./cut_with_center.jpg', imgp.image)


from  functions.pre_process.resize.util.resize import resize_image

class handler:
    def execute(input):
        image = resize_image(input, target=(input['height'], input['width']))
        input['image'] = image

        return input
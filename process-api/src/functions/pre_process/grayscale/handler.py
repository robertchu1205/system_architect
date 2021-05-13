import base64
import re
import io
from PIL import Image

class handler:
    def execute(input):
        image = input['image']

        image = re.sub('^data:image/.+;base64,', '', image)
        image = Image.open(io.BytesIO(base64.b64decode(image)))
        image = image.convert('LA')

        # image.save('D:/greyscale.png')

        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        image = str(base64.b64encode(buffered.getvalue()))
        image = image.replace("b'","").replace("'", "")        

        input['image'] = image

        return input
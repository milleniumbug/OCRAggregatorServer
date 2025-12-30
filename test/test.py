from ocr_aggregator_server import create_app, create_ogkalu_detector, create_darknet_detector, create_box_sorter
from PIL import Image, ImageDraw
detector = create_ogkalu_detector(create_box_sorter())
try:
    darknet_detector = create_darknet_detector(create_box_sorter())
except Exception as e:
    print(f"Error creating darknet detector: {e}")
    darknet_detector = None

import os

dir = os.path.dirname(os.path.abspath(__file__))
file = os.path.join(dir, '00016.jpeg')
#  from image
def test_detector(detector, detector_name, file):
    data = open(file, 'rb')
    detected_boxes = detector(data)

    #draw boxes on the image and output it to the same folder
    image = Image.open(file)
    draw = ImageDraw.Draw(image)

    i = 1
    for box in detected_boxes:
        draw.rectangle(box, outline='red')
        # draw a number in the top left corner 
        draw.text((box[0] + 5, box[1] + 5), str(i), fill='red', font=draw._getfont(14))
        i += 1
    ext = os.path.splitext(file)[-1]
    output_file = file.replace(ext, f'_detected_{detector_name}.png')
    image.save(output_file)

    print(detected_boxes)
    
test_detector(detector, 'ogkalu', file)
if darknet_detector is not None:
    test_detector(darknet_detector, 'darknet', file)
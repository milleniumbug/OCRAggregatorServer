from ocr_aggregator_server import create_app, create_darknet_detector, create_box_sorter
from PIL import Image, ImageDraw
detector = create_darknet_detector(create_box_sorter())


#  from image
data = open('test/00016.jpeg', 'rb')
detected_boxes = detector(data)

#draw boxes on the image and output it to the same folder
image = Image.open('test/00016.jpeg')
draw = ImageDraw.Draw(image)

i = 1
for box in detected_boxes:
    draw.rectangle(box, outline='red')
    # draw a number in the top left corner 
    draw.text((box[0], box[1]), str(i), fill='red', font=draw._getfont(14))
    i += 1

image.save('test/00016_detected.png')

print(detected_boxes)
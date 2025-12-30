from PIL import Image, ImageDraw, ImageFont
import os

def get_data_dir() -> str:
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    data_dir = os.path.normpath(os.path.join(cur_dir, "..", "data"))
    if not (os.path.exists(data_dir) and os.path.isdir(data_dir)):
        data_dir = os.path.normpath(os.path.join(cur_dir, "data"))
    if not (os.path.exists(data_dir) and os.path.isdir(data_dir)):
        data_dir = os.path.join(cur_dir, "_internal/data")
    if not (os.path.exists(data_dir) and os.path.isdir(data_dir)):
        data_dir = "data"
    return data_dir

def draw_boxes_on_image(file, boxes):
    image = Image.open(file)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    draw = ImageDraw.Draw(image)
    
    # check if boxes is a list of dicts
    texts = []
    if isinstance(boxes, list) and all(isinstance(box, dict) for box in boxes):
        rects = [box['rect'] for box in boxes]
        texts = [box['text'] for box in boxes]

    else:
        rects = boxes
    
    font_path = os.path.join(get_data_dir(), "NotoSansJP-Regular.ttf")
    if os.path.exists(font_path):
        draw.font = ImageFont.truetype(font_path, size=14)
    else:
        draw.font = ImageFont.load_default(size=14)

    for i, box in enumerate(rects):
        draw.rectangle(box, outline='red')
        # draw a number in the top left corner 
        draw.text((box[0] + 5, box[1] + 5), str(i + 1), fill='red')
        # if there is text, draw it at the bottom of the box
        if len(texts) > i and texts[i] is not None:
            draw.text((box[0] + 5, box[3] + 5), str(texts[i]), fill='red')
    return image



import argparse
from typing import Union

from flask import Flask, jsonify, request
from flask_cors import CORS
import PIL.Image
import io
import os
from .util import get_data_dir

#find the data directory
cur_dir = os.path.dirname(os.path.realpath(__file__))

print ("Current directory: {}".format(cur_dir))

data_dir = get_data_dir()

print("Data directory: {}".format(data_dir))


def create_box_sorter():
    def sorter(image_file, detections: list[tuple[int, int, int, int]]):
        # what we need to do is to sort the detections by their y coordinate, and then their x coordinate
        # We find all the detections that have y coordinates that overlap by more than 50% of their height
        # We then sort those detections by their x coordinate
        # We then repeat this process until all detections are sorted
    
        # first we sort the detections by their y coordinate
        detections.sort(key=lambda x: x[1])

        detection_lists :list[list[tuple]] = []
        
        for detection in detections:
            added = False
            
            # we will iterate through the list of lists
            for detection_list in detection_lists:
                # we will check if the detection overlaps with any of the detections in the list
                for detection_in_list in detection_list:
                    # we will check if the detection overlaps with the detection in the list by more than 50 percent
                    if (detection[1] >= detection_in_list[1] and detection[1] <= detection_in_list[3]) or (detection[3] >= detection_in_list[1] and detection[3] <= detection_in_list[3]):
                        overlap_start = max(detection[1], detection_in_list[1])
                        overlap_end = min(detection[3], detection_in_list[3])
                        overlap_height = overlap_end - overlap_start
                        detection_height = detection[3] - detection[1]
                        detection_in_list_height = detection_in_list[3] - detection_in_list[1]
                        if overlap_height / detection_height >= 0.5 or overlap_height / detection_in_list_height >= 0.5:
                            detection_list.append(detection)
                            added = True
                            break
                if added:
                    break
            
            if not added:
                # we have not added the detection to a list
                # we will create a new list and add the detection to it
                detection_lists.append([detection])
                
        #sort by the x2 coordinate in reverse order
        for detection_list in detection_lists:
            detection_list.sort(key=lambda x: x[2], reverse=True)
            
        # cat them all together
        sorted_detections = []
        for detection_list in detection_lists:
            sorted_detections += detection_list
        
        return sorted_detections
    return sorter


def create_darknet_detector(detection_sorter):
    from .darknet import load_darknet_detector
    MODEL_CFG = os.path.join(data_dir, "model.cfg")
    MODEL_WEIGHTS = os.path.join(data_dir, "model.weights")

    print("Darknet: Using model.cfg: {}".format(MODEL_CFG))
    print("Darknet: Using model.weights: {}".format(MODEL_WEIGHTS))

    Detector = load_darknet_detector()
    detector = Detector(
        MODEL_CFG,
        MODEL_WEIGHTS,
        0)

    def detect(image_file):
        result = detector.detect(image_file)
        return [(x1 - 10, y1 - 10, x2 + 10, y2 + 10) for x1, y1, x2, y2 in detection_sorter(image_file, result)]

    return detect

def create_ogkalu_detector(detection_sorter, confidence_threshold=0.3):
    from . import ogkalu
    from onnxruntime import InferenceSession
    from huggingface_hub import hf_hub_download
    
    model_name = "ogkalu/comic-text-and-bubble-detector"
    model_filename = "detector.onnx"
    # download the config.json file first
    hf_hub_download(repo_id=model_name, filename='config.json')
    model_path: str = hf_hub_download(
        repo_id=model_name,
        filename=model_filename
    )
    session: InferenceSession = InferenceSession(model_path)
    
    def process_detection(result):
        return [(int(box[0]), int(box[1]), int(box[2]), int(box[3])) for box in result]

    def detect(image_file):
        text_boxes = ogkalu.detect(image_file, session, confidence_threshold)
        result = process_detection(text_boxes)
        return [(x1, y1, x2, y2) for x1, y1, x2, y2 in detection_sorter(image_file, result)]


    return detect

def create_manga_ocr():
    from manga_ocr import MangaOcr
    mocr = MangaOcr(force_cpu=True)

    def ocr(image_file):
        with PIL.Image.open(image_file) as image:
            return mocr(image).replace("．．．", "…")

    return ocr


def create_tesseract_ocr():
    import pytesseract

    def ocr(image_file):
        with PIL.Image.open(image_file) as image:
            if image.width < image.height:
                lang = 'jpn+jpn_vert'
                config = '--psm 5'
            else:
                lang = 'jpn+jpn_vert'
                config = '--psm 6'
            text = pytesseract.pytesseract.image_to_string(image, lang='jpn+jpn_vert', config=config)
            return text

    return ocr


def create_ryou_ocr():
    import base64
    import requests

    def ocr(image_file):
        imageBase64 = base64.b64encode(image_file.read()).decode('ascii')
        r = requests.post(url='http://192.168.1.122:9846/api/ocr', json={ 'type': 'japanese', 'image': imageBase64 })
        text = "\n".join(r.json()['Lines'])
        return text

    return ocr


def create_combined_detector_ocr(ocr, detector):
    def combined(image_file):
        detections = detector(image_file)
        image_file.seek(0, io.SEEK_SET)
        with PIL.Image.open(image_file) as image:
            for detection in detections:
                region = image.crop(detection)
                with io.BytesIO() as region_file:
                    region.save(region_file, 'PNG')
                    region_file.seek(0, io.SEEK_SET)
                    text = ocr(region_file)
                    yield {"text": text, "rect": detection}

    return lambda image_file: list(combined(image_file))


def create_engines(
        ocr_mode: str,
        detector_mode: str,
        combined_mode: Union[str, None],
        detection_sorter_mode: str,
        confidence_threshold: float):

    if detection_sorter_mode == 'y_coordinate':
        sorter = create_box_sorter()

    if ocr_mode == 'manga-ocr':
        ocr = create_manga_ocr()
    elif ocr_mode == 'tesseract':
        ocr = create_tesseract_ocr()
    elif ocr_mode == 'ryou':
        ocr = create_ryou_ocr()
    else:
        ocr = None

    detector = None
    if detector_mode == 'darknet':
        try:
            detector = create_darknet_detector(sorter)
        except Exception as e:
            print(f"Error creating darknet detector: {e}")
            print(f"Falling back to ogkalu detector")
            detector = None
    if detector is None:
        detector = create_ogkalu_detector(sorter, confidence_threshold)

    if combined_mode is None:
        combined_detector_ocr = create_combined_detector_ocr(ocr, detector)

    return ocr, detector, combined_detector_ocr


def create_app(ocr, detector, combined_detector_ocr, config=None):
    app = Flask(__name__)
    app.config.update(DEBUG=True)
    app.config.update(config or {})

    CORS(app)

    @app.route("/ready", methods=['GET'])
    def is_ready():
        return jsonify({"ready": True})

    @app.route("/ocr", methods=['POST'])
    def issue_ocr():
        image_file = request.files['input_image']
        with io.BytesIO(image_file.stream.read()) as buffered:
            return jsonify(str(ocr(buffered)))

    @app.route("/detect", methods=['POST'])
    def issue_textbox_detection():
        image_file = request.files['input_image']
        with io.BytesIO(image_file.stream.read()) as buffered:
            return jsonify(detector(buffered))

    @app.route("/detect_ocr", methods=['POST'])
    def issue_textbox_detection_with_ocr():
        image_file = request.files['input_image']
        with io.BytesIO(image_file.stream.read()) as buffered:
            return jsonify(combined_detector_ocr(buffered))

    return app

def test_image(image_path, output_dir, combined_detector_ocr):
    import json
    from .util import draw_boxes_on_image
    image_paths = []
    # check if the image path is a directory or a file
    if os.path.isdir(image_path):
        # get all the pngs, jpegs, and jpgs in the directory
        for file in os.listdir(image_path):
            if file.endswith('.png') or file.endswith('.jpg') or file.endswith('.jpeg'):
                image_file = os.path.join(image_path, file)
                image_paths.append(image_file)
    else:
        image_paths.append(image_path)
    for image_path in image_paths:
        with open(image_path, 'rb') as image_file:
            ret = combined_detector_ocr(image_file)
            print(json.dumps(ret, ensure_ascii=False))
            ext = os.path.splitext(image_path)[-1]
            image_file_name = os.path.basename(image_path)
            output_file = os.path.join(output_dir, image_file_name.replace(ext, f'_detected_combined.png'))
            image = draw_boxes_on_image(image_path, ret)
            #ensure dir
            os.makedirs(output_dir, exist_ok=True)
            image.save(output_file)
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", action="store", default="127.0.0.1")
    parser.add_argument("--port", action="store", default="8000")
    parser.add_argument("--detection-mode", action="store", default="ogkalu")
    parser.add_argument("--ocr-mode", action="store", default="manga-ocr")
    parser.add_argument("--combined-detection-ocr-mode", action="store", default=None)
    parser.add_argument("--detection-ordering-mode", action="store", default='y_coordinate')
    parser.add_argument("--confidence-threshold", action="store", default=0.3, help="The confidence threshold for the ogkalu detector")
    parser.add_argument("--test-image", action="store", default=None, help="Run the combined detection and OCR on the test image and then exit")
    parser.add_argument("--test-image-output", action="store", default=None, help="Output the test image to the specified file")

    args = parser.parse_args()
    ocr, detector, combined_detector_ocr = create_engines(
        args.ocr_mode,
        args.detection_mode,
        args.combined_detection_ocr_mode,
        args.detection_ordering_mode,
        float(args.confidence_threshold))
    if args.test_image is not None:
        image_path = args.test_image
        if args.test_image_output is not None:
            output_dir = args.test_image_output
        else:
            output_dir = os.path.dirname(image_path)
        test_image(image_path, output_dir, combined_detector_ocr)
        return 0

    created_app = create_app(ocr, detector, combined_detector_ocr)
    created_app.run(host=args.host, port=args.port, use_reloader=False)


if __name__ == "__main__":
    main()

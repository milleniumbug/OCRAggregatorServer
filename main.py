#!/usr/bin/env python3
import argparse
from typing import Union

from flask import Flask, jsonify, request
from flask_cors import CORS
import PIL.Image
import io
import cv2
import np


def create_darknet_detector():
    import darknet
    Detector = darknet.load_darknet_detector()
    detector = Detector(
        'data/model.cfg',
        'data/model.weights',
        0)

    def detect(image_file):
        result = detector.detect(image_file)
        return [(x1 - 10, y1 - 10, x2 + 10, y2 + 10) for x1, y1, x2, y2 in result]

    return detect


def create_manga_ocr():
    from manga_ocr import MangaOcr
    mocr = MangaOcr()

    def ocr(image_file):
        with PIL.Image.open(image_file) as image:
            return mocr(image)

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


def create_combined_detector_ocr(ocr, detector):
    def combined(image_file):
        with io.BytesIO(image_file.read()) as buffered:
            detections = detector(buffered)
            buffered.seek(0, io.SEEK_SET)
            with PIL.Image.open(buffered) as image:
                for detection in detections:
                    region = image.crop(detection)
                    with io.BytesIO() as region_file:
                        region.save(region_file, 'PNG')
                        region_file.seek(0, io.SEEK_SET)
                        text = ocr(region_file)
                        yield {"text": text, "rect": detection}

    return lambda image_file: list(combined(image_file))


def create_engines(ocr_mode: str, detector_mode: str, combined_mode: Union[str, None]):
    if ocr_mode == 'manga-ocr':
        ocr = create_manga_ocr()
    elif ocr_mode == 'tesseract':
        ocr = create_tesseract_ocr()
    else:
        ocr = None

    if detector_mode == 'darknet':
        detector = create_darknet_detector()
    else:
        detector = None

    if combined_mode is None:
        combined_detector_ocr = create_combined_detector_ocr(ocr, detector)

    return ocr_mode, detector, combined_detector_ocr


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
        return jsonify(str(ocr(image_file.stream)))

    @app.route("/detect", methods=['POST'])
    def issue_textbox_detection():
        image_file = request.files['input_image']
        return jsonify(detector(image_file.stream))

    @app.route("/detect_ocr", methods=['POST'])
    def issue_textbox_detection_with_ocr():
        image_file = request.files['input_image']
        return jsonify(combined_detector_ocr(image_file.stream))

    return app


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", action="store", default="127.0.0.1")
    parser.add_argument("--port", action="store", default="8000")
    parser.add_argument("--detection-mode", action="store", default="darknet")
    parser.add_argument("--ocr-mode", action="store", default="manga-ocr")
    parser.add_argument("--combined-detection-ocr-mode", action="store", default=None)

    args = parser.parse_args()
    ocr, detector, combined_detector_ocr = create_engines(
        args.ocr_mode,
        args.detection_mode,
        args.combined_detection_ocr_mode)
    created_app = create_app(ocr, detector, combined_detector_ocr)
    created_app.run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()

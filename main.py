#!/usr/bin/env python3
import argparse
from flask import Flask, jsonify, request
from flask_cors import CORS
import PIL.Image
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
            mocr(image)

    return ocr


def create_ocr(mode: str):
    if mode == 'manga-ocr':
        return create_manga_ocr()
    else:
        return None


def create_detector(mode: str):
    if mode == 'darknet':
        return create_darknet_detector()
    else:
        return None


def create_app(ocr, detector, config=None):
    app = Flask(__name__)
    app.config.update(config or {})

    CORS(app)

    @app.route("/ready", methods=['GET'])
    def is_ready():
        return jsonify({"ready": True})

    @app.route("/ocr", methods=['POST'])
    def issue_ocr():
        image_file = request.files['input_image']
        return jsonify(str(ocr(image_file)))

    @app.route("/detect", methods=['POST'])
    def issue_textbox_detection():
        image_file = request.files['input_image']
        return jsonify(detector(image_file.stream))

    return app


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", action="store", default="127.0.0.1")
    parser.add_argument("--port", action="store", default="8000")
    parser.add_argument("--detection-mode", action="store", default="darknet")
    parser.add_argument("--ocr-mode", action="store", default="manga-ocr")

    args = parser.parse_args()
    created_app = create_app(create_ocr(args.ocr_mode), create_detector(args.detection_mode))
    created_app.run(host=args.host, port=args.port)

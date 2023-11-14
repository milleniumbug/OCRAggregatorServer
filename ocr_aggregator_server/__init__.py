from ocr_aggregator_server.server import create_app, create_darknet_detector, create_box_sorter, create_manga_ocr, create_tesseract_ocr, create_ryou_ocr, create_combined_detector_ocr, main


if __name__ == '__main__':
    main()

__all__ = [
 "create_app",
 "create_darknet_detector",
 "create_box_sorter",
 "create_manga_ocr",
 "create_tesseract_ocr",
 "create_ryou_ocr",
 "create_combined_detector_ocr",
 "main"
]
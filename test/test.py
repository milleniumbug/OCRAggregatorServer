from ocr_aggregator_server import create_app, create_darknet_detector, create_y_coordinate_sorter


detector = create_darknet_detector(create_y_coordinate_sorter())


#  from image
data = open('test/00016.jpeg', 'rb')
detected_boxes = detector(data)
print()
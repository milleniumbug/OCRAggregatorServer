import ctypes
import os


def load_darknet_detector():
    if os.name == "posix":
        cwd = os.path.dirname(__file__)
        lib = ctypes.CDLL(cwd + "/libdarknet.so", ctypes.RTLD_GLOBAL)
    elif os.name == "nt":
        cwd = os.path.dirname(__file__)
        os.environ['PATH'] = cwd + ';' + os.environ['PATH']
        lib = ctypes.CDLL("darknet.dll", ctypes.RTLD_GLOBAL)
    else:
        raise Exception("Unsupported OS")

    class Bbox(ctypes.Structure):
        _fields_ = [
            ('x', ctypes.c_uint32),
            ('y', ctypes.c_uint32),
            ('w', ctypes.c_uint32),
            ('h', ctypes.c_uint32),
            ('prob', ctypes.c_float),
            ('obj_id', ctypes.c_uint32),
            ('track_id', ctypes.c_uint32),
            ('frames_counter', ctypes.c_uint32),
            ('x_3d', ctypes.c_float),
            ('y_3d', ctypes.c_float),
            ('z_3d', ctypes.c_float),
        ]

    class BboxContainer(ctypes.Structure):
        _fields_ = [('candidates', Bbox * 1000)]

    lib.init.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
    lib.init.restype = ctypes.c_int

    lib.detect_mat.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(BboxContainer)]
    lib.detect_mat.restype = ctypes.c_int

    lib.dispose.argtypes = []
    lib.dispose.restype = ctypes.c_int

    class Detector:
        def __init__(self, cfg_path, weights_path, gpu, batch_size=1):
            self.library = lib
            cfg = ctypes.create_string_buffer(cfg_path.encode('utf8'))
            weights = ctypes.create_string_buffer(weights_path.encode('utf8'))
            self.library.init(cfg, weights, gpu, batch_size)

        def close(self):
            self.library.dispose()

        def detect(self, image_stream):
            b = bytes(image_stream.read())
            cont = BboxContainer()
            result = self.library.detect_mat(b, len(b), ctypes.byref(cont))
            return [(box.x, box.y, box.x + box.w, box.y + box.h) for box in cont.candidates[:result]]

    return Detector

import ctypes
import os
import platform

def load_darknet_detector():
    # check if macos
    cwd = os.path.dirname(__file__)
    if platform.system() == "Darwin":
        file = "libdarknet.dylib"
    # check if linux
    elif os.name == "posix":
        file = "libdarknet.so"
    elif os.name == "nt":
        file = "darknet.dll"
    else:   
        raise Exception("Unsupported OS")
    
    lib_path: str | None = os.path.join(cwd, file)
    dirs_to_try = [cwd, os.path.abspath(os.path.join(cwd, "..")), os.path.abspath(os.path.join(cwd, "_internal"))]
    for dir in dirs_to_try:
        lib_path = os.path.join(dir, file)
        if os.path.exists(lib_path):
            break
        lib_path = None
    if not lib_path:
        raise Exception(f"{file} not found, in either {', '.join(dirs_to_try)}")
    lib_dir = os.path.dirname(lib_path)
    if os.name == "nt":
        os.environ['PATH'] = lib_dir + ';' + os.environ['PATH']
        lib = ctypes.CDLL(file, ctypes.RTLD_GLOBAL)
    else:
        if platform.system() == "Darwin":
            os.environ['DYLD_LIBRARY_PATH'] = lib_dir
        
        lib = ctypes.CDLL(lib_path, ctypes.RTLD_GLOBAL)

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

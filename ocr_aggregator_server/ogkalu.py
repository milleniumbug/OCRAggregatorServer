from PIL import Image
import numpy as np

def calculate_iou(rect1: list[float], rect2: list[float]) -> float:
    """
    Calculate the Intersection over Union (IoU) of two rectangles.
    
    Args:
        rect1: First rectangle as [x1, y1, x2, y2]
        rect2: Second rectangle as [x1, y1, x2, y2]
    
    Returns:
        IoU value as a float
    """
    x1 = max(rect1[0], rect2[0])
    y1 = max(rect1[1], rect2[1])
    x2 = min(rect1[2], rect2[2])
    y2 = min(rect1[3], rect2[3])
    
    intersection_area = max(0, x2 - x1) * max(0, y2 - y1)
    
    rect1_area = (rect1[2] - rect1[0]) * (rect1[3] - rect1[1])
    rect2_area = (rect2[2] - rect2[0]) * (rect2[3] - rect2[1])
    
    union_area = rect1_area + rect2_area - intersection_area
    
    iou = intersection_area / union_area if union_area != 0 else 0
    
    return iou

def do_rectangles_overlap(
    rect1: list[float], 
    rect2: list[float], 
    iou_threshold: float = 0.2
) -> bool:
    """
    Check if two rectangles overlap based on IoU threshold.
    
    Args:
        rect1: First rectangle as [x1, y1, x2, y2]
        rect2: Second rectangle as [x1, y1, x2, y2]
        iou_threshold: Minimum IoU to consider as overlap
    
    Returns:
        True if rectangles overlap above threshold
    """
    iou = calculate_iou(rect1, rect2)
    return iou >= iou_threshold


def does_rectangle_fit(bigger_rect: list[float], smaller_rect: list[float]) -> bool:
    """
    Check if smaller_rect fits entirely inside bigger_rect.
    
    Args:
        bigger_rect: Potential containing rectangle as [x1, y1, x2, y2]
        smaller_rect: Potential contained rectangle as [x1, y1, x2, y2]
    
    Returns:
        True if smaller_rect fits inside bigger_rect
    """
    x1, y1, x2, y2 = bigger_rect
    px1, py1, px2, py2 = smaller_rect
    
    # Ensure the coordinates are properly ordered
    left1, top1, right1, bottom1 = min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)
    left2, top2, right2, bottom2 = min(px1, px2), min(py1, py2), max(px1, px2), max(py1, py2)
    
    # Check if the second rectangle fits within the first
    fits_horizontally = left1 <= left2 and right1 >= right2
    fits_vertically = top1 <= top2 and bottom1 >= bottom2
    
    return fits_horizontally and fits_vertically


def is_mostly_contained(
    outer_box: list[float], 
    inner_box: list[float], 
    threshold: float
) -> bool:
    """
    Check if inner_box is mostly contained within outer_box.
    
    Args:
        outer_box: The larger bounding box (x1, y1, x2, y2)
        inner_box: The smaller bounding box (x1, y1, x2, y2)
        threshold: The proportion of inner_box that must be inside outer_box
    
    Returns:
        Boolean indicating if inner_box is mostly contained in outer_box
    """
    ix1, iy1, ix2, iy2 = inner_box
    ox1, oy1, ox2, oy2 = outer_box
    
    # Calculate the area of the inner and outer boxes
    inner_area = (ix2 - ix1) * (iy2 - iy1)
    outer_area = (ox2 - ox1) * (oy2 - oy1)
    
    # Return False if the outer box is smaller than the inner box
    if outer_area < inner_area or inner_area == 0:
        return False
    
    # Calculate the area of intersection
    intersection_area = max(0, min(ix2, ox2) - max(ix1, ox1)) * max(0, min(iy2, oy2) - max(iy1, oy1))
    
    # Check if the proportion of intersection to inner area is greater than the threshold
    return intersection_area / inner_area >= threshold


def merge_boxes(box1: list[float], box2: list[float]) -> list[float]:
    """
    Merge two bounding boxes.
    
    Args:
        box1: First bounding box [x1, y1, x2, y2]
        box2: Second bounding box [x1, y1, x2, y2]
    
    Returns:
        Merged bounding box [x1, y1, x2, y2]
    """
    return [
        min(box1[0], box2[0]),
        min(box1[1], box2[1]),
        max(box1[2], box2[2]),
        max(box1[3], box2[3])
    ]


def merge_overlapping_boxes(
    bboxes: np.ndarray,
    containment_threshold: float = 0.3,
    overlap_threshold: float = 0.5,
) -> np.ndarray:
    """
    Merge boxes that are mostly contained within each other, and
    prune out duplicates/overlaps immediately as you go.
    
    Args:
        bboxes: Array of bounding boxes
        containment_threshold: Threshold for containment-based merging
        overlap_threshold: Threshold for overlap-based filtering
    
    Returns:
        Array of merged and filtered bounding boxes
    """
    accepted = []

    for i, box in enumerate(bboxes):
        # 1) Merge this box against all others based on containment:
        merged = box.copy()
        for j, other in enumerate(bboxes):
            if i == j:
                continue
            if (is_mostly_contained(merged, other, containment_threshold)
             or is_mostly_contained(other, merged, containment_threshold)):
                merged = merge_boxes(merged, other)

        # 2) On-the-fly pruning: see if `merged` overlaps or duplicates any accepted box
        conflict = False
        for acc in accepted:
            if np.array_equal(merged, acc) or do_rectangles_overlap(merged, acc, overlap_threshold):
                conflict = True
                break

        if conflict:
            # skip this one entirely
            continue

        # 3) Optionally, remove any already-accepted boxes that overlap too much with the new merged box
        accepted = [
            acc for acc in accepted
            if not (np.array_equal(acc, merged)
                    or do_rectangles_overlap(merged, acc, overlap_threshold))
        ]

        # 4) Finally accept the new box
        accepted.append(merged)

    return np.array(accepted)

def filter_and_fix_bboxes(
    bboxes: list[tuple[int, int, int, int]] | np.ndarray, 
    image_shape: tuple[int, int] | None = None, 
    width_tolerance: int = 5, 
    height_tolerance: int = 5
) -> np.ndarray:
    """
    Filter out or fix bounding boxes that don't make sense.
    
    - Drops any box with x2<=x1 or y2<=y1
    - Drops any box whose width or height is <= the given tolerances
    - If image_shape is provided, clamps boxes to [0, width)×[0, height)
    
    Args:
        bboxes: array-like of boxes [[x1, y1, x2, y2], …]
        image_shape: optional tuple (img_h, img_w) to clamp coordinates into
        width_tolerance: minimum width to keep
        height_tolerance: minimum height to keep
    
    Returns:
        np.ndarray of cleaned boxes
    """
    if len(bboxes) == 0:
        return np.empty((0,4), dtype=int)

    cleaned = []
    img_h, img_w = (None, None)
    if image_shape is not None:
        img_h, img_w = image_shape[:2]

    for box in bboxes:
        x1, y1, x2, y2 = box
        
        # clamp to image if dims given
        if img_w is not None:
            x1 = max(0, min(x1, img_w))
            x2 = max(0, min(x2, img_w))
        if img_h is not None:
            y1 = max(0, min(y1, img_h))
            y2 = max(0, min(y2, img_h))
        
        # ensure positive area
        w = x2 - x1
        h = y2 - y1
        if w <= 0 or h <= 0:
            continue
        
        # enforce minimum size
        if w <= width_tolerance or h <= height_tolerance:
            continue
        
        cleaned.append([x1, y1, x2, y2])

    return np.array(cleaned, dtype=int)



class ogkalu_bbox:
    x: int
    y: int
    x2: int
    y2: int
    confidence: float
    label: int
    
    def __init__(self, x: int, y: int, x2: int, y2: int, confidence: float, label: int):
        self.x = int(x)
        self.y = int(y)
        self.x2 = int(x2)
        self.y2 = int(y2)
        self.confidence = float(confidence)
        self.label = int(label)



def read_image(image):
    """Read an image file and return as RGB numpy array."""
    im = Image.open(image)
    if im.mode != "RGB":
        im = im.convert("RGB")
    return im

def get_image_array(path):
    pil_image = read_image(path)
    image_arr = np.array(pil_image)
    
    # pil_image = Image.fromarray(image_arr)  # image is already in RGB format
    im_resized = pil_image.resize((640, 640))
    arr = np.asarray(im_resized, dtype=np.float32) / 255.0  # (H,W,3)
    arr = np.transpose(arr, (2, 0, 1))  # (3,H,W)
    im_data = arr[np.newaxis, ...]  # (1,3,H,W)

    w, h = pil_image.size
    orig_size = np.array([[w, h]], dtype=np.int64)
    return im_data, orig_size, image_arr

def detect(image_file, session, confidence_threshold):
    resized_im_data, orig_size, image_arr = get_image_array(image_file)
            
    opt = {}
    opt["orig_target_sizes"] = [orig_size]
    outputs = session.run(None, {
        "images": resized_im_data,
        "orig_target_sizes": orig_size
    })
    
    labels, boxes, scores = outputs[:3]

    if isinstance(labels, np.ndarray) and labels.ndim == 2 and labels.shape[0] == 1:
        labels = labels[0]
    if isinstance(scores, np.ndarray) and scores.ndim == 2 and scores.shape[0] == 1:
        scores = scores[0]
    if isinstance(boxes, np.ndarray) and boxes.ndim == 3 and boxes.shape[0] == 1:
        boxes = boxes[0]
        
    def hash_box(box: np.ndarray) -> int:
        return hash((float(box[0]), float(box[1]), float(box[2]), float(box[3])))


    bubble_boxes = []
    text_boxes = []
    box_to_confidence = {}
    box_to_label = {}
    for i, box in enumerate(boxes):
        confidence = scores[i]
        if confidence < confidence_threshold:
            continue
        label = labels[i]
        if label == 0:
            bubble_boxes.append(box)
        elif label in [1, 2]:
            text_boxes.append(box)
    # height, width
    image_shape = (orig_size[0][1], orig_size[0][0])
    text_boxes = filter_and_fix_bboxes(text_boxes, image_shape)
    text_boxes = merge_overlapping_boxes(text_boxes)
    
    return text_boxes
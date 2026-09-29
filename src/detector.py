from ultralytics import YOLO

# Load trained model
model = YOLO("models/best.pt")


def detect_vehicles(image):
    """
    Detect vehicles and emergency vehicles from an image.
    """
    results = model(image)

    return results
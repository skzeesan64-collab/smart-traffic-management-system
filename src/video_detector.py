import cv2
from ultralytics import YOLO


# Load trained YOLO model
model = YOLO("models/best.pt")


# Emergency vehicle classes
EMERGENCY_CLASSES = {
    "ambulance",
    "ambulance_108",
    "ambulance_SOL",
    "fire_truck",
    "fireladder",
    "police"
}


def detect_video(input_video, output_video):
    """
    Detect vehicles and emergency vehicles in a video.

    Parameters:
        input_video  : path of input video
        output_video : path where processed video will be saved

    Returns:
        Dictionary containing detection summary.
    """

    cap = cv2.VideoCapture(input_video)

    if not cap.isOpened():
        raise ValueError("Unable to open input video.")

    # Video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        fps = 25

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Output video writer
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    writer = cv2.VideoWriter(
        output_video,
        fourcc,
        fps,
        (width, height)
    )

    frame_count = 0
    emergency_detected = False

    emergency_counts = {
        "ambulance": 0,
        "fire_truck": 0,
        "police": 0
    }

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        frame_count += 1

        # YOLO detection
        results = model(frame, verbose=False)

        result = results[0]

        # Draw detection boxes
        annotated_frame = result.plot()

        # Get detected class names
        detected_classes = []

        if result.boxes is not None and len(result.boxes) > 0:

            detected_classes = [
                result.names[int(cls)]
                for cls in result.boxes.cls
            ]

        # Check emergency vehicles
        for class_name in detected_classes:

            if class_name in EMERGENCY_CLASSES:

                emergency_detected = True

            if class_name in {
                "ambulance",
                "ambulance_108",
                "ambulance_SOL"
            }:
                emergency_counts["ambulance"] += 1

            elif class_name in {
                "fire_truck",
                "fireladder"
            }:
                emergency_counts["fire_truck"] += 1

            elif class_name == "police":
                emergency_counts["police"] += 1

        # Add status on video
        if emergency_detected:

            cv2.putText(
                annotated_frame,
                "EMERGENCY VEHICLE DETECTED",
                (20, 45),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                3
            )

        else:

            cv2.putText(
                annotated_frame,
                "NORMAL TRAFFIC",
                (20, 45),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                3
            )

        # Write frame
        writer.write(annotated_frame)

    # Release resources
    cap.release()
    writer.release()

    return {
        "total_frames": frame_count,
        "emergency_detected": emergency_detected,
        "ambulance_detections": emergency_counts["ambulance"],
        "fire_truck_detections": emergency_counts["fire_truck"],
        "police_detections": emergency_counts["police"]
    }
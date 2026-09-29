from flask import Flask, render_template, request, send_file
from src.detector import detect_vehicles
from src.video_detector import detect_video
from src.traffic.signal_control import get_signal_status

from PIL import Image
from werkzeug.utils import secure_filename

import io
import os
import base64
import uuid


# ==========================================================
# Flask App
# ==========================================================

app = Flask(__name__)


# ==========================================================
# Folders
# ==========================================================

UPLOAD_FOLDER = "data/videos"
RESULT_FOLDER = "results"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)


# ==========================================================
# Home Page
# ==========================================================

@app.route("/")
def home():
    return render_template("index.html")


# ==========================================================
# IMAGE ANALYSIS
# ==========================================================

@app.route("/analyze", methods=["POST"])
def analyze():

    uploaded_image = request.files.get("image")

    if not uploaded_image:
        return "No image uploaded.", 400

    # ------------------------------------------------------
    # Open image
    # ------------------------------------------------------

    image = Image.open(uploaded_image).convert("RGB")

    # ------------------------------------------------------
    # YOLO detection
    # ------------------------------------------------------

    results = detect_vehicles(image)

    result = results[0]

    # ------------------------------------------------------
    # Get detected class names
    # ------------------------------------------------------

    detected_classes = [
        result.names[int(cls)]
        for cls in result.boxes.cls
    ]

    # ------------------------------------------------------
    # Total detections
    # ------------------------------------------------------

    vehicle_count = len(detected_classes)

    # ------------------------------------------------------
    # Emergency vehicle classes
    # ------------------------------------------------------

    ambulance_classes = {
        "ambulance",
        "ambulance_108",
        "ambulance_SOL"
    }

    fire_classes = {
        "fire_truck",
        "fireladder"
    }

    police_classes = {
        "police"
    }

    # ------------------------------------------------------
    # Emergency counts
    # ------------------------------------------------------

    ambulance_count = sum(
        cls in ambulance_classes
        for cls in detected_classes
    )

    fire_truck_count = sum(
        cls in fire_classes
        for cls in detected_classes
    )

    police_count = sum(
        cls in police_classes
        for cls in detected_classes
    )

    # ------------------------------------------------------
    # Emergency detection
    # ------------------------------------------------------

    emergency_detected = (
        ambulance_count > 0
        or fire_truck_count > 0
        or police_count > 0
    )

    # ------------------------------------------------------
    # Traffic signal status
    # ------------------------------------------------------

    signal_status = get_signal_status(
        1 if emergency_detected else 0
    )

    # ------------------------------------------------------
    # Draw YOLO boxes
    # ------------------------------------------------------

    result_image = results[0].plot()

    result_image = Image.fromarray(result_image)

    buffer = io.BytesIO()

    result_image.save(
        buffer,
        format="JPEG"
    )

    image_base64 = base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")

    # ======================================================
    # IMAGE RESULT PAGE
    # ======================================================

    if emergency_detected:

        emergency_box = """
        <div class="emergency active">
            🚨 EMERGENCY VEHICLE DETECTED
            <span>Traffic signal priority should be given.</span>
        </div>
        """

    else:

        emergency_box = """
        <div class="emergency normal">
            ✅ NO EMERGENCY VEHICLE
            <span>Normal traffic signal operation.</span>
        </div>
        """

    signal = signal_status.get(
        "signal",
        "RED"
    )

    mode = signal_status.get(
        "mode",
        "NORMAL TRAFFIC"
    )

    message = signal_status.get(
        "message",
        "Normal traffic operation."
    )

    status = signal_status.get(
        "status",
        ""
    )

    return f"""
    <!DOCTYPE html>

    <html>

    <head>

        <title>Traffic Detection Result</title>

        <style>

            body {{
                margin: 0;
                background: #0f172a;
                color: white;
                font-family: Arial, sans-serif;
                text-align: center;
            }}

            .container {{
                width: 90%;
                max-width: 1000px;
                margin: 40px auto;
            }}

            h1 {{
                font-size: 42px;
                margin-bottom: 35px;
            }}

            .cards {{
                display: grid;
                grid-template-columns:
                    repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 35px;
            }}

            .card {{
                background: #1e293b;
                padding: 25px;
                border-radius: 18px;
            }}

            .card h2 {{
                color: #cbd5e1;
                font-size: 20px;
            }}

            .number {{
                font-size: 45px;
                font-weight: bold;
                color: #38bdf8;
            }}

            .emergency {{
                padding: 30px;
                border-radius: 18px;
                font-size: 30px;
                font-weight: bold;
                margin: 30px 0;
            }}

            .emergency span {{
                display: block;
                font-size: 18px;
                margin-top: 12px;
            }}

            .active {{
                background: #7f1d1d;
                border: 3px solid #ef4444;
            }}

            .normal {{
                background: #14532d;
                border: 3px solid #22c55e;
            }}

            .signal {{
                background: #1e293b;
                padding: 35px;
                border-radius: 20px;
                margin-bottom: 35px;
            }}

            .signal h2 {{
                font-size: 30px;
            }}

            .green {{
                color: #22c55e;
                font-size: 55px;
                font-weight: bold;
            }}

            .red {{
                color: #ef4444;
                font-size: 55px;
                font-weight: bold;
            }}

            .result {{
                background: #1e293b;
                padding: 30px;
                border-radius: 20px;
            }}

            .result img {{
                max-width: 90%;
                border-radius: 15px;
            }}

            .back {{
                display: inline-block;
                margin-top: 30px;
                padding: 15px 30px;
                background: #38bdf8;
                color: #0f172a;
                text-decoration: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 18px;
            }}

        </style>

    </head>

    <body>

        <div class="container">

            <h1>🚦 Smart Traffic Management System</h1>

            <div class="cards">

                <div class="card">
                    <h2>Total Detected</h2>
                    <div class="number">
                        {vehicle_count}
                    </div>
                </div>

                <div class="card">
                    <h2>🚑 Ambulance</h2>
                    <div class="number">
                        {ambulance_count}
                    </div>
                </div>

                <div class="card">
                    <h2>🚒 Fire Truck</h2>
                    <div class="number">
                        {fire_truck_count}
                    </div>
                </div>

                <div class="card">
                    <h2>🚓 Police</h2>
                    <div class="number">
                        {police_count}
                    </div>
                </div>

            </div>

            {emergency_box}

            <div class="signal">

                <h2>🚦 TRAFFIC SIGNAL STATUS</h2>

                <div class="{
                    'green' if signal == 'GREEN'
                    else 'red'
                }">

                    ● {signal}

                </div>

                <h2>{mode}</h2>

                <p>{message}</p>

                <p>{status}</p>

            </div>

            <div class="result">

                <h2>🤖 AI Detection Output</h2>

                <img
                    src="data:image/jpeg;base64,{image_base64}"
                    alt="Detection Result"
                >

            </div>

            <a class="back" href="/">
                ← Analyze Another File
            </a>

        </div>

    </body>

    </html>
    """


# ==========================================================
# VIDEO ANALYSIS
# ==========================================================

@app.route("/analyze_video", methods=["POST"])
def analyze_video():

    uploaded_video = request.files.get("video")

    if not uploaded_video:
        return "No video uploaded.", 400

    if uploaded_video.filename == "":
        return "No video selected.", 400

    # ------------------------------------------------------
    # Generate unique filenames
    # ------------------------------------------------------

    unique_id = uuid.uuid4().hex[:8]

    original_name = secure_filename(
        uploaded_video.filename
    )

    input_path = os.path.join(
        UPLOAD_FOLDER,
        f"{unique_id}_{original_name}"
    )

    output_path = os.path.join(
        RESULT_FOLDER,
        f"video_detected_{unique_id}.mp4"
    )

    # ------------------------------------------------------
    # Save uploaded video
    # ------------------------------------------------------

    uploaded_video.save(input_path)

    # ------------------------------------------------------
    # Run video detection
    # ------------------------------------------------------

    result = detect_video(
        input_path,
        output_path
    )

    # ------------------------------------------------------
    # Get results
    # ------------------------------------------------------

    total_frames = result.get(
        "total_frames",
        0
    )

    emergency_detected = result.get(
        "emergency_detected",
        False
    )

    ambulance_count = result.get(
        "ambulance_detections",
        0
    )

    fire_truck_count = result.get(
        "fire_truck_detections",
        0
    )

    police_count = result.get(
        "police_detections",
        0
    )

    # ------------------------------------------------------
    # Traffic signal
    # ------------------------------------------------------

    signal_status = get_signal_status(
        1 if emergency_detected else 0
    )

    signal = signal_status.get(
        "signal",
        "RED"
    )

    mode = signal_status.get(
        "mode",
        "NORMAL TRAFFIC"
    )

    message = signal_status.get(
        "message",
        "Normal traffic operation."
    )

    status = signal_status.get(
        "status",
        ""
    )

    # ------------------------------------------------------
    # Emergency box
    # ------------------------------------------------------

    if emergency_detected:

        emergency_box = """
        <div class="emergency active">
            🚨 EMERGENCY VEHICLE DETECTED
            <span>Traffic signal priority should be given.</span>
        </div>
        """

    else:

        emergency_box = """
        <div class="emergency normal">
            ✅ NO EMERGENCY VEHICLE
            <span>Normal traffic signal operation.</span>
        </div>
        """

    # ======================================================
    # VIDEO RESULT PAGE
    # ======================================================

    return f"""
    <!DOCTYPE html>

    <html>

    <head>

        <title>Video Detection Result</title>

        <style>

            body {{
                margin: 0;
                background: #0f172a;
                color: white;
                font-family: Arial, sans-serif;
                text-align: center;
            }}

            .container {{
                width: 90%;
                max-width: 1100px;
                margin: 40px auto;
            }}

            h1 {{
                font-size: 42px;
            }}

            .cards {{
                display: grid;
                grid-template-columns:
                    repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 35px 0;
            }}

            .card {{
                background: #1e293b;
                padding: 25px;
                border-radius: 18px;
            }}

            .card h2 {{
                color: #cbd5e1;
                font-size: 20px;
            }}

            .number {{
                font-size: 45px;
                font-weight: bold;
                color: #38bdf8;
            }}

            .emergency {{
                padding: 30px;
                border-radius: 18px;
                font-size: 30px;
                font-weight: bold;
                margin: 30px 0;
            }}

            .emergency span {{
                display: block;
                font-size: 18px;
                margin-top: 12px;
            }}

            .active {{
                background: #7f1d1d;
                border: 3px solid #ef4444;
            }}

            .normal {{
                background: #14532d;
                border: 3px solid #22c55e;
            }}

            .signal {{
                background: #1e293b;
                padding: 35px;
                border-radius: 20px;
                margin: 30px 0;
            }}

            .green {{
                color: #22c55e;
                font-size: 55px;
                font-weight: bold;
            }}

            .red {{
                color: #ef4444;
                font-size: 55px;
                font-weight: bold;
            }}

            video {{
                width: 90%;
                max-width: 900px;
                border-radius: 15px;
                margin-top: 20px;
            }}

            .back {{
                display: inline-block;
                margin-top: 30px;
                padding: 15px 30px;
                background: #38bdf8;
                color: #0f172a;
                text-decoration: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 18px;
            }}

        </style>

    </head>

    <body>

        <div class="container">

            <h1>🎥 Video Detection Result</h1>

            <div class="cards">

                <div class="card">
                    <h2>🎞️ Total Frames</h2>
                    <div class="number">
                        {total_frames}
                    </div>
                </div>

                <div class="card">
                    <h2>🚑 Ambulance</h2>
                    <div class="number">
                        {ambulance_count}
                    </div>
                </div>

                <div class="card">
                    <h2>🚒 Fire Truck</h2>
                    <div class="number">
                        {fire_truck_count}
                    </div>
                </div>

                <div class="card">
                    <h2>🚓 Police</h2>
                    <div class="number">
                        {police_count}
                    </div>
                </div>

            </div>

            {emergency_box}

            <div class="signal">

                <h2>🚦 TRAFFIC SIGNAL STATUS</h2>

                <div class="{
                    'green' if signal == 'GREEN'
                    else 'red'
                }">

                    ● {signal}

                </div>

                <h2>{mode}</h2>

                <p>{message}</p>

                <p>{status}</p>

            </div>

            <div>

                <h2>🤖 AI Video Detection Output</h2>

                <video controls>

                    <source
                        src="/video_result/{os.path.basename(output_path)}"
                        type="video/mp4"
                    >

                    Your browser does not support video playback.

                </video>

            </div>

            <br>

            <a class="back" href="/">
                ← Analyze Another File
            </a>

        </div>

    </body>

    </html>
    """


# ==========================================================
# SERVE PROCESSED VIDEO
# ==========================================================

@app.route("/video_result/<filename>")
def video_result(filename):

    file_path = os.path.join(
        RESULT_FOLDER,
        filename
    )

    if not os.path.exists(file_path):
        return "Video result not found.", 404

    return send_file(
        file_path,
        mimetype="video/mp4"
    )


# ==========================================================
# Run Flask
# ==========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )
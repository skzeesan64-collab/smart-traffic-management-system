from flask import Flask, render_template, request
from src.detector import detect_vehicles
from src.traffic.signal_control import get_signal_status
from PIL import Image
import io
import base64

app = Flask(__name__)


# --------------------------------------------------
# Home Page
# --------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# --------------------------------------------------
# Analyze Image
# --------------------------------------------------

@app.route("/analyze", methods=["POST"])
def analyze():

    uploaded_image = request.files["image"]

    # Open uploaded image
    image = Image.open(uploaded_image).convert("RGB")

    # Run YOLO detection
    results = detect_vehicles(image)

    # Get first result
    result = results[0]

    # Get detected class names
    detected_classes = [
        result.names[int(cls)]
        for cls in result.boxes.cls
    ]

    # --------------------------------------------------
    # Total Detection Count
    # --------------------------------------------------

    vehicle_count = len(detected_classes)

    # --------------------------------------------------
    # Emergency Vehicle Classes
    # --------------------------------------------------

    ambulance_classes = {
        "ambulance",
        "ambulance_108",
        "ambulance_SOL"
    }

    fire_truck_classes = {
        "fire_truck",
        "fireladder"
    }

    police_classes = {
        "police"
    }

    # --------------------------------------------------
    # Count Emergency Vehicles
    # --------------------------------------------------

    ambulance_count = sum(
        cls in ambulance_classes
        for cls in detected_classes
    )

    fire_truck_count = sum(
        cls in fire_truck_classes
        for cls in detected_classes
    )

    police_count = sum(
        cls in police_classes
        for cls in detected_classes
    )

    # --------------------------------------------------
    # Total Emergency Vehicles
    # --------------------------------------------------

    emergency_count = (
        ambulance_count
        + fire_truck_count
        + police_count
    )

    # --------------------------------------------------
    # Traffic Signal Control
    # --------------------------------------------------

    signal_data = get_signal_status(emergency_count)

    signal_mode = signal_data["mode"]
    signal_status = signal_data["signal"]
    signal_message = signal_data["message"]
    signal_description = signal_data["status"]

    # --------------------------------------------------
    # Emergency Alert
    # --------------------------------------------------

    if emergency_count > 0:

        emergency_status = "🚨 EMERGENCY VEHICLE DETECTED"

        emergency_message = (
            "Traffic signal priority should be given."
        )

        emergency_class = "emergency"

    else:

        emergency_status = "✅ NO EMERGENCY VEHICLE"

        emergency_message = (
            "Normal traffic signal operation."
        )

        emergency_class = "normal"

    # --------------------------------------------------
    # Draw YOLO Detection Boxes
    # --------------------------------------------------

    result_image = results[0].plot()

    result_image = Image.fromarray(result_image)

    # --------------------------------------------------
    # Convert Image to Browser Format
    # --------------------------------------------------

    buffer = io.BytesIO()

    result_image.save(
        buffer,
        format="JPEG"
    )

    image_base64 = base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")

    # --------------------------------------------------
    # Result Dashboard
    # --------------------------------------------------

    return f"""
<!DOCTYPE html>

<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <title>Smart Traffic Management System</title>

    <style>

        body {{
            margin: 0;
            font-family: Arial, sans-serif;
            background: #0f172a;
            color: white;
            text-align: center;
        }}

        .container {{
            width: 90%;
            max-width: 1200px;
            margin: 40px auto;
        }}

        h1 {{
            font-size: 36px;
            margin-bottom: 30px;
        }}

        /* ------------------------------------------
           Statistics Cards
        ------------------------------------------ */

        .stats {{
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
            margin-bottom: 30px;
        }}

        .card {{
            background: #1e293b;
            padding: 20px;
            border-radius: 15px;
            width: 180px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }}

        .card h2 {{
            font-size: 32px;
            margin: 10px 0;
            color: #38bdf8;
        }}

        .card p {{
            margin: 0;
            color: #cbd5e1;
            font-size: 16px;
        }}

        /* ------------------------------------------
           Emergency Alert
        ------------------------------------------ */

        .alert {{
            padding: 22px;
            border-radius: 15px;
            margin: 25px auto 30px;
            max-width: 800px;
        }}

        .emergency {{
            background: #7f1d1d;
            border: 2px solid #ef4444;
        }}

        .normal {{
            background: #14532d;
            border: 2px solid #22c55e;
        }}

        .alert h2 {{
            margin: 5px 0 10px;
            font-size: 24px;
        }}

        .alert p {{
            margin: 0;
            color: #e2e8f0;
            font-size: 16px;
        }}

        /* ------------------------------------------
           Traffic Signal
        ------------------------------------------ */

        .signal-box {{
            background: #1e293b;
            padding: 25px;
            border-radius: 15px;
            margin: 25px auto 30px;
            max-width: 800px;
        }}

        .signal-box h2 {{
            margin-bottom: 20px;
        }}

        .signal {{
            font-size: 48px;
            font-weight: bold;
            margin: 15px;
        }}

        .green {{
            color: #22c55e;
        }}

        .red {{
            color: #ef4444;
        }}

        .signal-mode {{
            font-size: 20px;
            font-weight: bold;
            margin: 10px;
        }}

        .signal-message {{
            color: #cbd5e1;
            font-size: 16px;
        }}

        /* ------------------------------------------
           AI Detection Output
        ------------------------------------------ */

        .result-box {{
            background: #1e293b;
            padding: 25px;
            border-radius: 15px;
        }}

        .result-box img {{
            max-width: 90%;
            border-radius: 12px;
        }}

        /* ------------------------------------------
           Back Button
        ------------------------------------------ */

        .back-button {{
            display: inline-block;
            margin-top: 25px;
            padding: 12px 25px;
            background: #38bdf8;
            color: #0f172a;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
        }}

        .back-button:hover {{
            background: #7dd3fc;
        }}

    </style>

</head>


<body>

<div class="container">

    <h1>
        🚦 Smart Traffic Management System
    </h1>


    <!-- ------------------------------------------
         Detection Statistics
    ------------------------------------------- -->

    <div class="stats">

        <div class="card">

            <p>Total Detected</p>

            <h2>
                {vehicle_count}
            </h2>

        </div>


        <div class="card">

            <p>🚑 Ambulance</p>

            <h2>
                {ambulance_count}
            </h2>

        </div>


        <div class="card">

            <p>🚒 Fire Truck</p>

            <h2>
                {fire_truck_count}
            </h2>

        </div>


        <div class="card">

            <p>🚓 Police</p>

            <h2>
                {police_count}
            </h2>

        </div>

    </div>


    <!-- ------------------------------------------
         Emergency Alert
    ------------------------------------------- -->

    <div class="alert {emergency_class}">

        <h2>
            {emergency_status}
        </h2>

        <p>
            {emergency_message}
        </p>

    </div>


    <!-- ------------------------------------------
         Traffic Signal Status
    ------------------------------------------- -->

    <div class="signal-box">

        <h2>
            🚦 TRAFFIC SIGNAL STATUS
        </h2>

        <div class="signal
            {'green' if signal_status == 'GREEN' else 'red'}">

            {'🟢' if signal_status == 'GREEN' else '🔴'}

            {signal_status}

        </div>

        <div class="signal-mode">

            {signal_mode}

        </div>

        <p class="signal-message">

            {signal_message}

        </p>

        <p class="signal-message">

            {signal_description}

        </p>

    </div>


    <!-- ------------------------------------------
         AI Detection Output
    ------------------------------------------- -->

    <div class="result-box">

        <h2>
            🤖 AI Detection Output
        </h2>

        <img
            src="data:image/jpeg;base64,{image_base64}"
            alt="Detection Result"
        >

    </div>


    <!-- ------------------------------------------
         Back Button
    ------------------------------------------- -->

    <a href="/" class="back-button">

        ← Analyze Another Image

    </a>

</div>

</body>

</html>
"""


# --------------------------------------------------
# Run Flask
# --------------------------------------------------

if __name__ == "__main__":

    app.run(debug=True)
# --------------------------------------------------
# Smart Traffic Signal Control
# --------------------------------------------------


def get_signal_status(emergency_count):
    """
    Decide traffic signal status based on
    emergency vehicle detection.
    """

    if emergency_count > 0:

        return {
            "mode": "EMERGENCY PRIORITY",
            "signal": "GREEN",
            "message": "Emergency vehicle detected. Green signal priority activated.",
            "status": "🚨 Emergency vehicle has priority."
        }

    else:

        return {
            "mode": "NORMAL TRAFFIC",
            "signal": "RED",
            "message": "No emergency vehicle detected. Normal traffic control.",
            "status": "🟢 Normal traffic operation."
        }
from datetime import datetime, timedelta
from .models import BloodSugar


def get_readings_from_db(session, time_range='24h'):
    
    time_threshold = datetime.now()

    if time_range == '24h':
        time_threshold = time_threshold - timedelta(hours=24)

    elif time_range == 'week':
        time_threshold = time_threshold - timedelta(days=7)

    elif time_range == 'fortnight':
        time_threshold = time_threshold - timedelta(days=14)

    readings = session.query(BloodSugar).filter(BloodSugar.timestamp >= time_threshold).all()

    data = []
    for reading in readings:
        data.append({
            'timestamp': reading.timestamp,
            'blood_glucose_value': reading.blood_glucose_value,
            'description': reading.blood_description
        })
    
    return data
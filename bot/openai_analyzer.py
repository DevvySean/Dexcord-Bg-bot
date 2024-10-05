import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def analyze_blood_sugar_trends(readings, time_range='24h'):
    reading_summary = "\n".join([f"Time: {reading['timestamp']}, Blood Sugar: {reading['blood_glucose_value']}, Trend: {reading['description']}" for reading in readings])
    
    prompt = f"""Here are the blood sugar readings from the last {time_range}:\n\n{reading_summary}\n\nCan you analyze these and provide insights on any trends, 
    also make sure you have enough data to make a good analysis and provide recommendations for the user. If you dont have enough data please let the user know and dont suggest anything.
    also can you provide a summary of the trends in the blood sugar readings and give the user their percentage for time their blood sugars were in range, their range is between 5 and 10 mmol/L."""
    messages = [
        {
            "role": "system",
            "content": "You are an AI assistant that helps analyze blood sugar trends."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=300,
        temperature=0
    )

    return response.choices[0].message['content']
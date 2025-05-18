import streamlit as st
import requests
import sqlite3
from datetime import datetime, timezone
import os
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load API key
try:
    from config import OPENWEATHERMAP_API_KEY
except ImportError:
    OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
    if not OPENWEATHERMAP_API_KEY:
        logger.error("OPENWEATHERMAP_API_KEY environment variable not set")
        st.error("API key not set. Please set the OPENWEATHERMAP_API_KEY environment variable.")
        st.stop()

logger.debug(f"API Key loaded: {OPENWEATHERMAP_API_KEY[:5]}...")

BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# Use absolute path for local database, /tmp for Streamlit Community Cloud
DB_PATH = os.path.join(os.getcwd(), "weather.db") if not 'STREAMLIT_CLOUD' in os.environ else '/tmp/weather.db'
logger.debug(f"Database path: {DB_PATH}")

# Initialize SQLite database
def init_db():
    try:
        logger.debug("Initializing database")
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS search_history (city TEXT, timestamp TEXT, temperature REAL, description TEXT)")
        conn.commit()
        conn.close()
        logger.debug("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        st.error(f"Database error: {str(e)}")
        st.stop()

# Fetch weather data
def fetch_weather(location):
    if not location:
        return None, "Location cannot be empty"

    # Parse location
    parts = location.split(',')
    city = parts[0].strip()
    state = parts[1].strip() if len(parts) > 1 else None
    country = parts[2].strip() if len(parts) > 2 else None

    # Build query
    query = city
    if state:
        query += f",{state}"
    if country:
        query += f",{country}"
    logger.debug(f"Query constructed: {query}")

    # Fetch weather data
    params = {'q': query, 'appid': OPENWEATHERMAP_API_KEY, 'units': 'metric'}
    try:
        logger.debug("Sending request to OpenWeatherMap API")
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        logger.debug(f"API response status: {response.status_code}")

        if response.status_code == 200:
            weather_data = {
                'city': data['name'],
                'temperature': data['main']['temp'],
                'description': data['weather'][0]['description'].capitalize(),
                'humidity': data['main']['humidity'],
                'icon': data['weather'][0]['icon'],
                'country': data['sys']['country']
            }
            display_location = weather_data['city']
            if state:
                display_location += f", {state}"
            if country:
                display_location += f", {country}"
            weather_data['display_location'] = display_location

            # Save to database
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            logger.debug(f"Saving to database: {display_location}")
            c.execute("INSERT INTO search_history (city, timestamp, temperature, description) VALUES (?, ?, ?, ?)",
                      (display_location.lower(), datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'), 
                       weather_data['temperature'], weather_data['description']))
            conn.commit()
            conn.close()
            logger.debug("Data saved to database")

            return weather_data, None
        else:
            logger.warning(f"API error: {data.get('message', 'Unknown error')}")
            return None, "Location not found"
    except Exception as e:
        logger.error(f"Error fetching weather: {str(e)}")
        return None, str(e)

# Fetch search history
def get_history():
    try:
        logger.debug("Fetching search history")
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM search_history ORDER BY timestamp DESC LIMIT 5")
        history = [{'city': row[0], 'timestamp': row[1], 'temperature': row[2], 'description': row[3]} 
                   for row in c.fetchall()]
        conn.close()
        logger.debug(f"History retrieved: {history}")
        return history
    except Exception as e:
        logger.error(f"Error in get_history: {str(e)}")
        return []

# Streamlit app
def main():
    # Initialize database
    init_db()

    # Set page config
    st.set_page_config(page_title="Weather App", page_icon="🌞", layout="centered")

    # Custom CSS for background and black text
    st.markdown("""
        <style>
        body {
            background-image: url('https://cdn.pixabay.com/photo/2017/08/30/01/05/sun-2694505_1280.jpg');
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
            background-repeat: no-repeat;
            background-color: #87ceeb; /* Fallback color: light sky blue */
        }
        .stApp {
            padding: 20px;
            border-radius: 15px;
            background-color: rgba(255, 255, 255, 0.3); /* More transparent overlay */
        }
        .stTextInput > div > div > input {
            background-color: #ffffff !important; /* White background for input */
            color: #000000 !important; /* Black text */
            border-radius: 8px;
            padding: 10px;
            border: 1px solid #e5e7eb;
        }
        .stTextInput > div > div > input::placeholder {
            color: #666666 !important; /* Gray placeholder text */
        }
        .stButton > button {
            background-color: #facc15;
            color: #1f2937;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: bold;
        }
        .stButton > button:hover {
            background-color: #eab308;
        }
        .weather-icon {
            width: 70px;
            height: 70px;
            filter: brightness(1.2);
            box-shadow: 0 0 10px rgba(255, 215, 0, 0.7);
        }
        /* Ensure all text is black */
        h1, h2, h3, h4, h5, h6, p, div, span, label, .stMarkdown, .stText, .stError {
            color: #000000 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Title
    st.title("Weather App")

    # Search input and button
    location = st.text_input("Enter city, state, or country", placeholder="e.g., Mumbai or Austin, Texas, US")
    if st.button("Search"):
        if location:
            weather_data, error = fetch_weather(location)
            if weather_data:
                st.subheader(weather_data['display_location'])
                st.write(f"**Temperature:** {weather_data['temperature']}°C")
                st.write(f"**Weather:** {weather_data['description']}")
                st.write(f"**Humidity:** {weather_data['humidity']}%")
                st.markdown(f"<img src='https://openweathermap.org/img/wn/{weather_data['icon']}@2x.png' class='weather-icon'>", 
                            unsafe_allow_html=True)
            else:
                st.error(error)

    # Display search history
    st.subheader("Recent Searches")
    history = get_history()
    if history:
        for item in history:
            st.write(f"{item['city'].capitalize()} - {item['temperature']}°C, {item['description']} ({item['timestamp']})")
    else:
        st.write("No search history yet.")

if __name__ == "__main__":
    main()
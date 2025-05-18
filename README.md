# Micro-IT-Internship

Weather App 🌞☁️
This is a simple Weather App built with Streamlit. It shows the current weather for any city you search for. The app has a nice background with clouds and a sun, and all text is in black for easy reading.
Features

Search for weather by city, state, or country (e.g., "Mumbai" or "Austin, Texas, US").
Shows temperature, weather description, and humidity.
Displays a weather icon.
Keeps a history of your recent searches (up to 5).
Beautiful background with clouds and sun.

Try the App
Click the button below to use the app:https://weather-app-2706.streamlit.app/


  
    Open Weather App
  


How to Run Locally
If you want to run this app on your computer, follow these steps:

Clone the Repository:

Open your terminal and run:git clone https://github.com/snehithamuddam/weather_app_streamlit.git


Go to the project folder:cd weather_app_streamlit




Install Dependencies:

Make sure you have Python installed.
Install the required packages:pip install -r requirements.txt




Set Up the API Key:

Sign up at OpenWeatherMap to get an API key.
Create a file named config.py in the project folder.
Add your API key to config.py like this:OPENWEATHERMAP_API_KEY = "your_api_key_here"




Run the App:

Start the app with:streamlit run app.py


Open your browser and go to http://localhost:8501 to see the app.



Deployment
This app is deployed on Streamlit Community Cloud. To deploy your own version:

Upload the project to GitHub.
Go to Streamlit Community Cloud and create a new app.
Connect your GitHub repository.
Add your OPENWEATHERMAP_API_KEY in the Advanced settings as an environment variable.
Deploy the app.

Notes

The search history resets when the app restarts on Streamlit Community Cloud because it uses a temporary database.
Make sure to keep your API key safe and don’t upload config.py to GitHub.

Enjoy using the Weather App! 🌞

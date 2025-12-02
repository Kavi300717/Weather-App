from django.shortcuts import render
from django.conf import settings
from django.contrib import messages
import requests
import datetime

def home(request):
    # Default city
    city = 'Mumbai'

    if request.method == 'POST':
        city = request.POST['city']

    # OpenWeatherMap API call
    # Safely get API key, defaulting to None if not found
    openweathermap_api_key = getattr(settings, 'OPENWEATHER_API_KEY', None)
    if not openweathermap_api_key:
        messages.error(request, "OpenWeatherMap API key is not configured.")
        day = datetime.date.today()
        return render(request, 'weatherapp/index.html', {'description': 'N/A', 'icon': '01d', 'temp': 'N/A', 'day': day, 'city': city, 'exception_occurred': True, 'image_url': 'https://images.unsplash.com/photo-1562664377-709f2c337eb1'})

    weather_url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={openweathermap_api_key}'
    weather_params = {'units': 'metric'}

    # Google Custom Search API for city image
    image_url = 'https://images.unsplash.com/photo-1562664377-709f2c337eb1' # Default image
    if getattr(settings, 'GOOGLE_API_KEY', None) and getattr(settings, 'GOOGLE_SEARCH_ENGINE_ID', None):
        try:
            search_query = f"{city} city landmark 1920x1080"
            search_url = "https://www.googleapis.com/customsearch/v1"
            search_params = {
                'key': settings.GOOGLE_API_KEY,
                'cx': settings.GOOGLE_SEARCH_ENGINE_ID,
                'q': search_query,
                'searchType': 'image',
                'num': 1
            }
            search_response = requests.get(search_url, params=search_params)
            search_response.raise_for_status() # Raise an exception for bad status codes
            search_data = search_response.json()
            if "items" in search_data and len(search_data["items"]) > 0:
                image_url = search_data["items"][0]['link']
        except requests.exceptions.RequestException as e:
            print(f"Could not fetch city image: {e}")
            # Silently fail and use the default image

    try:
        response = requests.get(weather_url, params=weather_params)
        response.raise_for_status() # Will raise an HTTPError for bad responses (4xx or 5xx)
        weather_data = response.json()

        description = weather_data['weather'][0]['description']
        icon = weather_data['weather'][0]['icon']
        temp = weather_data['main']['temp']
        day = datetime.date.today()

        return render(request, 'weatherapp/index.html', {'description': description, 'icon': icon, 'temp': temp, 'day': day, 'city': city, 'exception_occurred': False, 'image_url': image_url})

    except (requests.exceptions.RequestException, KeyError):
        exception_occurred = True
        messages.error(request, f'Could not retrieve weather data for "{city}". Please check the city name and try again.')
        day = datetime.date.today()
        # Render with default values but keep the user's city input for context
        return render(request, 'weatherapp/index.html', {'description': 'N/A', 'icon': '01d', 'temp': 'N/A', 'day': day, 'city': city, 'exception_occurred': exception_occurred, 'image_url': image_url})
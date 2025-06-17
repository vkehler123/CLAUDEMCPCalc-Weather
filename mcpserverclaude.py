import math


from mcp.server.fastmcp import FastMCP


from starlette import requests


from weather_server import API_KEY, get_coordinates






# Create an MCP server
mcp = FastMCP("Weather and Calculator")


def clean_result(value, tol=1e-10):
   if isinstance(value, (int, float)):
       if abs(value) < tol:
           return 0
       return None
   return None


class Calculator:
   @mcp.tool()
   def add(a: int, b: int) -> int:
       """Add two numbers"""
       return a + b


   @mcp.tool()
   def subtract(a: int, b: int) -> int:
       """Subtract two numbers"""
       return a - b


   @mcp.tool()
   def multiply(a: int, b: int) -> int:
       """Multiply two numbers"""
       return a * b


   @mcp.tool()
   def divide(a: int, b: int) -> float:
       """Divide two numbers"""
       return a / b


   @mcp.tool()
   def power(a: int, b: int) -> int:
       """One number raised to a power"""
       return a**b


   @mcp.tool()
   def sqrt(a: int) -> float:
       """Square root of one number"""
       return math.sqrt(a)


   @mcp.tool()
   def cosine(a: int) -> float:
       """Cosine of one number"""
       return math.cos(a)


   @mcp.tool()
   def sine(a: int) -> float:
       """Sine of one number"""
       return math.sin(a)


   @mcp.tool()
   def tangent(a: int) -> float:
       """Tangent of one number"""
       return math.tan(a)


   @mcp.tool()
   def acos(a: float) -> float:
       """Inverse cosine of one number"""
       return math.acos(a)


   @mcp.tool()
   def asin(a: float) -> float:
       """Inverse cosine of one number"""
       return math.asin(a)


   # @mcp.tool()
   # def atan(a: float) -> float:
   #     """Inverse cosine of one number"""
   #     return math.atan(a)


       # Add a dynamic greeting resource
   @mcp.resource("greeting://{name}")
   def get_greeting(name: str) -> str:
       """Get a personalized greeting"""
       return f"Hello, {name}!"


class Weather:
   import os
   import requests
   from dotenv import load_dotenv
   from mcp.server.fastmcp import FastMCP


   load_dotenv()
   API_KEY = os.getenv("WEATHER_API_KEY") or ""


   mcp = FastMCP("Weather MCP")


   def get_coordinates(city_name: str):
       url = "http://api.openweathermap.org/geo/1.0/direct"
       params = {"q": city_name, "limit": 1, "appid": API_KEY}
       try:
           response = requests.get(url, params=params)
           response.raise_for_status()
           data = response.json()
           if not data:
               return None, None
           return data[0]["lat"], data[0]["lon"]
       except Exception:
           return None, None


   @mcp.tool()
   def get_weather_forecast(city_name: str) -> dict:
       """Get the current weather and 5-day forecast for a city."""
       city_name = city_name.replace(",", "").strip()


       lat, lon = get_coordinates(city_name)
       if lat is None or lon is None:
           return {"error": f"Could not find location for '{city_name}'."}


       # Current weather
       current_url = "https://api.openweathermap.org/data/2.5/weather"
       current_params = {
           "lat": lat,
           "lon": lon,
           "units": "imperial",
           "appid": API_KEY,
       }
       current_data = requests.get(current_url, params=current_params).json()


       # Forecast (3-hour intervals for 5 days)
       forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
       forecast_params = {
           "lat": lat,
           "lon": lon,
           "units": "imperial",
           "appid": API_KEY,
       }
       forecast_data = requests.get(forecast_url, params=forecast_params).json()


       current_temp = round(current_data.get("main", {}).get("temp", 0))
       current_condition = current_data.get("weather", [{}])[0].get("description", "Unknown").capitalize()


       # Grab 1 forecast per day (noon) from the 3-hour forecasts
       daily_forecast = []
       seen_dates = set()
       for item in forecast_data.get("list", []):
           dt_txt = item["dt_txt"]  # Format: "2025-06-05 12:00:00"
           if "12:00:00" in dt_txt:
               date = dt_txt.split(" ")[0]
               if date not in seen_dates:
                   seen_dates.add(date)
                   temp = round(item["main"]["temp"])
                   desc = item["weather"][0]["description"].capitalize()
                   daily_forecast.append({"date": date, "temp": temp, "condition": desc})
           if len(daily_forecast) >= 5:
               break


       return {
           "city": city_name,
           "current_temp": f"{current_temp}°F",
           "current_condition": current_condition,
           "5_day_forecast": daily_forecast,
       }


   if __name__ == "__main__":
       mcp.run()

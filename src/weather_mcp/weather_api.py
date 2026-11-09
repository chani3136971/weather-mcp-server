"""
Weather API module - לוגיקה לקבלת נתוני מזג אוויר
משתמש ב-Open-Meteo API (חינמי, ללא צורך במפתח)
"""

import httpx
from typing import Dict, Any, Optional
from datetime import datetime


class WeatherAPIError(Exception):
    """שגיאה בקבלת נתוני מזג אוויר."""
    pass


async def get_current_weather_data(
    latitude: float,
    longitude: float,
    location_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    מקבל מזג אוויר נוכחי לפי קואורדינטות.
    
    Args:
        latitude: קו רוחב
        longitude: קו אורך
        location_name: שם המיקום (אופציונלי, לתצוגה)
    
    Returns:
        Dictionary עם נתוני מזג האוויר הנוכחיים
    
    Raises:
        WeatherAPIError: אם יש בעיה בקבלת הנתונים
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "weather_code",
            "wind_speed_10m",
            "wind_direction_10m",
        ],
        "timezone": "auto",
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            current = data["current"]
            
            # פרשנות של קוד מזג האוויר
            weather_description = _get_weather_description(
                current["weather_code"]
            )
            
            # בניית תשובה מעוצבת
            result = {
                "location": location_name or f"{latitude}, {longitude}",
                "time": current["time"],
                "temperature": {
                    "value": current["temperature_2m"],
                    "unit": "°C",
                    "feels_like": current["apparent_temperature"],
                },
                "humidity": {
                    "value": current["relative_humidity_2m"],
                    "unit": "%",
                },
                "wind": {
                    "speed": current["wind_speed_10m"],
                    "direction": current["wind_direction_10m"],
                    "unit": "km/h",
                },
                "precipitation": {
                    "value": current["precipitation"],
                    "unit": "mm",
                },
                "condition": weather_description,
                "weather_code": current["weather_code"],
            }
            
            return result
            
    except httpx.HTTPStatusError as e:
        raise WeatherAPIError(
            f"שגיאת תקשורת עם שרת מזג האוויר: {e.response.status_code}"
        )
    except httpx.RequestError as e:
        raise WeatherAPIError(
            f"בעיה בחיבור לשרת מזג האוויר: {str(e)}"
        )
    except (KeyError, ValueError) as e:
        raise WeatherAPIError(
            f"פורמט תשובה לא צפוי מהשרת: {str(e)}"
        )


async def get_forecast_data(
    latitude: float,
    longitude: float,
    days: int = 7,
    location_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    מקבל תחזית מזג אוויר למספר ימים.
    
    Args:
        latitude: קו רוחב
        longitude: קו אורך
        days: מספר ימים לתחזית (1-16)
        location_name: שם המיקום (אופציונלי)
    
    Returns:
        Dictionary עם תחזית מזג האוויר
    
    Raises:
        WeatherAPIError: אם יש בעיה בקבלת הנתונים
        ValueError: אם מספר הימים לא בטווח התקין
    """
    if not 1 <= days <= 16:
        raise ValueError("מספר הימים חייב להיות בין 1 ל-16")
    
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": [
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "precipitation_probability_max",
            "wind_speed_10m_max",
        ],
        "timezone": "auto",
        "forecast_days": days,
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            daily = data["daily"]
            
            # בניית רשימת ימים
            forecast_days = []
            for i in range(len(daily["time"])):
                day_data = {
                    "date": daily["time"][i],
                    "temperature": {
                        "max": daily["temperature_2m_max"][i],
                        "min": daily["temperature_2m_min"][i],
                        "unit": "°C",
                    },
                    "precipitation": {
                        "sum": daily["precipitation_sum"][i],
                        "probability": daily["precipitation_probability_max"][i],
                        "unit": "mm",
                    },
                    "wind": {
                        "max_speed": daily["wind_speed_10m_max"][i],
                        "unit": "km/h",
                    },
                    "condition": _get_weather_description(
                        daily["weather_code"][i]
                    ),
                    "weather_code": daily["weather_code"][i],
                }
                forecast_days.append(day_data)
            
            result = {
                "location": location_name or f"{latitude}, {longitude}",
                "forecast_days": days,
                "daily_forecast": forecast_days,
            }
            
            return result
            
    except httpx.HTTPStatusError as e:
        raise WeatherAPIError(
            f"שגיאת תקשורת עם שרת מזג האוויר: {e.response.status_code}"
        )
    except httpx.RequestError as e:
        raise WeatherAPIError(
            f"בעיה בחיבור לשרת מזג האוויר: {str(e)}"
        )
    except (KeyError, ValueError, IndexError) as e:
        raise WeatherAPIError(
            f"פורמט תשובה לא צפוי מהשרת: {str(e)}"
        )


def _get_weather_description(code: int) -> str:
    """
    ממיר קוד מזג אוויר WMO לתיאור קריא.
    
    מבוסס על: https://open-meteo.com/en/docs
    WMO Weather interpretation codes
    """
    weather_codes = {
        0: "שמיים בהירים",
        1: "בהיר ברובו",
        2: "מעונן חלקית",
        3: "מעונן",
        45: "ערפל",
        48: "ערפל קפוא",
        51: "טפטוף קל",
        53: "טפטוף בינוני",
        55: "טפטוף כבד",
        56: "טפטוף קפוא קל",
        57: "טפטוף קפוא כבד",
        61: "גשם קל",
        63: "גשם בינוני",
        65: "גשם כבד",
        66: "גשם קפוא קל",
        67: "גשם קפוא כבד",
        71: "שלג קל",
        73: "שלג בינוני",
        75: "שלג כבד",
        77: "גרגירי שלג",
        80: "ממטרי גשם קלים",
        81: "ממטרי גשם בינוניים",
        82: "ממטרי גשם חזקים",
        85: "ממטרי שלג קלים",
        86: "ממטרי שלג כבדים",
        95: "סופת רעמים",
        96: "סופת רעמים עם ברד קל",
        99: "סופת רעמים עם ברד כבד",
    }
    
    return weather_codes.get(code, f"מזג אוויר לא ידוע (קוד: {code})")

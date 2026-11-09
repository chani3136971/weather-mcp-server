"""
Weather Forecast MCP Server - שרת MCP ראשי
מספק כלים (Tools) לקבלת מזג אוויר באמצעות Open-Meteo API
"""

from fastmcp import FastMCP
from typing import Optional
import logging

from .weather_api import (
    get_current_weather_data,
    get_forecast_data,
    WeatherAPIError,
)
from .geocoding import (
    get_coordinates,
    validate_coordinates,
    GeocodingError,
)

# הגדרת logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# יצירת שרת MCP
mcp = FastMCP("Weather Forecast MCP Server")


@mcp.tool()
async def get_openmeteo_current_weather(location: str) -> dict:
    """
    קבלת מזג אוויר נוכחי מ-Open-Meteo לפי שם עיר.
    
    🌍 מקור: Open-Meteo API (נתונים חופשיים ופתוחים)
    🎯 שימוש: כאשר המשתמש רוצה נתונים מפורטים או בעברית
    
    מחזיר טמפרטורה נוכחית, תחושה, לחות, רוח, משקעים ותיאור מזג האוויר.
    תומך בערים בכל העולם, כולל שמות בעברית.
    
    Args:
        location: שם העיר (למשל: "תל אביב", "Jerusalem", "New York", "London")
    
    Returns:
        נתוני מזג האוויר הנוכחיים כולל:
        - טמפרטורה ותחושת טמפרטורה
        - לחות יחסית
        - מהירות וכיוון רוח
        - משקעים
        - תיאור מזג האוויר
    
    Examples:
        >>> await get_current_weather("תל אביב")
        >>> await get_current_weather("Jerusalem")
    """
    try:
        logger.info(f"מבצע חיפוש מזג אוויר עבור: {location}")
        
        # המרת שם העיר לקואורדינטות
        geo_data = await get_coordinates(location)
        logger.info(
            f"נמצאה עיר: {geo_data['name']}, {geo_data['country']} "
            f"({geo_data['latitude']}, {geo_data['longitude']})"
        )
        
        # קבלת נתוני מזג אוויר
        weather_data = await get_current_weather_data(
            latitude=geo_data["latitude"],
            longitude=geo_data["longitude"],
            location_name=f"{geo_data['name']}, {geo_data['country']}",
        )
        
        logger.info(f"נתוני מזג אוויר התקבלו בהצלחה עבור {location}")
        return weather_data
        
    except GeocodingError as e:
        error_msg = f"שגיאה במציאת העיר: {str(e)}"
        logger.error(error_msg)
        return {
            "error": error_msg,
            "type": "geocoding_error",
            "location_searched": location,
        }
    except WeatherAPIError as e:
        error_msg = f"שגיאה בקבלת נתוני מזג אוויר: {str(e)}"
        logger.error(error_msg)
        return {
            "error": error_msg,
            "type": "weather_api_error",
            "location": location,
        }
    except Exception as e:
        error_msg = f"שגיאה לא צפויה: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "error": error_msg,
            "type": "unexpected_error",
            "location": location,
        }


@mcp.tool()
async def get_openmeteo_forecast(location: str, days: int = 7) -> dict:
    """
    קבלת תחזית מזג אוויר מ-Open-Meteo למספר ימים קדימה.
    
    מחזיר תחזית יומית הכוללת טמפרטורות מקסימום ומינימום, משקעים,
    הסתברות לגשם ומהירות רוח מקסימלית.
    
    Args:
        location: שם העיר (למשל: "תל אביב", "Haifa", "Eilat")
        days: מספר ימים לתחזית (1-16, ברירת מחדל: 7)
    
    Returns:
        תחזית מזג אוויר יומית עבור המספר הימים המבוקש:
        - טמפרטורה מקסימלית ומינימלית
        - סך משקעים והסתברות לגשם
        - מהירות רוח מקסימלית
        - תיאור מזג האוויר
    
    Examples:
        >>> await get_weather_forecast("ירושלים")
        >>> await get_weather_forecast("Eilat", days=3)
    """
    try:
        logger.info(f"מבצע חיפוש תחזית עבור: {location} ({days} ימים)")
        
        # בדיקת תקינות מספר הימים
        if not isinstance(days, int) or not 1 <= days <= 16:
            return {
                "error": "מספר הימים חייב להיות מספר שלם בין 1 ל-16",
                "type": "invalid_parameter",
                "days_requested": days,
            }
        
        # המרת שם העיר לקואורדינטות
        geo_data = await get_coordinates(location)
        logger.info(
            f"נמצאה עיר: {geo_data['name']}, {geo_data['country']}"
        )
        
        # קבלת תחזית
        forecast_data = await get_forecast_data(
            latitude=geo_data["latitude"],
            longitude=geo_data["longitude"],
            days=days,
            location_name=f"{geo_data['name']}, {geo_data['country']}",
        )
        
        logger.info(f"תחזית התקבלה בהצלחה עבור {location}")
        return forecast_data
        
    except GeocodingError as e:
        error_msg = f"שגיאה במציאת העיר: {str(e)}"
        logger.error(error_msg)
        return {
            "error": error_msg,
            "type": "geocoding_error",
            "location_searched": location,
        }
    except WeatherAPIError as e:
        error_msg = f"שגיאה בקבלת תחזית: {str(e)}"
        logger.error(error_msg)
        return {
            "error": error_msg,
            "type": "weather_api_error",
            "location": location,
        }
    except ValueError as e:
        error_msg = f"פרמטר לא תקין: {str(e)}"
        logger.error(error_msg)
        return {
            "error": error_msg,
            "type": "validation_error",
            "location": location,
            "days": days,
        }
    except Exception as e:
        error_msg = f"שגיאה לא צפויה: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "error": error_msg,
            "type": "unexpected_error",
            "location": location,
        }


@mcp.tool()
async def get_openmeteo_by_coordinates(
    latitude: float,
    longitude: float
) -> dict:
    """
    קבלת מזג אוויר נוכחי מ-Open-Meteo לפי קואורדינטות GPS.
    
    שימושי כאשר יש לך קואורדינטות מדויקות של מיקום ולא שם עיר.
    
    Args:
        latitude: קו רוחב (Latitude) בין -90 ל-90
        longitude: קו אורך (Longitude) בין -180 ל-180
    
    Returns:
        נתוני מזג האוויר הנוכחיים למיקום הגיאוגרפי המבוקש
    
    Examples:
        >>> await get_weather_by_coordinates(32.0853, 34.7818)  # תל אביב
        >>> await get_weather_by_coordinates(31.7683, 35.2137)  # ירושלים
    """
    try:
        logger.info(f"מבצע חיפוש מזג אוויר לקואורדינטות: {latitude}, {longitude}")
        
        # בדיקת תקינות הקואורדינטות
        validate_coordinates(latitude, longitude)
        
        # קבלת נתוני מזג אוויר
        weather_data = await get_current_weather_data(
            latitude=latitude,
            longitude=longitude,
        )
        
        logger.info(f"נתוני מזג אוויר התקבלו בהצלחה")
        return weather_data
        
    except ValueError as e:
        error_msg = f"קואורדינטות לא תקינות: {str(e)}"
        logger.error(error_msg)
        return {
            "error": error_msg,
            "type": "validation_error",
            "latitude": latitude,
            "longitude": longitude,
        }
    except WeatherAPIError as e:
        error_msg = f"שגיאה בקבלת נתוני מזג אוויר: {str(e)}"
        logger.error(error_msg)
        return {
            "error": error_msg,
            "type": "weather_api_error",
            "latitude": latitude,
            "longitude": longitude,
        }
    except Exception as e:
        error_msg = f"שגיאה לא צפויה: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "error": error_msg,
            "type": "unexpected_error",
            "latitude": latitude,
            "longitude": longitude,
        }


if __name__ == "__main__":
    # הרצת השרת
    logger.info("מפעיל שרת Weather Forecast MCP...")
    mcp.run()

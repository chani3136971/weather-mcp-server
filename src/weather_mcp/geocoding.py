"""
Geocoding module - המרת שמות ערים לקואורדינטות GPS
משתמש ב-Open-Meteo Geocoding API
"""

import httpx
from typing import Optional, Dict, Any


class GeocodingError(Exception):
    """שגיאה בתהליך המרת כתובת לקואורדינטות."""
    pass


async def get_coordinates(city_name: str) -> Dict[str, Any]:
    """
    מקבל שם עיר ומחזיר קואורדינטות GPS ופרטים נוספים.
    
    Args:
        city_name: שם העיר לחיפוש (תומך בעברית, אנגלית ושפות נוספות)
    
    Returns:
        Dictionary עם הפרטים הבאים:
        - latitude: קו רוחב
        - longitude: קו אורך
        - name: שם העיר
        - country: שם המדינה
        - admin1: מדינה/מחוז (אם זמין)
    
    Raises:
        GeocodingError: אם העיר לא נמצאה או יש בעיית תקשורת
    """
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": city_name,
        "count": 1,  # מספיק תוצאה אחת - הרלוונטית ביותר
        "language": "he",  # עדיפות לשמות בעברית
        "format": "json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # בדיקה אם נמצאו תוצאות
            if "results" not in data or not data["results"]:
                raise GeocodingError(
                    f"העיר '{city_name}' לא נמצאה. "
                    f"אנא בדוק את האיות או נסה שם אנגלי."
                )
            
            # לקיחת התוצאה הראשונה (הרלוונטית ביותר)
            result = data["results"][0]
            
            return {
                "latitude": result["latitude"],
                "longitude": result["longitude"],
                "name": result["name"],
                "country": result.get("country", ""),
                "admin1": result.get("admin1", ""),  # מדינה/אזור
            }
            
    except httpx.HTTPStatusError as e:
        raise GeocodingError(
            f"שגיאת תקשורת עם שרת הגיאוקודינג: {e.response.status_code}"
        )
    except httpx.RequestError as e:
        raise GeocodingError(
            f"בעיה בחיבור לשרת הגיאוקודינג: {str(e)}"
        )
    except KeyError as e:
        raise GeocodingError(
            f"פורמט תשובה לא צפוי מהשרת: חסר שדה {str(e)}"
        )


def validate_coordinates(latitude: float, longitude: float) -> None:
    """
    מוודא שהקואורדינטות תקפות.
    
    Args:
        latitude: קו רוחב (-90 עד 90)
        longitude: קו אורך (-180 עד 180)
    
    Raises:
        ValueError: אם הקואורדינטות לא בטווח התקין
    """
    if not -90 <= latitude <= 90:
        raise ValueError(
            f"קו רוחב לא תקין: {latitude}. "
            f"הערך חייב להיות בין -90 ל-90"
        )
    
    if not -180 <= longitude <= 180:
        raise ValueError(
            f"קו אורך לא תקין: {longitude}. "
            f"הערך חייב להיות בין -180 ל-180"
        )

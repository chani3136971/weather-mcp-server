"""
טסטים לשרת Weather MCP
בודק את כל הפונקציות הליבה של הפרויקט
"""

import asyncio
import sys
from pathlib import Path

# הוספת src לנתיב
sys.path.insert(0, str(Path(__file__).parent / "src"))

from weather_mcp.geocoding import get_coordinates, validate_coordinates, GeocodingError
from weather_mcp.weather_api import get_current_weather_data, get_forecast_data, WeatherAPIError
from weather_mcp.server import get_openmeteo_current_weather, get_openmeteo_forecast, get_openmeteo_by_coordinates


async def test_geocoding():
    """בדיקת המרת שמות ערים לקואורדינטות"""
    print("\n" + "="*60)
    print("🧪 טסט 1: Geocoding - המרת שמות ערים")
    print("="*60)
    
    # טסט 1.1: עיר בעברית
    print("\n1.1 בודק חיפוש עיר בעברית...")
    try:
        result = await get_coordinates("תל אביב")
        assert "latitude" in result
        assert "longitude" in result
        assert "name" in result
        assert 32.0 < result["latitude"] < 32.2  # תל אביב בערך
        print(f"   ✅ הצלחה: {result['name']}, {result['country']}")
        print(f"   📍 {result['latitude']}, {result['longitude']}")
    except Exception as e:
        print(f"   ❌ נכשל: {e}")
        return False
    
    # טסט 1.2: עיר באנגלית
    print("\n1.2 בודק חיפוש עיר באנגלית...")
    try:
        result = await get_coordinates("Jerusalem")
        assert "latitude" in result
        assert 31.7 < result["latitude"] < 31.9  # ירושלים בערך
        print(f"   ✅ הצלחה: {result['name']}")
    except Exception as e:
        print(f"   ❌ נכשל: {e}")
        return False
    
    # טסט 1.3: עיר לא קיימת
    print("\n1.3 בודק טיפול בעיר לא קיימת...")
    try:
        await get_coordinates("עיר_שלא_קיימת_12345")
        print(f"   ❌ נכשל: היה צריך לזרוק שגיאה")
        return False
    except GeocodingError:
        print(f"   ✅ הצלחה: זרק GeocodingError כצפוי")
    
    # טסט 1.4: וולידציה של קואורדינטות
    print("\n1.4 בודק וולידציה של קואורדינטות...")
    try:
        validate_coordinates(32.0, 34.0)  # תקין
        validate_coordinates(200, 34.0)   # לא תקין - צריך לזרוק שגיאה
        print(f"   ❌ נכשל: היה צריך לזרוק ValueError")
        return False
    except ValueError:
        print(f"   ✅ הצלחה: זיהה קואורדינטות לא תקינות")
    
    print("\n✅ כל טסטי Geocoding עברו בהצלחה!")
    return True


async def test_weather_api():
    """בדיקת קבלת נתוני מזג אוויר"""
    print("\n" + "="*60)
    print("🧪 טסט 2: Weather API - קבלת נתוני מזג אוויר")
    print("="*60)
    
    # טסט 2.1: מזג אוויר נוכחי
    print("\n2.1 בודק קבלת מזג אוויר נוכחי...")
    try:
        result = await get_current_weather_data(
            latitude=32.0853,
            longitude=34.7818,
            location_name="תל אביב"
        )
        assert "temperature" in result
        assert "humidity" in result
        assert "wind" in result
        assert "condition" in result
        assert isinstance(result["temperature"]["value"], (int, float))
        assert 0 <= result["humidity"]["value"] <= 100
        print(f"   ✅ הצלחה!")
        print(f"   🌡️  {result['temperature']['value']}°C")
        print(f"   💧 {result['humidity']['value']}%")
        print(f"   ☁️  {result['condition']}")
    except Exception as e:
        print(f"   ❌ נכשל: {e}")
        return False
    
    # טסט 2.2: תחזית לימים
    print("\n2.2 בודק תחזית ל-3 ימים...")
    try:
        result = await get_forecast_data(
            latitude=31.7683,
            longitude=35.2137,
            days=3,
            location_name="ירושלים"
        )
        assert "daily_forecast" in result
        assert len(result["daily_forecast"]) == 3
        assert "temperature" in result["daily_forecast"][0]
        assert "max" in result["daily_forecast"][0]["temperature"]
        print(f"   ✅ הצלחה!")
        print(f"   📅 קיבלנו {len(result['daily_forecast'])} ימים")
        print(f"   🌡️  יום ראשון: {result['daily_forecast'][0]['temperature']['max']}°C")
    except Exception as e:
        print(f"   ❌ נכשל: {e}")
        return False
    
    # טסט 2.3: תחזית עם פרמטר לא תקין
    print("\n2.3 בודק טיפול בפרמטר לא תקין...")
    try:
        await get_forecast_data(32.0, 34.0, days=20)  # מעל 16
        print(f"   ❌ נכשל: היה צריך לזרוק ValueError")
        return False
    except ValueError:
        print(f"   ✅ הצלחה: זיהה פרמטר לא תקין")
    
    print("\n✅ כל טסטי Weather API עברו בהצלחה!")
    return True


async def test_mcp_tools():
    """בדיקת כלי MCP"""
    print("\n" + "="*60)
    print("🧪 טסט 3: MCP Tools - כלי השרת")
    print("="*60)
    
    # טסט 3.1: get_openmeteo_current_weather
    print("\n3.1 בודק get_openmeteo_current_weather...")
    try:
        result = await get_openmeteo_current_weather("חיפה")
        assert "temperature" in result
        assert "error" not in result
        print(f"   ✅ הצלחה: {result['location']}")
        print(f"   🌡️  {result['temperature']['value']}°C")
    except Exception as e:
        print(f"   ❌ נכשל: {e}")
        return False
    
    # טסט 3.2: get_openmeteo_forecast
    print("\n3.2 בודק get_openmeteo_forecast...")
    try:
        result = await get_openmeteo_forecast("Eilat", days=5)
        assert "daily_forecast" in result
        assert len(result["daily_forecast"]) == 5
        assert "error" not in result
        print(f"   ✅ הצלחה: תחזית ל-{len(result['daily_forecast'])} ימים")
    except Exception as e:
        print(f"   ❌ נכשל: {e}")
        return False
    
    # טסט 3.3: get_openmeteo_by_coordinates
    print("\n3.3 בודק get_openmeteo_by_coordinates...")
    try:
        result = await get_openmeteo_by_coordinates(32.0853, 34.7818)
        assert "temperature" in result
        assert "error" not in result
        print(f"   ✅ הצלחה!")
    except Exception as e:
        print(f"   ❌ נכשל: {e}")
        return False
    
    # טסט 3.4: טיפול בשגיאות
    print("\n3.4 בודק טיפול בשגיאות...")
    try:
        result = await get_openmeteo_current_weather("עיר_לא_קיימת_999")
        assert "error" in result
        assert result["type"] == "geocoding_error"
        print(f"   ✅ הצלחה: החזיר שגיאה מובנית")
    except Exception as e:
        print(f"   ❌ נכשל: {e}")
        return False
    
    print("\n✅ כל טסטי MCP Tools עברו בהצלחה!")
    return True


async def run_all_tests():
    """הרצת כל הטסטים"""
    print("\n" + "="*60)
    print("🚀 מריץ טסטים לשרת Weather MCP")
    print("="*60)
    
    results = []
    
    # הרצת כל הטסטים
    results.append(await test_geocoding())
    results.append(await test_weather_api())
    results.append(await test_mcp_tools())
    
    # סיכום
    print("\n" + "="*60)
    print("📊 סיכום טסטים")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n✅ עברו: {passed}/{total}")
    print(f"❌ נכשלו: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 כל הטסטים עברו בהצלחה!")
        print("✅ השרת מוכן לשימוש!")
        return 0
    else:
        print("\n⚠️  יש טסטים שנכשלו")
        print("❌ יש לתקן את הבעיות לפני השימוש")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)

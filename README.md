# Weather Forecast MCP Server

שרת MCP (Model Context Protocol) בפייתון המספק תחזית מזג אוויר באמצעות Open-Meteo API.

## תכונות

- 🌡️ קבלת מזג אוויר נוכחי לפי שם עיר או קואורדינטות
- 📅 תחזית מזג אוויר ל-7 יום
- 🌍 תמיכה בערים ברחבי העולם
- ⚡ API חינמי ללא צורך במפתח API
- 🛡️ טיפול מלא בשגיאות

## התקנה

### דרישות מוקדמות
- Python 3.10 או גרסה חדשה יותר
- uv (מומלץ) או pip

### התקנה עם uv
```bash
# התקנת uv אם לא מותקן
# Windows (PowerShell):
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# התקנת התלויות
uv pip install -e .
```

### התקנה עם pip
```bash
pip install -e .
```

## שימוש

### הרצת השרת ישירות
```bash
# עם uv
uvx --from . weather-mcp

# עם python
python -m weather_mcp.server
```

### הרצה עם stdio (לשימוש עם Kiro או Claude Desktop)
```bash
uv --directory . run weather_mcp.server
```

## חיבור ל-Kiro IDE

הוסף את השרת ל-MCP config שלך (`.kiro/settings/mcp.json`):

```json
{
  "mcpServers": {
    "weather": {
      "command": "uv",
      "args": [
        "--directory",
        "c:\\Users\\User\\Desktop\\מחשבים\\פרקטיקוד\\תחזית מזג אוויר",
        "run",
        "weather_mcp.server"
      ]
    }
  }
}
```

## הכלים הזמינים (Tools)

### 1. `get_current_weather`
קבלת מזג אוויר נוכחי

**פרמטרים:**
- `location` (string): שם העיר (למשל: "תל אביב", "Jerusalem", "New York")

**דוגמה:**
```json
{
  "location": "תל אביב"
}
```

### 2. `get_weather_forecast`
קבלת תחזית מזג אוויר ל-7 ימים

**פרמטרים:**
- `location` (string): שם העיר
- `days` (int, optional): מספר ימים (1-7, ברירת מחדל: 7)

**דוגמה:**
```json
{
  "location": "Jerusalem",
  "days": 5
}
```

### 3. `get_weather_by_coordinates`
קבלת מזג אוויר לפי קואורדינטות GPS

**פרמטרים:**
- `latitude` (float): קו רוחב
- `longitude` (float): קו אורך

**דוגמה:**
```json
{
  "latitude": 32.0853,
  "longitude": 34.7818
}
```

## מבנה הפרויקט

```
weather-forecast-mcp/
├── src/
│   └── weather_mcp/
│       ├── __init__.py
│       ├── server.py          # שרת MCP ראשי
│       ├── weather_api.py     # לוגיקת API
│       └── geocoding.py       # המרת שמות ערים לקואורדינטות
├── pyproject.toml             # הגדרות פרויקט ותלויות
└── README.md
```

## API שבשימוש

השרת משתמש ב-[Open-Meteo API](https://open-meteo.com/) - שירות חינמי וללא צורך במפתח API.

## טיפול בשגיאות

השרת מטפל באופן אוטומטי במצבי שגיאה:
- ❌ שם עיר לא קיים
- ❌ בעיות רשת
- ❌ קואורדינטות לא תקינות
- ❌ פרמטרים לא תקפים

## דוגמאות שימוש

לאחר חיבור השרת ל-Kiro, ניתן לשאול:

```
"מה מזג האוויר בתל אביב?"
"תן לי תחזית ל-5 ימים בירושלים"
"מה הטמפרטורה בקואורדינטות 32.0853, 34.7818?"
```

## רישיון

MIT License

import os
import sqlite3
import random
import requests
from functools import wraps
from datetime import timedelta, date
from urllib.parse import quote_plus
from flask import Flask, jsonify, redirect, render_template_string, request, session, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "ashplex_secret")
app.permanent_session_lifetime = timedelta(days=30)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DATABASE_PATH", os.path.join("/tmp", "ashplex_users.db"))

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "ashutosh")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Ashplex@123")
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")

def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = db()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'customer'
    )
    """)

    cur.execute("PRAGMA table_info(users)")
    user_cols = [row["name"] for row in cur.fetchall()]
    required_user_cols = {"id", "username", "password", "role"}

    if not required_user_cols.issubset(set(user_cols)):
        cur.execute("DROP TABLE IF EXISTS users")
        cur.execute("""
        CREATE TABLE users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT DEFAULT 'customer'
        )
        """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_stats(
        username TEXT PRIMARY KEY,
        total_plays INTEGER DEFAULT 0,
        today_plays INTEGER DEFAULT 0,
        total_rewards INTEGER DEFAULT 0,
        last_reward_date TEXT DEFAULT '',
        last_play_date TEXT DEFAULT ''
    )
    """)

    cur.execute("PRAGMA table_info(user_stats)")
    stat_cols = [row["name"] for row in cur.fetchall()]
    required_stat_cols = {
        "username",
        "total_plays",
        "today_plays",
        "total_rewards",
        "last_reward_date",
        "last_play_date"
    }

    if not required_stat_cols.issubset(set(stat_cols)):
        cur.execute("DROP TABLE IF EXISTS user_stats")
        cur.execute("""
        CREATE TABLE user_stats(
            username TEXT PRIMARY KEY,
            total_plays INTEGER DEFAULT 0,
            today_plays INTEGER DEFAULT 0,
            total_rewards INTEGER DEFAULT 0,
            last_reward_date TEXT DEFAULT '',
            last_play_date TEXT DEFAULT ''
        )
        """)

    cur.execute("SELECT * FROM users WHERE role='developer'")
    dev = cur.fetchone()

    if not dev:
        cur.execute(
            "INSERT OR IGNORE INTO users(username,password,role) VALUES(?,?,?)",
            (ADMIN_USERNAME, ADMIN_PASSWORD, "developer")
        )
    else:
        cur.execute(
            "UPDATE users SET username=?, password=? WHERE role='developer'",
            (ADMIN_USERNAME, ADMIN_PASSWORD)
        )

    con.commit()
    con.close()

init_db()


LANDING_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>ASHPLEX</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}
body{
  min-height:100vh;color:white;background:
  radial-gradient(circle at 20% 0%,rgba(250,35,59,.35),transparent 32%),
  radial-gradient(circle at 80% 10%,rgba(29,185,84,.28),transparent 35%),
  linear-gradient(180deg,#171820,#050506 65%,#000);
  display:flex;align-items:center;justify-content:center;padding:24px;
}
.wrap{max-width:980px;width:100%;display:grid;grid-template-columns:1.1fr .9fr;gap:28px;align-items:center}
.card{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.12);border-radius:34px;padding:34px;box-shadow:0 35px 100px rgba(0,0,0,.45)}
.logo{font-size:28px;font-weight:900;margin-bottom:18px}.logo span{color:#ff2d55}
h1{font-size:62px;line-height:.98;letter-spacing:-2px;margin-bottom:18px}
p{color:#cfcfd8;font-size:17px;line-height:1.65}
.actions{display:flex;gap:14px;margin-top:28px;flex-wrap:wrap}
.btn{border:0;border-radius:999px;padding:15px 24px;font-weight:900;text-decoration:none;display:inline-block}
.primary{background:#ff2d55;color:white}.secondary{background:rgba(255,255,255,.10);color:white}
.phone-preview{min-height:430px;border-radius:36px;background:linear-gradient(135deg,#ff2d55,#1db954);padding:22px;display:flex;flex-direction:column;justify-content:space-between}
.album{height:240px;border-radius:28px;background:rgba(0,0,0,.35);display:flex;align-items:center;justify-content:center;font-size:72px}
.player{background:rgba(0,0,0,.35);border-radius:24px;padding:18px}
@media(max-width:850px){.wrap{grid-template-columns:1fr}h1{font-size:42px}.phone-preview{min-height:310px}}

.hero-banner{
    padding:40px;
    border-radius:28px;
    background:linear-gradient(135deg,#121212,#1f1f1f,#2b0f18);
    margin-bottom:30px;
    border:1px solid rgba(255,255,255,0.08);
    box-shadow:0 10px 40px rgba(0,0,0,0.5);
}
.hero-banner h1{
    font-size:48px;
    font-weight:800;
    color:white;
    margin-bottom:10px;
}
.hero-banner h2{
    font-size:28px;
    color:#ff2d55;
    margin-bottom:14px;
}
.hero-banner p{
    color:#bdbdbd;
    font-size:17px;
    max-width:800px;
    line-height:1.7;
}

</style>
</head>
<body>
<div class="wrap">
  <div class="card">
    <div class="logo">ASH<span>PLEX</span></div>
    <h1>Your Mood.<br>Your Music.<br>Your World.</h1>
    <p>AI mood based music platform with latest trending songs, 90s classics, playlist search, like/share, rewards, premium plan, and developer analytics.</p>
    <div class="actions">
      <a class="btn primary" href="/home">Open ASHPLEX</a>
      <a class="btn secondary" href="/login">Login / Save Account</a>
    </div>
  </div>
  <div class="phone-preview">
    <div class="album">🎧</div>
    <div class="player">
      <h2>ASHPLEX</h2>
      <p>Search • Play • Like • Share</p>
    </div>
  </div>
</div>
</body>
</html>
"""

LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>ASHPLEX Login</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}
body{
  min-height:100vh;background:
  radial-gradient(circle at 20% 0%,rgba(250,35,59,.30),transparent 34%),
  linear-gradient(180deg,#171820,#050506 65%,#000);
  color:white;display:flex;align-items:center;justify-content:center;padding:20px;
}
.box{width:min(460px,100%);background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.12);border-radius:32px;padding:30px;box-shadow:0 30px 90px rgba(0,0,0,.5)}
.logo{font-size:28px;font-weight:900;margin-bottom:12px}.logo span{color:#ff2d55}
h1{font-size:32px;margin-bottom:10px}
p{color:#aaa;line-height:1.5;margin-bottom:20px}
label{display:block;color:#ccc;margin-bottom:8px;font-weight:700}
input{width:100%;padding:16px 18px;border-radius:18px;border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.09);color:white;outline:none;font-size:16px;margin-bottom:12px}
button,.gmail{width:100%;border:0;border-radius:999px;background:#ff2d55;color:white;padding:15px;margin-top:10px;font-weight:900;font-size:16px;cursor:pointer;text-align:center;text-decoration:none;display:block}
.gmail{background:white;color:#111}
.err{color:#ff9aaa;margin-top:12px}
.otpbox{background:rgba(255,255,255,.08);border:1px dashed rgba(255,255,255,.18);border-radius:18px;padding:12px;margin:14px 0;color:#ffcf70}
.small{color:#888;font-size:13px;margin-top:16px}
.divider{display:flex;align-items:center;gap:10px;margin:18px 0;color:#aaa}.divider:before,.divider:after{content:"";flex:1;height:1px;background:rgba(255,255,255,.12)}
</style>
</head>
<body>
<div class="box">
  <div class="logo">ASH<span>PLEX</span></div>
  <h1>Login to ASHPLEX</h1>
  <p>Use mobile OTP or Gmail login. User data will be saved in ASHPLEX database.</p>

  {% if step == "phone" %}
  <form method="POST" action="/send-otp">
    <label>Mobile Number</label>
    <input name="phone" placeholder="Example: 9876543210" inputmode="numeric" maxlength="10" required>
    <button>Send OTP</button>
  </form>

  <div class="divider">OR</div>
  <a class="gmail" href="/gmail-login">📧 Continue with Gmail</a>
  {% endif %}

  {% if step == "otp" %}
  <form method="POST" action="/verify-otp">
    <label>Enter OTP sent to {{phone}}</label>
    <input name="otp" placeholder="Enter 6 digit OTP" inputmode="numeric" maxlength="6" required>
    <button>Verify OTP</button>
  </form>
  <div class="otpbox">Demo OTP: <b>{{demo_otp}}</b><br>Real SMS OTP ke liye Firebase/Twilio config add karna hoga.</div>
  <a class="gmail" href="/login">Change Number</a>
  {% endif %}

  {% if error %}<div class="err">{{error}}</div>{% endif %}
  <div class="small">Note: Real OTP/Gmail OAuth needs Firebase or Google OAuth credentials. Current version shows teacher-demo flow.</div>
</div>
</body>
</html>
"""


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect("/")
        return f(*args, **kwargs)
    return wrapper

def developer_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect("/")
        if session.get("role") != "developer":
            return redirect("/home")
        return f(*args, **kwargs)
    return wrapper

def ai_mood_query(mood="trending", level="medium"):
    mood = (mood or "trending").lower()
    level = (level or "medium").lower()

    mood_map = {
        "trending": {
            "low": "arijit singh",
            "medium": "arijit singh|vishal mishra|shreya ghoshal|bollywood hits",
            "high": "badshah|neha kakkar|bollywood dance"
        },
        "viral": {
            "low": "anuv jain",
            "medium": "arijit singh|anuv jain|vishal mishra",
            "high": "badshah|neha kakkar|bollywood dance"
        },
        "new": {
            "low": "vishal mishra",
            "medium": "vishal mishra|arijit singh|shreya ghoshal",
            "high": "bollywood hits|badshah|neha kakkar"
        },
        "classic90s": {
            "low": "kumar sanu",
            "medium": "kumar sanu|udit narayan|alka yagnik|sonu nigam",
            "high": "udit narayan|alka yagnik|abhijeet"
        },
        "happy": {
            "low": "udit narayan",
            "medium": "bollywood happy|udit narayan|abhijeet",
            "high": "bollywood dance|badshah|neha kakkar"
        },
        "sad": {
            "low": "sonu nigam",
            "medium": "arijit singh sad|sonu nigam|kk",
            "high": "arijit singh heartbreak|vishal mishra"
        },
        "romantic": {
            "low": "kumar sanu romantic",
            "medium": "arijit singh romantic|kumar sanu|alka yagnik",
            "high": "arijit singh|shreya ghoshal|bollywood love"
        },
        "focus": {
            "low": "lofi hindi",
            "medium": "lofi hindi|instrumental hindi",
            "high": "deep focus instrumental"
        },
        "relax": {
            "low": "anuv jain",
            "medium": "anuv jain|arijit singh acoustic|sonu nigam",
            "high": "chill hindi|lofi hindi"
        },
        "workout": {
            "low": "bollywood dance",
            "medium": "badshah|bollywood dance|neha kakkar",
            "high": "badshah|yo yo honey singh|bollywood workout"
        },
        "angry": {
            "low": "bollywood rock",
            "medium": "badshah|yo yo honey singh",
            "high": "bollywood bass|badshah"
        }
    }

    return mood_map.get(mood, mood_map["trending"]).get(level, mood_map["trending"]["medium"])

def youtube_search_url(title="", artist="", query=""):
    if query:
        search_text = query + " song"
    else:
        search_text = f"{title} {artist} song"
    return "https://www.youtube.com/results?search_query=" + quote_plus(search_text)

def youtube_embed_url(query=""):
    return "https://www.youtube.com/embed?listType=search&list=" + quote_plus(query + " song")

def get_youtube_video(query="arijit song"):
    """
    Uses official YouTube Data API v3 to get exact videoId.
    This fixes 'This video is unavailable' caused by search-list iframe embed.
    """
    if not YOUTUBE_API_KEY:
        return {
            "ok": False,
            "error": "YOUTUBE_API_KEY missing",
            "video_id": "",
            "title": "",
            "channel": "",
            "embed_url": "",
            "watch_url": youtube_search_url(query=query)
        }

    try:
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": query + " song",
            "type": "video",
            "maxResults": 1,
            "videoEmbeddable": "true",
            "safeSearch": "none",
            "key": YOUTUBE_API_KEY
        }

        data = requests.get(url, params=params, timeout=10).json()

        items = data.get("items", [])
        if not items:
            return {
                "ok": False,
                "error": "No embeddable video found",
                "video_id": "",
                "title": "",
                "channel": "",
                "embed_url": "",
                "watch_url": youtube_search_url(query=query)
            }

        item = items[0]
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        channel = item["snippet"]["channelTitle"]

        return {
            "ok": True,
            "error": "",
            "video_id": video_id,
            "title": title,
            "channel": channel,
            "embed_url": f"https://www.youtube.com/embed/{video_id}?autoplay=1&rel=0&enablejsapi=1&controls=0&modestbranding=1",
            "watch_url": f"https://www.youtube.com/watch?v={video_id}"
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "video_id": "",
            "title": "",
            "channel": "",
            "embed_url": "",
            "watch_url": youtube_search_url(query=query)
        }


def youtube_cards_for_query(query="trending", max_results=12):
    """
    Converts YouTube API playlist results into ASHPLEX song cards with real thumbnails.
    This makes fallback look real instead of generated covers.
    """
    try:
        videos = get_youtube_playlist(query, max_results)
        songs = []
        for i, v in enumerate(videos):
            title = v.get("title", "Unknown Song")
            channel = v.get("channel", "YouTube")
            thumb = v.get("thumbnail", "")
            songs.append({
                "id": f"youtube-{i}",
                "title": title,
                "artist": channel,
                "cover": thumb,
                "preview": "",
                "youtube_url": "/youtube?q=" + quote_plus(title),
                "source": "YouTube API"
            })
        return songs
    except Exception:
        return []


def fallback_songs_for_query(query="trending"):
    """
    Final backup only. Used when Deezer and YouTube API both fail.
    """
    q = (query or "").lower()

    latest = [
        ("Sajni", "Arijit Singh"),
        ("Husn", "Anuv Jain"),
        ("Heeriye", "Jasleen Royal, Arijit Singh"),
        ("Chaleya", "Arijit Singh, Shilpa Rao"),
        ("Pehle Bhi Main", "Vishal Mishra"),
        ("O Maahi", "Arijit Singh"),
        ("Tere Vaaste", "Sachin-Jigar"),
        ("Apna Bana Le", "Arijit Singh"),
    ]

    classics = [
        ("Pehla Nasha", "Udit Narayan"),
        ("Tujhe Dekha To", "Kumar Sanu"),
        ("Dheere Dheere Se", "Kumar Sanu"),
        ("Chura Ke Dil Mera", "Kumar Sanu, Alka Yagnik"),
        ("Tip Tip Barsa Pani", "Udit Narayan, Alka Yagnik"),
        ("Sandese Aate Hain", "Sonu Nigam"),
    ]

    if "90s" in q or "kumar" in q or "udit" in q or "classic" in q:
        data = classics
        label = "90s Classics"
    else:
        data = latest
        label = "Backup Playlist"

    songs = []
    for i, (title, artist) in enumerate(data):
        safe_title = title.replace("&", "and")
        safe_artist = artist.replace("&", "and")
        svg = f"""data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500'><defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'><stop offset='0%' stop-color='%2332323a'/><stop offset='45%' stop-color='%23181924'/><stop offset='100%' stop-color='%23060609'/></linearGradient><radialGradient id='r' cx='35%' cy='20%' r='80%'><stop offset='0%' stop-color='%23fa233b' stop-opacity='.55'/><stop offset='100%' stop-color='%23fa233b' stop-opacity='0'/></radialGradient></defs><rect width='500' height='500' rx='42' fill='url(%23g)'/><rect width='500' height='500' rx='42' fill='url(%23r)'/><circle cx='250' cy='210' r='92' fill='none' stroke='white' stroke-opacity='.18' stroke-width='16'/><circle cx='250' cy='210' r='22' fill='white' fill-opacity='.22'/><text x='38' y='360' fill='white' font-size='34' font-family='Arial' font-weight='800'>{safe_title[:20]}</text><text x='38' y='405' fill='%23cfcfd8' font-size='22' font-family='Arial'>{safe_artist[:27]}</text><text x='38' y='455' fill='%23ff9aaa' font-size='18' font-family='Arial'>{label}</text></svg>"""
        songs.append({
            "id": f"fallback-{i}",
            "title": title,
            "artist": artist,
            "cover": svg,
            "preview": "",
            "youtube_url": youtube_search_url(title, artist),
            "source": "Backup + YouTube"
        })
    return songs


def get_deezer_songs(query="arijit"):
    """
    Deezer works better with short artist/song queries.
    If query contains '|', ASHPLEX searches multiple short queries and combines real cover cards.
    """
    all_songs = []
    seen = set()

    parts = [p.strip() for p in str(query).split("|") if p.strip()]
    if not parts:
        parts = ["arijit singh"]

    for part in parts[:5]:
        try:
            url = f"https://api.deezer.com/search?q={quote_plus(part)}"
            data = requests.get(url, timeout=8).json()

            for s in data.get("data", [])[:8]:
                title = s.get("title", "Unknown")
                artist = s.get("artist", {}).get("name", "Unknown")
                key = (title.lower(), artist.lower())

                if key in seen:
                    continue

                cover = (
                    s.get("album", {}).get("cover_xl")
                    or s.get("album", {}).get("cover_big")
                    or s.get("album", {}).get("cover_medium", "")
                )

                if not cover:
                    continue

                seen.add(key)
                all_songs.append({
                    "id": s.get("id"),
                    "title": title,
                    "artist": artist,
                    "cover": cover,
                    "preview": s.get("preview", ""),
                    "youtube_url": youtube_search_url(title, artist),
                    "source": "Deezer Real Cover + YouTube"
                })

                if len(all_songs) >= 18:
                    break

            if len(all_songs) >= 18:
                break

        except Exception:
            continue

    if all_songs:
        return all_songs

    # Last backup only when Deezer/network fails completely
    youtube_songs = youtube_cards_for_query(query.replace("|", " "), 12)
    if youtube_songs:
        return youtube_songs

    return fallback_songs_for_query(query)

def update_user_activity(username):
    today = str(date.today())

    con = db()
    cur = con.cursor()
    cur.execute("SELECT * FROM user_stats WHERE username=?", (username,))
    stat = cur.fetchone()

    reward_added = 0

    if not stat:
        cur.execute("""
            INSERT INTO user_stats(username, total_plays, today_plays, total_rewards, last_reward_date, last_play_date)
            VALUES(?,?,?,?,?,?)
        """, (username, 1, 1, 0, "", today))
        today_plays = 1
        total_rewards = 0
    else:
        if stat["last_play_date"] == today:
            today_plays = stat["today_plays"] + 1
        else:
            today_plays = 1

        total_rewards = stat["total_rewards"]

        if today_plays >= 20 and stat["last_reward_date"] != today:
            reward_added = 10
            total_rewards += 10
            cur.execute("""
                UPDATE user_stats
                SET total_plays = total_plays + 1,
                    today_plays = ?,
                    total_rewards = ?,
                    last_reward_date = ?,
                    last_play_date = ?
                WHERE username=?
            """, (today_plays, total_rewards, today, today, username))
        else:
            cur.execute("""
                UPDATE user_stats
                SET total_plays = total_plays + 1,
                    today_plays = ?,
                    total_rewards = ?,
                    last_play_date = ?
                WHERE username=?
            """, (today_plays, total_rewards, today, username))

    con.commit()
    con.close()

    return {
        "today_plays": today_plays,
        "total_rewards": total_rewards,
        "reward_added": reward_added,
        "target": 20,
        "target_achieved": today_plays >= 20
    }

LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>ASHPLEX Login</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
*{box-sizing:border-box}
body{margin:0;min-height:100vh;background:radial-gradient(circle at top,#3a1d2f,#08080b 48%,#000);color:white;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;display:flex;align-items:center;justify-content:center}
.card{width:370px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.12);border-radius:28px;padding:34px;text-align:center;box-shadow:0 30px 90px rgba(0,0,0,.45)}
h1{font-size:36px;margin:0 0 4px}.tag{color:#b8b8c6;font-size:13px;margin-bottom:24px}
input{width:100%;padding:14px;margin:8px 0;border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.08);border-radius:16px;color:white}
button{width:100%;padding:14px;margin-top:12px;border:0;background:#fa233b;color:white;border-radius:18px;font-weight:800;cursor:pointer}
a{color:#ff8a98}.small{font-size:12px;color:#aaa;margin-top:14px;line-height:1.6}
.chip{background:rgba(255,255,255,.08);color:white;text-decoration:none;border:1px solid rgba(255,255,255,.12);padding:9px 13px;border-radius:999px;font-weight:800}.chip:hover{background:#fa233b}
</style>
</head>
<body>
<div class="card">
<h1>🎧 ASHPLEX</h1>
<div class="tag">Your Mood. Your Music. Your World.</div>
<form method="POST" action="/login">
<input name="user" placeholder="Username" required>
<input name="password" type="password" placeholder="Password" required>
<label style="display:flex;gap:8px;align-items:center;justify-content:center;color:#aaa;font-size:13px;margin-top:8px">
<input type="checkbox" name="remember" checked style="width:auto;margin:0"> Remember me
</label>
<button>Login</button>
</form>
<div class="small">
Developer: ashutosh / Ashplex@123<br>
New customer? <a href="/register">Create account</a>
</div>
</div>

<script>
function openMoodPlaylist(selectEl){
  const mood = selectEl.value;
  if(mood){
    window.location.href = "/mood?mood=" + encodeURIComponent(mood);
  }
}
</script>

</body>
</html>
"""

REGISTER_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>ASHPLEX Register</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
*{box-sizing:border-box}
body{margin:0;min-height:100vh;background:radial-gradient(circle at top,#3a1d2f,#08080b 48%,#000);color:white;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;display:flex;align-items:center;justify-content:center}
.card{width:370px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.12);border-radius:28px;padding:34px;text-align:center;box-shadow:0 30px 90px rgba(0,0,0,.45)}
h1{font-size:36px;margin:0 0 4px}.tag{color:#b8b8c6;font-size:13px;margin-bottom:24px}
input{width:100%;padding:14px;margin:8px 0;border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.08);border-radius:16px;color:white}
button{width:100%;padding:14px;margin-top:12px;border:0;background:#fa233b;color:white;border-radius:18px;font-weight:800;cursor:pointer}
a{color:#ff8a98}.small{font-size:12px;color:#aaa;margin-top:14px}
</style>
</head>
<body>
<div class="card">
<h1>🎧 ASHPLEX</h1>
<div class="tag">Customer Registration</div>
<form method="POST" action="/register">
<input name="user" placeholder="Create username" required>
<input name="password" type="password" placeholder="Create password" required>
<button>Create Account</button>
</form>
<div class="small">Already have account? <a href="/">Login</a></div>
</div>
</body>
</html>
"""

APP_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>ASHPLEX</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#08080b;--text:#f5f5f7;--muted:#9898a6;--red:#fa233b;--red2:#ff5a6d}
body{min-height:100vh;background:#08080b;color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;overflow:hidden}
.app{width:100vw;height:100vh;display:grid;grid-template-columns:250px 1fr;grid-template-rows:1fr 92px;background:#08080b}
.sidebar{grid-row:1/2;background:rgba(18,18,23,.96);border-right:1px solid rgba(255,255,255,.08);padding:24px 18px}
.brand{display:flex;align-items:center;gap:10px;margin-bottom:28px}.brand-icon{width:42px;height:42px;border-radius:14px;background:linear-gradient(135deg,var(--red),#ff7b91);display:flex;align-items:center;justify-content:center;font-size:21px}.brand h2{font-size:20px}.brand p{font-size:11px;color:var(--muted)}
.nav-title{color:#777785;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;margin:20px 10px 8px}
.nav a{display:flex;align-items:center;gap:12px;padding:11px 12px;color:#c9c9d3;text-decoration:none;border-radius:12px;font-size:15px;margin:3px 0}.nav a:hover,.nav a.active{background:rgba(255,255,255,.08);color:white}
.main{overflow-y:auto;padding:26px 34px 120px;background:radial-gradient(circle at 75% -10%, rgba(250,35,59,.20), transparent 32%),linear-gradient(180deg,#181820,#09090d 45%,#000)}
.topbar{display:flex;justify-content:space-between;align-items:center;gap:18px;margin-bottom:28px}.search{flex:1;max-width:520px;position:relative}.search input{width:100%;padding:14px 18px;border:0;outline:none;border-radius:18px;color:white;background:rgba(255,255,255,.10);border:1px solid rgba(255,255,255,.10)}.user-pill{padding:11px 16px;border-radius:18px;background:rgba(255,255,255,.08);color:#ddd;font-size:14px}
.hero{display:grid;grid-template-columns:250px 1fr;gap:30px;align-items:end;min-height:300px;padding:28px;border-radius:34px;background:linear-gradient(135deg,rgba(255,255,255,.14),rgba(255,255,255,.04)),radial-gradient(circle at top right,rgba(250,35,59,.42),transparent 40%);border:1px solid rgba(255,255,255,.12);box-shadow:0 28px 90px rgba(0,0,0,.35);margin-bottom:28px}.hero-cover{width:250px;height:250px;border-radius:30px;overflow:hidden;box-shadow:0 25px 70px rgba(0,0,0,.55);background:#222}.hero-cover img{width:100%;height:100%;object-fit:cover}.hero h1{font-size:64px;line-height:.95;letter-spacing:-2px;margin-bottom:12px}.hero p{color:#d5d5df;font-size:16px;margin-bottom:22px}.eyebrow{color:var(--red2);text-transform:uppercase;font-size:12px;font-weight:800;letter-spacing:1.6px;margin-bottom:10px}
.btn{display:inline-flex;align-items:center;justify-content:center;border:0;text-decoration:none;color:white;font-weight:750;padding:13px 22px;border-radius:999px;background:var(--red);cursor:pointer}.btn.secondary{background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.12)}
.mood-ai-box{margin:0 0 24px;padding:18px;border-radius:24px;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.10);backdrop-filter:blur(20px)}.mood-ai-head{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:14px}.mood-ai-head h3{font-size:18px}.ai-badge{font-size:12px;color:#ffb3bd;background:rgba(250,35,59,.16);padding:7px 11px;border-radius:999px}.mood-ai-form{display:grid;grid-template-columns:1fr 1fr auto;gap:12px;align-items:end}.mood-ai-form label{display:block;color:var(--muted);font-size:12px;margin-bottom:6px}.mood-ai-form select{width:100%;padding:13px 14px;border:0;outline:none;border-radius:16px;color:white;background:rgba(255,255,255,.10);border:1px solid rgba(255,255,255,.10)}
.hybrid-box{margin:0 0 24px;padding:18px;border-radius:24px;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.10)}.source-badge{display:inline-block;margin-top:8px;padding:6px 10px;border-radius:999px;background:rgba(250,35,59,.16);color:#ffb3bd;font-size:12px;text-decoration:none}
.section-row{display:flex;align-items:center;justify-content:space-between;margin:10px 0 16px}.section-row h2{font-size:26px}.section-row span{color:var(--muted)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(165px,1fr));gap:20px}.card{background:rgba(255,255,255,.065);border:1px solid rgba(255,255,255,.08);border-radius:22px;padding:14px;transition:.25s;cursor:pointer}.card:hover{transform:translateY(-7px);background:rgba(255,255,255,.10);box-shadow:0 22px 55px rgba(0,0,0,.35)}.card-cover{width:100%;aspect-ratio:1/1;border-radius:18px;overflow:hidden;background:#222;margin-bottom:12px;position:relative}.card-cover img{width:100%;height:100%;object-fit:cover}.play-badge{position:absolute;right:10px;bottom:10px;width:42px;height:42px;border-radius:50%;background:var(--red);display:flex;align-items:center;justify-content:center;opacity:0;transition:.2s}.card:hover .play-badge{opacity:1}.card h3{font-size:15px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-bottom:5px}.card p{color:var(--muted);font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.yt-btn{display:inline-flex;margin-top:10px;padding:8px 11px;border-radius:999px;background:#ff0033;color:white;text-decoration:none;font-size:12px;font-weight:800}
.player{grid-column:1/3;background:rgba(12,12,16,.92);backdrop-filter:blur(28px);border-top:1px solid rgba(255,255,255,.10);display:grid;grid-template-columns:320px 1fr 260px;align-items:center;padding:14px 28px;z-index:20}.now{display:flex;align-items:center;gap:14px;min-width:0}.now-cover{width:60px;height:60px;border-radius:14px;overflow:hidden;background:#222}.now-cover img{width:100%;height:100%;object-fit:cover}.now h3{font-size:15px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.now p{color:var(--muted);font-size:12px}.controls{display:flex;align-items:center;justify-content:center;gap:18px}.control{border:0;color:white;background:transparent;font-size:22px;cursor:pointer}.play{width:46px;height:46px;border-radius:50%;background:white;color:#000}.hidden-audio{display:none}.volume{justify-self:end;color:#aaa}
@media(max-width:850px){body{overflow:auto}.app{display:block;min-height:100vh;height:auto;padding-bottom:92px}.sidebar{display:none}.main{padding:18px 16px 120px;min-height:100vh}.topbar{display:block}.search{max-width:none;margin-bottom:14px}.user-pill{display:inline-block}.hero{display:block;padding:20px;border-radius:28px;min-height:auto}.hero-cover{width:100%;height:auto;aspect-ratio:1/1;max-width:330px;margin:0 auto 22px}.hero div:last-child{text-align:center}.hero h1{font-size:46px}.mood-ai-form{grid-template-columns:1fr}.grid{grid-template-columns:1fr}.card{display:grid;grid-template-columns:86px 1fr;gap:14px;align-items:center}.card-cover{margin:0}.player{position:fixed;left:0;right:0;bottom:0;grid-template-columns:1fr auto;padding:12px 16px}.controls .control:not(.play),.volume{display:none}}
</style>
</head>
<body>
<div class="app">
<aside class="sidebar">
<div class="brand"><div class="brand-icon">🎧</div><div><h2>ASHPLEX</h2><p>Your Mood. Your Music. Your World.</p></div></div>
<nav class="nav">
<div class="nav-title">Library</div>
<a class="active" href="/home"><span>⌂</span> Listen Now</a>
{% if role == 'developer' %}<a href="/developer"><span>⚙</span> Developer Panel</a>{% endif %}
<a href="/wallet"><span>🎁</span> Rewards</a>
<a href="/account"><span>⚙</span> Account</a>
<a href="/youtube?q={{query}}" ><span>▶</span> YouTube Full Mode</a>
{% if user %}<a href="/logout"><span>⇥</span> Logout</a>{% else %}<a href="/login"><span>🔐</span> Login / Save Account</a>{% endif %}
</nav>
</aside>

<main class="main">
<div class="topbar">
<form class="search" action="/home"><input name="q" value="{{query}}" placeholder="Search Deezer preview songs..."></form>
<div class="user-pill">{% if user %}Hi, {{user}} · {{role}}{% else %}<a href="/login" style="color:white;text-decoration:none">Login to save your music</a>{% endif %}</div>
</div>

{% if not user %}
<div style="margin:-8px 0 22px;padding:15px 18px;border-radius:20px;background:rgba(250,35,59,.14);border:1px solid rgba(250,35,59,.22);display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap">
  <div>
    <b>Save your ASHPLEX experience</b>
    <p style="color:#ddd;margin-top:4px;font-size:14px">Login later with mobile OTP or Gmail to save rewards, likes and listening activity.</p>
  </div>
  <a class="btn" href="/login">Login Now</a>
</div>
{% endif %}

<section class="hero">
<div class="hero-cover">{% if songs and songs[0].cover %}<img src="{{songs[0].cover}}">{% else %}<div style="height:100%;display:flex;align-items:center;justify-content:center;font-size:52px">🎧</div>{% endif %}</div>
<div>
<div class="eyebrow">ASHPLEX Hybrid Music</div>
<h1>Your Mood.<br>Your Music.</h1>
<p>Trending Now shows latest songs; 90s Classics shows old evergreen songs. Deezer API gives preview and YouTube gives full-song discovery.</p>
<a class="btn" href="/home">Play Mix</a>
<a class="btn secondary" href="/youtube?q={{query}}">YouTube Full Mode</a>
</div>
</section>

<div class="mood-ai-box">
<div class="mood-ai-head"><h3>🤖 AI Mood Level Recommendation
<div class="teacher-demo" style="margin-top:16px;display:flex;gap:10px;flex-wrap:wrap">
  <a class="chip" href="/mood?mood=trending">🔥 Trending Now</a>
  <a class="chip" href="/mood?mood=viral">📈 Viral Reels</a>
  <a class="chip" href="/mood?mood=new">🆕 New Hindi</a>
  <a class="chip" href="/mood?mood=classic90s">🎧 90s Classics</a>
  <a class="chip" href="/mood?mood=happy">😊 Happy</a>
  <a class="chip" href="/mood?mood=sad">💔 Sad</a>
  <a class="chip" href="/mood?mood=romantic">❤️ Romantic</a>
  <a class="chip" href="/mood?mood=focus">🎯 Focus</a>
  <a class="chip" href="/mood?mood=relax">🌙 Relax</a>
  <a class="chip" href="/mood?mood=workout">💪 Workout</a>
  <a class="chip" href="/mood?mood=angry">⚡ Angry</a>
</div>
<!-- Teacher Demo Mood Buttons -->
</h3><div class="ai-badge">Mood + Level → Deezer search</div></div>
<form class="mood-ai-form" action="/home">
<div>
<label>Select Mood</label>
<select name="mood" onchange="openMoodPlaylist(this)">
<option value="trending">Trending Now - Latest Songs</option><option value="viral">Viral Reels Songs</option><option value="new">New Hindi Songs</option><option value="classic90s">90s Classics</option><option value="happy">Happy</option><option value="sad">Sad</option><option value="romantic">Romantic</option><option value="focus">Focus</option><option value="relax">Relax</option><option value="workout">Workout</option><option value="angry">Angry</option>
</select>
</div>
<div>
<label>Mood Level</label>
<select name="level">
<option value="low">Low / Soft</option><option value="medium" selected>Medium</option><option value="high">High / Intense</option>
</select>
</div>
<button class="btn" type="submit">Generate Mix</button>
</form>
</div>

<div class="hybrid-box">
<h3>🌐 Hybrid Full Song Source</h3>
<p style="color:#aaa;margin:8px 0 12px">Preview on ASHPLEX via Deezer. Full song option opens YouTube search/player.</p>
<a class="source-badge" href="/youtube?q={{query}}">Open YouTube Full Song Mode</a>
</div>


<div class="hybrid-box">
<h3>🔥 Teacher Demo Sections</h3>
<p style="color:#aaa;margin:8px 0 12px">Trending uses short Deezer-friendly searches first, so real album covers load before backup mode.</p>
<div style="display:flex;gap:10px;flex-wrap:wrap">
  <a class="source-badge" href="/mood?mood=trending">🔥 Trending Now</a>
  <a class="source-badge" href="/mood?mood=viral">📈 Viral Reels</a>
  <a class="source-badge" href="/mood?mood=new">🆕 New Hindi</a>
  <a class="source-badge" href="/mood?mood=classic90s">🎧 90s Classics</a>
</div>
</div>

<div class="hybrid-box"><h3>✅ Real cover mode</h3><p style="color:#aaa;margin-top:8px">ASHPLEX now searches short artist/song keywords on Deezer first, so real album covers appear. Backup mode runs only if API/network fails.</p></div>
<div class="section-row"><h2>Made For You</h2><span>{{songs|length}} real cover tracks · {{query}}</span></div>

<div class="grid">
{% for s in songs %}
<div class="card" onclick="playSong('{{s.preview}}','{{s.title|e}}','{{s.artist|e}}','{{s.cover}}')">
<div class="card-cover">{% if s.cover %}<img src="{{s.cover}}">{% else %}<div style="height:100%;display:flex;align-items:center;justify-content:center;font-size:35px">🎵</div>{% endif %}<div class="play-badge">▶</div></div>
<div><h3>{{s.title}}</h3><p>{{s.artist}}</p><p style="font-size:11px;color:#ff9aaa;margin-top:4px">{{s.source}}</p><a class="yt-btn" href="/playlist?q={{s.title}} {{s.artist}}" onclick="event.stopPropagation()">▶ Open Player</a></div>
</div>
{% else %}
<p style="color:#aaa">No songs found from API, but ASHPLEX fallback playlist should load automatically.</p>
{% endfor %}
</div>
</main>

<footer class="player">
<div class="now">
<div class="now-cover" id="nowCover">{% if songs and songs[0].cover %}<img src="{{songs[0].cover}}">{% else %}🎧{% endif %}</div>
<div style="min-width:0"><h3 id="nowTitle">{% if songs %}{{songs[0].title}}{% else %}No Song{% endif %}</h3><p id="nowArtist">{% if songs %}{{songs[0].artist}}{% else %}Search music{% endif %}</p></div>
</div>
<div class="controls"><button class="control">⏮</button><button class="control play" id="playBtn">▶</button><button class="control">⏭</button></div>
<div class="volume">🔊 ━━━━━</div>
</footer>
</div>

<audio id="audio" class="hidden-audio" {% if songs %}src="{{songs[0].preview}}"{% endif %}></audio>
<script>
const audio=document.getElementById("audio");const playBtn=document.getElementById("playBtn");
function playSong(src,title,artist,cover){
  if(!src){alert("Preview not available. Use YouTube Full Song button.");return;}
  audio.src=src;
  document.getElementById("nowTitle").innerText=title;
  document.getElementById("nowArtist").innerText=artist;
  document.getElementById("nowCover").innerHTML=cover?'<img src="'+cover+'">':'🎵';
  audio.play();
  playBtn.innerText="⏸";
  fetch("/api/play").then(r=>r.json()).then(d=>{
    if(d.reward_added && d.reward_added > 0){
      alert("🎉 Congratulations! You earned ₹" + d.reward_added + " reward for completing daily target.");
    }
  });
}
playBtn.addEventListener("click",()=>{if(audio.paused){audio.play();playBtn.innerText="⏸";fetch("/api/play");}else{audio.pause();playBtn.innerText="▶"}});
audio.addEventListener("ended",()=>{playBtn.innerText="▶"});
</script>
</body>
</html>
"""

YOUTUBE_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>ASHPLEX Player</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{
  min-height:100vh;
  background:
    radial-gradient(circle at 20% 0%,rgba(250,35,59,.30),transparent 30%),
    radial-gradient(circle at 75% 0%,rgba(83,60,255,.22),transparent 32%),
    linear-gradient(180deg,#171820,#07070b 58%,#000);
  color:white;
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;
}
.page{min-height:100vh;padding:24px}
.header{
  max-width:1180px;
  margin:0 auto 22px;
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:18px;
}
.logo h1{font-size:30px;letter-spacing:-.6px}
.logo p{color:#aaa;margin-top:6px}
.search{display:flex;gap:10px;width:min(560px,100%)}
.search input{
  flex:1;padding:14px 18px;border-radius:999px;border:1px solid rgba(255,255,255,.12);
  background:rgba(255,255,255,.09);color:white;outline:none;
}
.btn{border:0;border-radius:999px;background:#fa233b;color:white;padding:13px 20px;font-weight:800;text-decoration:none;cursor:pointer;white-space:nowrap}
.player-card{
  max-width:1180px;margin:0 auto;border-radius:38px;overflow:hidden;
  background:linear-gradient(135deg,rgba(255,255,255,.14),rgba(255,255,255,.045));
  border:1px solid rgba(255,255,255,.12);box-shadow:0 35px 120px rgba(0,0,0,.58);position:relative;
}
.player-layout{display:grid;grid-template-columns:260px 1fr;gap:32px;align-items:center;padding:32px}
.cover-shell{
  width:260px;height:260px;border-radius:34px;overflow:hidden;background:#000;
  box-shadow:0 30px 90px rgba(0,0,0,.65);position:relative;
}
.cover-shell iframe{
  width:100%;height:100%;border:0;transform:scale(1.62);pointer-events:none;opacity:.98;
}
.cover-shell:after{
  content:"";position:absolute;left:28px;right:28px;bottom:-30px;height:65px;
  background:#fa233b;filter:blur(40px);opacity:.35;
}
.badge{
  display:inline-flex;align-items:center;gap:8px;padding:9px 14px;border-radius:999px;
  background:rgba(250,35,59,.16);border:1px solid rgba(250,35,59,.25);
  color:#ff9aaa;font-size:13px;font-weight:800;margin-bottom:18px;
}
.title{font-size:38px;line-height:1.12;letter-spacing:-1px;margin-bottom:10px}
.channel{color:#c5c5d0;font-size:16px;margin-bottom:22px}
.progress{display:grid;grid-template-columns:42px 1fr 48px;align-items:center;gap:12px;color:#cfcfd8;font-size:13px;margin:18px 0}
.bar{height:7px;border-radius:999px;background:rgba(255,255,255,.16);position:relative;cursor:pointer;--p:0%}
.bar:before{content:"";position:absolute;inset:0 auto 0 0;width:var(--p);border-radius:999px;background:#fff}
.bar:after{content:"";position:absolute;left:var(--p);top:50%;transform:translate(-50%,-50%);width:15px;height:15px;border-radius:50%;background:#fff}
.controls{display:flex;align-items:center;justify-content:center;gap:20px;margin:22px 0}
.ctrl{border:0;background:rgba(255,255,255,.08);color:white;width:48px;height:48px;border-radius:50%;font-size:18px;cursor:pointer}
.mainplay{border:0;background:#fff;color:#111;width:74px;height:74px;border-radius:50%;font-size:34px;font-weight:900;cursor:pointer}
.actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px}
.action{border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.08);color:white;padding:10px 14px;border-radius:999px;cursor:pointer;font-weight:700}
.action.active{background:#fa233b;border-color:#fa233b}
.note{margin-top:18px;color:#aaa;line-height:1.55}
.warning{max-width:900px;margin:40px auto;padding:26px;border-radius:28px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.12)}
@media(max-width:850px){
  .page{padding:14px 14px 100px}.header{display:block}.search{width:100%;margin-top:14px}
  .player-card{border-radius:34px;max-width:430px}
  .player-layout{display:block;padding:18px}
  .cover-shell{width:100%;height:auto;aspect-ratio:1/1;margin-bottom:20px}
  .title{font-size:24px}.mainplay{width:66px;height:66px;font-size:30px}.ctrl{width:44px;height:44px}
}
</style>
</head>
<body>
<div class="page">
  <div class="header">
    <div class="logo">
      <h1>🎧 ASHPLEX Audio Mode</h1>
      <p>Video is converted into compact music-player style inside ASHPLEX.</p>
    </div>
    <form class="search" action="/playlist">
      <input name="q" value="{{q}}" placeholder="Search artist or song...">
      <button class="btn">Search Playlist</button>
    </form>
    <a class="btn" href="/home">Back</a>
  </div>

  {% if video.ok %}
  <div class="player-card">
    <div class="player-layout">
      <div class="cover-shell">
        <iframe id="ytPlayer" src="{{video.embed_url}}" allow="autoplay; encrypted-media" allowfullscreen></iframe>
      </div>
      <div>
        <div class="badge">🎵 Now Playing inside ASHPLEX</div>
        <h2 class="title">{{video.title}}</h2>
        <p class="channel">{{video.channel}}</p>

        <div class="progress">
          <span id="currentTime">0:00</span>
          <div class="bar" id="progressBar"></div>
          <span id="durationTime">0:00</span>
        </div>

        <div class="controls">
          <button class="ctrl" id="backBtn">⏪</button>
          <button class="mainplay" id="playPauseBtn">Ⅱ</button>
          <button class="ctrl" id="forwardBtn">⏩</button>
          <button class="ctrl" id="loopBtn">🔁</button>
        </div>

        <div class="actions">
          <button class="action" id="likeBtn">♡ Like</button>
          <button class="action" onclick="shareSong()">📤 Share</button>
          <button class="action" id="muteBtn">🔊 Sound</button>
        </div>

        <p class="note">YouTube policy does not allow pure audio extraction, so ASHPLEX keeps video compact like album art and gives music-player controls.</p>
      </div>
    </div>
  </div>
  {% else %}
  <div class="warning">
    <h2>⚠️ YouTube API setup needed</h2>
    <p style="color:#aaa;margin:12px 0">{{video.error}}</p>
    <p style="color:#aaa">Add YOUTUBE_API_KEY in Render Environment Variables, then redeploy.</p>
  </div>
  {% endif %}
</div>

<script>
document.querySelectorAll(".title").forEach(el=>{
  const t=document.createElement("textarea");
  t.innerHTML=el.innerHTML;
  el.innerText=t.value;
});

let ytPlayer;
let loopMode=false;

function fmt(sec){
  sec=Math.max(0,Math.floor(sec||0));
  return Math.floor(sec/60)+":"+String(sec%60).padStart(2,"0");
}
function updateProgress(){
  if(!ytPlayer || !ytPlayer.getDuration) return;
  const d=ytPlayer.getDuration();
  const c=ytPlayer.getCurrentTime();
  if(d>0){
    document.getElementById("progressBar").style.setProperty("--p", ((c/d)*100)+"%");
    document.getElementById("currentTime").innerText=fmt(c);
    document.getElementById("durationTime").innerText=fmt(d);
  }
}
function onYouTubeIframeAPIReady(){
  ytPlayer=new YT.Player("ytPlayer",{
    events:{
      onReady:function(){bindControls(); setInterval(updateProgress,700);},
      onStateChange:function(e){
        if(e.data===YT.PlayerState.ENDED && loopMode){ytPlayer.seekTo(0,true);ytPlayer.playVideo();}
        document.getElementById("playPauseBtn").innerText=(e.data===YT.PlayerState.PLAYING)?"Ⅱ":"▶";
      }
    }
  });
}
function bindControls(){
  document.getElementById("playPauseBtn").onclick=()=>{
    const s=ytPlayer.getPlayerState();
    if(s===YT.PlayerState.PLAYING) ytPlayer.pauseVideo(); else ytPlayer.playVideo();
  };
  document.getElementById("backBtn").onclick=()=>ytPlayer.seekTo(Math.max(0,ytPlayer.getCurrentTime()-10),true);
  document.getElementById("forwardBtn").onclick=()=>ytPlayer.seekTo(Math.min(ytPlayer.getDuration(),ytPlayer.getCurrentTime()+10),true);
  document.getElementById("loopBtn").onclick=(e)=>{loopMode=!loopMode;e.target.classList.toggle("active",loopMode);};
  document.getElementById("muteBtn").onclick=(e)=>{ if(ytPlayer.isMuted()){ytPlayer.unMute();e.target.innerText="🔊 Sound"}else{ytPlayer.mute();e.target.innerText="🔇 Muted"} };
  document.getElementById("likeBtn").onclick=(e)=>{e.target.classList.toggle("active");e.target.innerText=e.target.classList.contains("active")?"❤️ Liked":"♡ Like"};
  document.getElementById("progressBar").onclick=(e)=>{
    const r=e.target.getBoundingClientRect();
    ytPlayer.seekTo(((e.clientX-r.left)/r.width)*ytPlayer.getDuration(),true);
  };
}
function shareSong(){
  if(navigator.share){navigator.share({title:document.querySelector(".title").innerText,text:"Listen on ASHPLEX",url:location.href});}
  else alert("Share this link: "+location.href);
}
</script>
<script src="https://www.youtube.com/iframe_api"></script>
</body>
</html>
"""



PLAYLIST_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>ASHPLEX Playlist</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{min-height:100vh;background:radial-gradient(circle at top,#22162a,#07070b 58%,#000);color:white;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}
.page{padding:24px;max-width:1180px;margin:auto}
.header{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-bottom:26px}
h1{font-size:36px}.muted{color:#aaa;margin-top:6px}
.search{display:flex;gap:10px;width:min(560px,100%)}
.search input{flex:1;padding:14px 18px;border-radius:999px;border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.09);color:white;outline:none}
.btn{border:0;border-radius:999px;background:#fa233b;color:white;padding:13px 20px;font-weight:800;text-decoration:none;cursor:pointer;white-space:nowrap}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:18px}
.card{background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.10);border-radius:24px;padding:14px;text-decoration:none;color:white;transition:.25s}
.card:hover{transform:translateY(-6px);background:rgba(255,255,255,.11)}
.card img{width:100%;aspect-ratio:16/10;object-fit:cover;border-radius:18px;margin-bottom:12px;background:#111}
.card h3{font-size:16px;line-height:1.25;margin-bottom:6px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.card p{color:#aaa;font-size:13px}
@media(max-width:850px){.page{padding:16px}.header{display:block}.search{width:100%;margin-top:16px}.grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="page">
  <div class="header">
    <div>
      <h1>🎵 ASHPLEX Playlist</h1>
      <p class="muted">Search result playlist for: <b>{{q}}</b></p><p class="muted">Teacher demo: Trending Now = latest songs, 90s Classics = old songs, Mood AI = mood-based playlist.</p>
    </div>
    <form class="search" action="/playlist">
      <input name="q" value="{{q}}" placeholder="Search artist or song...">
      <button class="btn">Search</button>
    </form>
    <a class="btn" href="/home">Home</a>
  </div>

  <div class="grid">
    {% for v in videos %}
    <a class="card" href="/youtube?q={{v.title}}">
      <img src="{{v.thumbnail}}">
      <h3>{{v.title}}</h3>
      <p>{{v.channel}}</p>
    </a>
    {% else %}
    <p class="muted">No playlist found. Check YouTube API key.</p>
    {% endfor %}
  </div>
</div>
<script>
document.querySelectorAll("h3").forEach(el=>{
  const t=document.createElement("textarea");t.innerHTML=el.innerHTML;el.innerText=t.value;
});
</script>
</body>
</html>
"""

DEVELOPER_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>ASHPLEX Developer</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
*{box-sizing:border-box}
body{margin:0;background:radial-gradient(circle at top right,rgba(250,35,59,.22),transparent 35%),#08080b;color:white;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}
.page{min-height:100vh;padding:28px}.header{display:flex;justify-content:space-between;align-items:center;margin-bottom:24px}.btn{background:#fa233b;color:white;text-decoration:none;padding:12px 18px;border-radius:999px;font-weight:700;border:0;cursor:pointer}.btn.secondary{background:rgba(255,255,255,.12)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:22px;margin-bottom:22px}.panel{background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.10);border-radius:24px;padding:22px}.panel h2{margin-top:0}.big{font-size:42px;color:#ff8a98;font-weight:800}table{width:100%;border-collapse:collapse;margin-top:12px}td,th{padding:12px;border-bottom:1px solid rgba(255,255,255,.08);text-align:left}th{color:#aaa}
@media(max-width:850px){.header{display:block}}
</style>
</head>
<body>
<div class="page">
<div class="header">
<div><h1>🎧 ASHPLEX Developer Panel</h1><p style="color:#aaa">Deezer + YouTube hybrid platform with customer analytics.</p></div>
<div><a class="btn secondary" href="/home">Open App</a> <a class="btn secondary" href="/logout">Logout</a></div>
</div>

<div class="grid">
<div class="panel"><h2>Total Customers</h2><div class="big">{{customer_count}}</div><p style="color:#aaa">Registered customer accounts</p></div>
<div class="panel"><h2>Total Plays</h2><div class="big">{{total_plays}}</div><p style="color:#aaa">Customer preview play activity</p></div>
<div class="panel"><h2>Music Sources</h2><div class="big">2</div><p style="color:#aaa">Deezer preview + YouTube full song</p></div>
</div>

<div class="panel">
<h2>Customer Listening Activity & Reward Status</h2>
<p style="color:#aaa">Rule: If customer listens 20 songs in one day, reward target is achieved.</p>
<table>
<tr><th>Customer</th><th>Total Plays</th><th>Today Plays</th><th>Reward Earned</th><th>Status</th></tr>
{% for u in stats %}
<tr>
<td>{{u.username}}</td>
<td>{{u.total_plays}}</td>
<td>{{u.today_plays}}</td>
<td>₹{{u.total_rewards}}</td>
<td>{% if u.today_plays >= 20 %}🔥 Target Achieved{% else %}⏳ In Progress{% endif %}</td>
</tr>
{% else %}
<tr><td colspan="5" style="color:#aaa">No listening activity yet.</td></tr>
{% endfor %}
</table>
</div>
</div>
</body>
</html>
"""

ACCOUNT_HTML = """
<!DOCTYPE html>
<html>
<head><title>ASHPLEX Account</title><meta name="viewport" content="width=device-width, initial-scale=1.0"><style>
body{margin:0;min-height:100vh;background:#08080b;color:white;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;display:flex;align-items:center;justify-content:center}.card{width:440px;background:rgba(255,255,255,.08);border-radius:24px;padding:28px}.btn{display:inline-block;margin-top:18px;padding:12px 18px;border-radius:999px;background:#fa233b;color:white;text-decoration:none;border:0;font-weight:700;cursor:pointer}.secondary{background:rgba(255,255,255,.12)}.danger{background:#b00020}.row{padding:12px 0;border-bottom:1px solid rgba(255,255,255,.08);display:flex;justify-content:space-between}</style></head>
<body><div class="card"><h1>🎧 ASHPLEX Account</h1><p style="color:#aaa">Your account is saved in database for future login.</p><div class="row"><span>Username</span><b>{{user}}</b></div><div class="row"><span>Role</span><b>{{role}}</b></div><a class="btn secondary" href="/home">Back</a> <a class="btn secondary" href="/logout">Logout</a>{% if role != 'developer' %}<form method="POST" action="/forget-account" onsubmit="return confirm('Delete account permanently?')"><button class="btn danger">Forget / Delete My Account</button></form>{% endif %}</div></body></html>
"""

WALLET_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>ASHPLEX Rewards</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body{margin:0;min-height:100vh;background:radial-gradient(circle at top right,rgba(250,35,59,.22),transparent 35%),#08080b;color:white;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;display:flex;align-items:center;justify-content:center;padding:20px}
.card{width:460px;background:rgba(255,255,255,.08);border-radius:24px;padding:28px;border:1px solid rgba(255,255,255,.12)}
h1{margin:0 0 10px}.big{font-size:48px;color:#ff8a98;font-weight:800}.muted{color:#aaa}.bar{height:12px;background:rgba(255,255,255,.1);border-radius:20px;overflow:hidden;margin:16px 0}.fill{height:100%;background:#fa233b;width:{{progress}}%}.btn{display:inline-block;margin-top:18px;padding:12px 18px;border-radius:999px;background:#fa233b;color:white;text-decoration:none;font-weight:700}
</style>
</head>
<body>
<div class="card">
<h1>🎁 ASHPLEX Reward Wallet</h1>
<p class="muted">Daily target: Listen 20 preview songs to unlock ₹10 reward.</p>
<div class="big">₹{{total_rewards}}</div>
<p>Total reward earned</p>
<div class="bar"><div class="fill"></div></div>
<p>{{today_plays}} / 20 songs listened today</p>
<a class="btn" href="/home">Back to Music</a>
</div>
</body>
</html>
"""


MOOD_PLAYLIST_QUERIES = {
    "trending": "latest hindi songs Arijit Singh Vishal Mishra Bollywood hits",
    "viral": "viral hindi reels songs Arijit Singh Anuv Jain",
    "new": "new hindi songs Arijit Singh Vishal Mishra Shreya Ghoshal",
    "classic90s": "90s hindi songs Kumar Sanu Udit Narayan Alka Yagnik Sonu Nigam",
    "happy": "happy bollywood songs Udit Narayan Abhijeet",
    "sad": "sad hindi songs Arijit Singh Sonu Nigam",
    "romantic": "romantic hindi songs Arijit Singh Kumar Sanu Alka Yagnik",
    "focus": "lofi hindi focus songs",
    "relax": "relaxing hindi songs Anuv Jain Arijit Singh",
    "workout": "bollywood dance workout songs Badshah Neha Kakkar",
    "angry": "bollywood attitude songs Badshah Honey Singh"
}

def mood_to_query(mood):
    return MOOD_PLAYLIST_QUERIES.get((mood or "trending").lower(), MOOD_PLAYLIST_QUERIES["trending"])

def get_youtube_playlist(query="arijit songs", max_results=12):
    """
    Uses YouTube Data API v3 to show playlist/list results for artist search.
    It returns multiple embeddable videos instead of directly auto-opening one song.
    """
    if not YOUTUBE_API_KEY:
        return []

    try:
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": query + " songs",
            "type": "video",
            "maxResults": max_results,
            "videoEmbeddable": "true",
            "safeSearch": "none",
            "key": YOUTUBE_API_KEY
        }
        data = requests.get(url, params=params, timeout=10).json()
        items = data.get("items", [])

        results = []
        for item in items:
            vid = item.get("id", {}).get("videoId", "")
            snip = item.get("snippet", {})
            if not vid:
                continue
            thumb = (
                snip.get("thumbnails", {}).get("high", {}).get("url")
                or snip.get("thumbnails", {}).get("medium", {}).get("url")
                or snip.get("thumbnails", {}).get("default", {}).get("url")
                or ""
            )
            results.append({
                "video_id": vid,
                "title": snip.get("title", "Unknown Song"),
                "channel": snip.get("channelTitle", "YouTube"),
                "thumbnail": thumb,
                "embed_url": f"https://www.youtube.com/embed/{vid}?autoplay=1&rel=0&enablejsapi=1&controls=0&modestbranding=1"
            })
        return results
    except Exception:
        return []


@app.route("/health")
def health():
    return "OK", 200

@app.route("/")
def landing():
    if "user" in session:
        return redirect("/home")
    return render_template_string(LANDING_HTML)

@app.route("/login", methods=["GET"])
def mobile_login():
    return render_template_string(LOGIN_HTML, error=None, step="phone")

@app.route("/send-otp", methods=["POST"])
def send_otp():
    phone = request.form.get("phone", "").strip()

    if not phone.isdigit() or len(phone) != 10:
        return render_template_string(LOGIN_HTML, error="Please enter a valid 10 digit mobile number.", step="phone")

    otp = str(random.randint(100000, 999999))
    session["pending_phone"] = phone
    session["pending_otp"] = otp

    # Demo: OTP screen par dikhega.
    # Real SMS ke liye Firebase/Twilio API yaha integrate hoga.
    return render_template_string(LOGIN_HTML, error=None, step="otp", phone=phone, demo_otp=otp)

@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    otp = request.form.get("otp", "").strip()
    phone = session.get("pending_phone")
    real_otp = session.get("pending_otp")

    if not phone or not real_otp:
        return redirect("/login")

    if otp != real_otp:
        return render_template_string(LOGIN_HTML, error="Wrong OTP. Please try again.", step="otp", phone=phone, demo_otp=real_otp)

    con = db()
    cur = con.cursor()

    cur.execute("SELECT * FROM users WHERE username=?", (phone,))
    user = cur.fetchone()

    if not user:
        cur.execute(
            "INSERT INTO users(username,password,role) VALUES(?,?,?)",
            (phone, "otp_login", "customer")
        )

    cur.execute(
        "INSERT OR IGNORE INTO user_stats(username,total_plays,today_plays,total_rewards,last_reward_date,last_play_date) VALUES(?,?,?,?,?,?)",
        (phone, 0, 0, 0, "", "")
    )

    con.commit()
    con.close()

    session["user"] = phone
    session["role"] = "customer"
    session.pop("pending_phone", None)
    session.pop("pending_otp", None)
    session.permanent = True

    return redirect("/home")

@app.route("/gmail-login")
def gmail_login():
    # Demo Gmail login flow.
    # Real Gmail OAuth ke liye Google Cloud OAuth Client ID/Secret add karna hoga.
    gmail_user = "demo.gmail.user@gmail.com"

    con = db()
    cur = con.cursor()

    cur.execute("SELECT * FROM users WHERE username=?", (gmail_user,))
    user = cur.fetchone()

    if not user:
        cur.execute(
            "INSERT INTO users(username,password,role) VALUES(?,?,?)",
            (gmail_user, "gmail_login", "customer")
        )

    cur.execute(
        "INSERT OR IGNORE INTO user_stats(username,total_plays,today_plays,total_rewards,last_reward_date,last_play_date) VALUES(?,?,?,?,?,?)",
        (gmail_user, 0, 0, 0, "", "")
    )

    con.commit()
    con.close()

    session["user"] = gmail_user
    session["role"] = "customer"
    session.permanent = True

    return redirect("/home")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return REGISTER_HTML

    username = request.form.get("user", "").strip()
    password = request.form.get("password", "").strip()

    try:
        con = db()
        cur = con.cursor()
        cur.execute("INSERT INTO users(username,password,role) VALUES(?,?,?)", (username, password, "customer"))
        con.commit()
        con.close()
        return redirect("/")
    except sqlite3.IntegrityError:
        return REGISTER_HTML.replace("Customer Registration", "Username already exists")

@app.route("/home")
def home():
    mood = request.args.get("mood", "trending")
    level = request.args.get("level", "medium")
    query = request.args.get("q")

    if not query:
        query = ai_mood_query(mood, level)

    songs = get_deezer_songs(query)

    return render_template_string(
        APP_HTML,
        songs=songs,
        query=query,
        user=session.get("user"),
        role=session.get("role", "guest")
    )

@app.route("/youtube")
def youtube_mode():
    q = request.args.get("q", "arijit song")
    video = get_youtube_video(q)
    return render_template_string(
        YOUTUBE_HTML,
        q=q,
        video=video
    )


@app.route("/mood")
def mood_mode():
    mood = request.args.get("mood", "trending")
    q = mood_to_query(mood)
    videos = get_youtube_playlist(q, 12)
    return render_template_string(
        PLAYLIST_HTML,
        q=f"{mood.title()} Mood - {q}",
        videos=videos
    )

@app.route("/playlist")
def playlist_mode():
    q = request.args.get("q", "arijit songs")
    videos = get_youtube_playlist(q, 12)
    return render_template_string(
        PLAYLIST_HTML,
        q=q,
        videos=videos
    )



@app.route("/developer")
@developer_required
def developer():
    con = db()
    cur = con.cursor()

    cur.execute("SELECT COUNT(*) AS c FROM users WHERE role='customer'")
    customer_count = cur.fetchone()["c"]

    cur.execute("SELECT COALESCE(SUM(total_plays),0) AS total FROM user_stats")
    total_plays = cur.fetchone()["total"]

    cur.execute("""
        SELECT username, total_plays, today_plays, total_rewards
        FROM user_stats
        ORDER BY total_plays DESC
    """)
    stats = cur.fetchall()

    con.close()

    return render_template_string(
        DEVELOPER_HTML,
        stats=stats,
        customer_count=customer_count,
        total_plays=total_plays
    )

@app.route("/wallet")
@login_required
def wallet():
    username = session.get("user")
    con = db()
    cur = con.cursor()
    cur.execute("SELECT * FROM user_stats WHERE username=?", (username,))
    stat = cur.fetchone()
    con.close()

    today_plays = stat["today_plays"] if stat else 0
    total_rewards = stat["total_rewards"] if stat else 0
    progress = min(100, int((today_plays / 20) * 100))

    return render_template_string(
        WALLET_HTML,
        today_plays=today_plays,
        total_rewards=total_rewards,
        progress=progress
    )

@app.route("/account")
@login_required
def account():
    return render_template_string(ACCOUNT_HTML, user=session.get("user"), role=session.get("role"))

@app.route("/forget-account", methods=["POST"])
@login_required
def forget_account():
    if session.get("role") == "developer":
        return redirect("/account")

    username = session.get("user")
    con = db()
    cur = con.cursor()
    cur.execute("DELETE FROM users WHERE username=? AND role='customer'", (username,))
    cur.execute("DELETE FROM user_stats WHERE username=?", (username,))
    con.commit()
    con.close()
    session.clear()
    return redirect("/")

@app.route("/api/play")
def api_play():
    if "user" not in session:
        return jsonify({"ok": True, "guest": True, "message": "Login to save activity and rewards."})
    result = update_user_activity(session.get("user"))
    return jsonify({"ok": True, **result})

@app.route("/api/deezer")
def api_deezer():
    q = request.args.get("q", "arijit")
    return jsonify({"query": q, "songs": get_deezer_songs(q)})

@app.route("/api/youtube")
def api_youtube():
    q = request.args.get("q", "arijit")
    video = get_youtube_video(q)
    return jsonify({
        "query": q,
        "video": video,
        "youtube_search_url": youtube_search_url(query=q)
    })


@app.route("/api/user-stats")
@login_required
def api_user_stats():
    username = session.get("user")
    con = db()
    cur = con.cursor()
    cur.execute("SELECT * FROM user_stats WHERE username=?", (username,))
    stat = cur.fetchone()
    con.close()

    if not stat:
        return jsonify({"username": username, "total_plays": 0, "today_plays": 0, "total_rewards": 0})

    return jsonify({
        "username": stat["username"],
        "total_plays": stat["total_plays"],
        "today_plays": stat["today_plays"],
        "total_rewards": stat["total_rewards"],
        "target": 20
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

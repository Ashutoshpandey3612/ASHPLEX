from flask import Flask, render_template_string, request, redirect, session
import sqlite3
import random
from functools import wraps

app = Flask(__name__)
app.secret_key = "ashplex_secret_key"

DB_NAME = "ashplex_users.db"

def db():
    con = sqlite3.connect(DB_NAME)
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
    con.commit()
    con.close()

init_db()

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        return func(*args, **kwargs)
    return wrapper

LANDING_HTML = """
<!DOCTYPE html><html><head><title>ASHPLEX</title><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}
body{min-height:100vh;color:white;background:radial-gradient(circle at 20% 0%,rgba(250,35,59,.35),transparent 32%),radial-gradient(circle at 80% 10%,rgba(29,185,84,.28),transparent 35%),linear-gradient(180deg,#171820,#050506 65%,#000);display:flex;align-items:center;justify-content:center;padding:24px}
.wrap{max-width:980px;width:100%;display:grid;grid-template-columns:1.1fr .9fr;gap:28px;align-items:center}
.card{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.12);border-radius:34px;padding:34px;box-shadow:0 35px 100px rgba(0,0,0,.45)}
.logo{font-size:30px;font-weight:900;margin-bottom:18px}.logo span{color:#ff2d55}
h1{font-size:62px;line-height:.98;letter-spacing:-2px;margin-bottom:18px}
p{color:#cfcfd8;font-size:17px;line-height:1.65}.actions{display:flex;gap:14px;margin-top:28px;flex-wrap:wrap}
.btn{border:0;border-radius:999px;padding:15px 24px;font-weight:900;text-decoration:none;display:inline-block}
.primary{background:#ff2d55;color:white}.secondary{background:rgba(255,255,255,.10);color:white}
.preview{min-height:430px;border-radius:36px;background:linear-gradient(135deg,#ff2d55,#1db954);padding:22px;display:flex;flex-direction:column;justify-content:space-between}
.album{height:240px;border-radius:28px;background:rgba(0,0,0,.35);display:flex;align-items:center;justify-content:center;font-size:72px}
.player{background:rgba(0,0,0,.35);border-radius:24px;padding:18px}
@media(max-width:850px){.wrap{grid-template-columns:1fr}h1{font-size:42px}.preview{min-height:310px}}
</style></head><body>
<div class="wrap"><div class="card"><div class="logo">ASH<span>PLEX</span></div><h1>Your Mood.<br>Your Music.<br>Your World.</h1><p>AI mood based music platform with playlist search, like/share, rewards, premium plan, and developer analytics.</p><div class="actions"><a class="btn primary" href="/login">Continue with Mobile / Gmail</a><a class="btn secondary" href="/home">Preview App</a></div></div><div class="preview"><div class="album">🎧</div><div class="player"><h2>ASHPLEX</h2><p>Search • Play • Like • Share</p></div></div></div>
</body></html>
"""

LOGIN_HTML = """
<!DOCTYPE html><html><head><title>ASHPLEX Login</title><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}
body{min-height:100vh;background:radial-gradient(circle at 20% 0%,rgba(250,35,59,.30),transparent 34%),linear-gradient(180deg,#171820,#050506 65%,#000);color:white;display:flex;align-items:center;justify-content:center;padding:20px}
.box{width:min(460px,100%);background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.12);border-radius:32px;padding:30px;box-shadow:0 30px 90px rgba(0,0,0,.5)}
.logo{font-size:28px;font-weight:900;margin-bottom:12px}.logo span{color:#ff2d55}
h1{font-size:32px;margin-bottom:10px}p{color:#aaa;line-height:1.5;margin-bottom:20px}
label{display:block;color:#ccc;margin-bottom:8px;font-weight:700}
input{width:100%;padding:16px 18px;border-radius:18px;border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.09);color:white;outline:none;font-size:16px;margin-bottom:12px}
button,.gmail{width:100%;border:0;border-radius:999px;background:#ff2d55;color:white;padding:15px;margin-top:10px;font-weight:900;font-size:16px;cursor:pointer;text-align:center;text-decoration:none;display:block}
.gmail{background:white;color:#111}.err{color:#ff9aaa;margin-top:12px}
.otpbox{background:rgba(255,255,255,.08);border:1px dashed rgba(255,255,255,.18);border-radius:18px;padding:12px;margin:14px 0;color:#ffcf70}
.small{color:#888;font-size:13px;margin-top:16px}.divider{display:flex;align-items:center;gap:10px;margin:18px 0;color:#aaa}.divider:before,.divider:after{content:"";flex:1;height:1px;background:rgba(255,255,255,.12)}
</style></head><body>
<div class="box"><div class="logo">ASH<span>PLEX</span></div><h1>Login to ASHPLEX</h1><p>Use mobile OTP or Gmail login. User data will be saved in ASHPLEX database.</p>
{% if step == "phone" %}
<form method="POST" action="/send-otp"><label>Mobile Number</label><input name="phone" placeholder="Example: 9876543210" inputmode="numeric" maxlength="10" required><button>Send OTP</button></form>
<div class="divider">OR</div><a class="gmail" href="/gmail-login">📧 Continue with Gmail</a>
{% endif %}
{% if step == "otp" %}
<form method="POST" action="/verify-otp"><label>Enter OTP sent to {{phone}}</label><input name="otp" placeholder="Enter 6 digit OTP" inputmode="numeric" maxlength="6" required><button>Verify OTP</button></form>
<div class="otpbox">Demo OTP: <b>{{demo_otp}}</b><br>Real SMS OTP ke liye Firebase/Twilio config add karna hoga.</div><a class="gmail" href="/login">Change Number</a>
{% endif %}
{% if error %}<div class="err">{{error}}</div>{% endif %}
<div class="small">Note: Real OTP/Gmail OAuth needs Firebase or Google OAuth credentials. Current version shows teacher-demo flow.</div></div>
</body></html>
"""

HOME_HTML = """
<!DOCTYPE html><html><head><title>ASHPLEX Home</title><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}
body{background:#08090d;color:white;min-height:100vh}
.sidebar{position:fixed;left:0;top:0;bottom:0;width:245px;background:#111217;padding:28px 18px;border-right:1px solid rgba(255,255,255,.08)}
.logo{font-size:28px;font-weight:900;margin-bottom:34px}.logo span{color:#ff2d55}
.nav a{display:block;color:#ccc;text-decoration:none;padding:14px 16px;border-radius:16px;margin-bottom:8px;font-weight:700}
.nav a.active,.nav a:hover{background:#ff2d55;color:white}.main{margin-left:245px;padding:28px 34px 120px}
.top{display:flex;justify-content:space-between;align-items:center;margin-bottom:28px}.search{display:flex;gap:10px;width:min(640px,100%)}
.search input{flex:1;background:#191b23;border:1px solid rgba(255,255,255,.08);border-radius:18px;padding:15px 18px;color:white;outline:none}.search button{border:0;border-radius:18px;background:#ff2d55;color:white;font-weight:900;padding:0 22px}
.user{color:#aaa}.hero{border-radius:34px;background:linear-gradient(135deg,#ff2d55,#171820 70%);padding:36px;margin-bottom:32px}
.hero h1{font-size:56px;line-height:1;margin-bottom:14px}.hero p{color:#eee;font-size:18px}
.moods{display:flex;gap:10px;overflow-x:auto;margin-bottom:30px}.moods a{color:white;text-decoration:none;background:#181a20;border:1px solid rgba(255,255,255,.08);padding:11px 16px;border-radius:999px;font-weight:800}.moods a.active{background:#ff2d55}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:18px}.card{background:#171821;border:1px solid rgba(255,255,255,.07);border-radius:24px;padding:14px}
.cover{height:170px;border-radius:18px;background:linear-gradient(135deg,#ff2d55,#1db954);display:flex;align-items:center;justify-content:center;font-size:44px;margin-bottom:12px}
.card h3{font-size:16px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.card p{color:#aaa;font-size:13px;margin:5px 0 12px}
.actions{display:flex;gap:8px}.actions button,.actions a{border:0;background:#262936;color:white;text-decoration:none;border-radius:12px;padding:9px 11px;cursor:pointer}
.player{position:fixed;left:245px;right:0;bottom:0;height:86px;background:#111217;border-top:1px solid rgba(255,255,255,.08);display:flex;align-items:center;justify-content:space-between;padding:0 24px}
@media(max-width:850px){.sidebar{display:none}.main{margin-left:0;padding:18px 14px 110px}.hero h1{font-size:38px}.top{display:block}.search{width:100%;margin-bottom:12px}.grid{grid-template-columns:1fr}.player{left:10px;right:10px;bottom:10px;border-radius:24px}}
</style><script>
function like(btn){btn.innerText = btn.innerText.includes("❤️") ? "♡" : "❤️";}
function shareSong(name){if(navigator.share){navigator.share({title:name,text:"Listen on ASHPLEX",url:location.href});}else alert("Share: "+location.href);}
</script></head><body>
<aside class="sidebar"><div class="logo">ASH<span>PLEX</span></div><div class="nav"><a class="active" href="/home">🏠 Home</a><a href="#moods">🤖 Mood AI</a><a href="#songs">🎵 Songs</a><a href="/logout">🚪 Logout</a></div></aside>
<main class="main"><div class="top"><form class="search" method="GET" action="/home"><input name="q" value="{{q}}" placeholder="Search song or artist..."><button>Search</button></form><div class="user">Logged in: {{user}}</div></div>
<section class="hero"><h1>Your Mood.<br>Your Music.<br>Your World.</h1><p>Mobile/Gmail login, saved database user, mood playlists, like/share and ASHPLEX music player.</p></section>
<section id="moods"><h2 style="margin-bottom:14px">🤖 Mood Suggestions</h2><div class="moods">{% for m in moods %}<a class="{{'active' if mood==m.id else ''}}" href="/home?mood={{m.id}}">{{m.icon}} {{m.name}}</a>{% endfor %}</div></section>
<section id="songs"><h2 style="margin-bottom:14px">🎵 Songs / Playlist</h2><div class="grid">{% for s in songs %}<div class="card"><div class="cover">🎧</div><h3>{{s.title}}</h3><p>{{s.artist}}</p><div class="actions"><a href="/youtube?q={{s.title}} {{s.artist}}">▶ Play</a><button onclick="like(this)">♡</button><button onclick="shareSong('{{s.title}}')">📤</button></div></div>{% endfor %}</div></section></main>
<footer class="player"><b>🎧 ASHPLEX Player</b><span>Search • Play • Like • Share</span></footer>
</body></html>
"""

YOUTUBE_HTML = """
<!DOCTYPE html><html><head><title>ASHPLEX Player</title><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>body{margin:0;background:#08090d;color:white;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}.page{padding:24px;max-width:1100px;margin:auto}.card{background:#15161d;border:1px solid rgba(255,255,255,.08);border-radius:30px;padding:22px}iframe{width:100%;height:520px;border:0;border-radius:22px;background:#000}a{color:white;background:#ff2d55;text-decoration:none;padding:12px 18px;border-radius:999px;display:inline-block;margin-bottom:16px;font-weight:900}@media(max-width:850px){iframe{height:260px}.page{padding:14px}}</style></head>
<body><div class="page"><a href="/home">← Back</a><div class="card"><h1>{{q}}</h1><iframe src="https://www.youtube.com/embed?listType=search&list={{q}}" allow="autoplay; encrypted-media" allowfullscreen></iframe></div></div></body></html>
"""

SONGS = [
    {"title":"Pehla Nasha","artist":"Udit Narayan","mood":"romantic"},
    {"title":"Tujhe Dekha To","artist":"Kumar Sanu","mood":"romantic"},
    {"title":"Dheere Dheere Se","artist":"Kumar Sanu, Anuradha Paudwal","mood":"relax"},
    {"title":"Mera Dil Bhi Kitna Pagal Hai","artist":"Kumar Sanu, Alka Yagnik","mood":"romantic"},
    {"title":"Pardesi Pardesi","artist":"Udit Narayan, Alka Yagnik","mood":"sad"},
    {"title":"Sandese Aate Hain","artist":"Sonu Nigam","mood":"sad"},
    {"title":"Main Koi Aisa Geet Gaoon","artist":"Abhijeet","mood":"happy"},
    {"title":"Chura Ke Dil Mera","artist":"Kumar Sanu, Alka Yagnik","mood":"party"},
    {"title":"Tip Tip Barsa Pani","artist":"Udit Narayan, Alka Yagnik","mood":"party"},
    {"title":"Bahut Pyar Karte Hain","artist":"Anuradha Paudwal","mood":"sad"},
]

MOODS = [
    {"id":"all","name":"All","icon":"🎧"},
    {"id":"romantic","name":"Romantic","icon":"❤️"},
    {"id":"sad","name":"Sad","icon":"💔"},
    {"id":"happy","name":"Happy","icon":"😊"},
    {"id":"relax","name":"Relax","icon":"🌙"},
    {"id":"party","name":"Party","icon":"💃"},
]

def filter_songs(q="", mood="all"):
    q = (q or "").lower().strip()
    mood = (mood or "all").lower()
    data = SONGS
    if mood != "all":
        data = [s for s in data if s["mood"] == mood]
    if q:
        data = [s for s in SONGS if q in (s["title"] + " " + s["artist"]).lower()]
    return data or SONGS

def save_user(username, password_type):
    con = db()
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cur.fetchone()
    if not user:
        cur.execute("INSERT INTO users(username,password,role) VALUES(?,?,?)", (username, password_type, "customer"))
    cur.execute(
        "INSERT OR IGNORE INTO user_stats(username,total_plays,today_plays,total_rewards,last_reward_date,last_play_date) VALUES(?,?,?,?,?,?)",
        (username, 0, 0, 0, "", "")
    )
    con.commit()
    con.close()

@app.route("/")
def landing():
    if "user" in session:
        return redirect("/home")
    return render_template_string(LANDING_HTML)

@app.route("/login")
def login():
    return render_template_string(LOGIN_HTML, step="phone", error=None)

@app.route("/send-otp", methods=["POST"])
def send_otp():
    phone = request.form.get("phone", "").strip()
    if not phone.isdigit() or len(phone) != 10:
        return render_template_string(LOGIN_HTML, step="phone", error="Please enter valid 10 digit mobile number.")
    otp = str(random.randint(100000, 999999))
    session["pending_phone"] = phone
    session["pending_otp"] = otp
    return render_template_string(LOGIN_HTML, step="otp", phone=phone, demo_otp=otp, error=None)

@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    otp = request.form.get("otp", "").strip()
    phone = session.get("pending_phone")
    real = session.get("pending_otp")
    if not phone or not real:
        return redirect("/login")
    if otp != real:
        return render_template_string(LOGIN_HTML, step="otp", phone=phone, demo_otp=real, error="Wrong OTP")
    save_user(phone, "otp_login")
    session["user"] = phone
    session["role"] = "customer"
    session.pop("pending_phone", None)
    session.pop("pending_otp", None)
    return redirect("/home")

@app.route("/gmail-login")
def gmail_login():
    email = "demo.gmail.user@gmail.com"
    save_user(email, "gmail_login")
    session["user"] = email
    session["role"] = "customer"
    return redirect("/home")

@app.route("/home")
@login_required
def home():
    q = request.args.get("q", "")
    mood = request.args.get("mood", "all")
    songs = filter_songs(q, mood)
    return render_template_string(HOME_HTML, songs=songs, moods=MOODS, mood=mood, q=q, user=session.get("user"))

@app.route("/youtube")
@login_required
def youtube():
    q = request.args.get("q", "90s hindi song")
    return render_template_string(YOUTUBE_HTML, q=q)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

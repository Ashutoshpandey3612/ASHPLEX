from flask import Flask, render_template_string, request
import requests
import base64
from urllib.parse import quote_plus

app = Flask(__name__)

# ---------------------------
# ASHPLEX SVG cover fallback
# ---------------------------
def svg_cover(title="ASHPLEX", subtitle="90s Hindi"):
    safe_title = str(title).replace("&", "&amp;").replace("<", "").replace(">", "")
    safe_subtitle = str(subtitle).replace("&", "&amp;").replace("<", "").replace(">", "")
    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="600" height="600">
      <defs>
        <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#1db954"/>
          <stop offset="55%" stop-color="#101217"/>
          <stop offset="100%" stop-color="#07130b"/>
        </linearGradient>
        <radialGradient id="r" cx="25%" cy="25%" r="70%">
          <stop offset="0%" stop-color="#ffffff" stop-opacity="0.28"/>
          <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
        </radialGradient>
      </defs>
      <rect width="600" height="600" rx="55" fill="url(#g)"/>
      <rect width="600" height="600" rx="55" fill="url(#r)"/>
      <circle cx="475" cy="95" r="75" fill="#ffffff" opacity="0.10"/>
      <circle cx="110" cy="500" r="95" fill="#ffffff" opacity="0.08"/>
      <text x="48" y="95" fill="#ffffff" font-size="34" font-family="Arial" font-weight="700">ASHPLEX</text>
      <text x="48" y="300" fill="#ffffff" font-size="44" font-family="Arial" font-weight="800">{safe_title[:22]}</text>
      <text x="48" y="355" fill="#d8f8df" font-size="25" font-family="Arial">{safe_subtitle[:32]}</text>
      <text x="48" y="520" fill="#ffffff" opacity="0.75" font-size="22" font-family="Arial">Your Mood. Your Music. Your World.</text>
    </svg>
    """
    b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return "data:image/svg+xml;base64," + b64

def pick_image(song, fallback_title="ASHPLEX", fallback_artist="90s Hindi"):
    imgs = song.get("image") or []
    if isinstance(imgs, list):
        for item in reversed(imgs):
            if isinstance(item, dict) and item.get("url"):
                return item["url"]
    return svg_cover(fallback_title, fallback_artist)

# ---------------------------
# JioSaavn API
# ---------------------------
def fetch_saavn(query="90s hindi songs", limit=20):
    try:
        url = "https://saavn.dev/api/search/songs"
        params = {"query": query, "limit": limit}
        res = requests.get(url, params=params, timeout=12)
        data = res.json()
        results = data.get("data", {}).get("results") or []
        songs = []

        for s in results[:limit]:
            name = s.get("name") or s.get("title") or "Unknown Song"
            artist = s.get("primaryArtists") or s.get("primaryArtistsName") or "Unknown Artist"
            songs.append({
                "name": name,
                "artist": artist,
                "image": pick_image(s, name, artist),
                "youtube": "https://www.youtube.com/results?search_query=" + quote_plus(name + " " + artist)
            })

        if songs:
            return songs
    except Exception as e:
        print("JioSaavn API error:", e)
    return []

def fallback_songs():
    data = [
        ("Pehla Nasha", "Udit Narayan"),
        ("Tujhe Dekha To", "Kumar Sanu"),
        ("Dheere Dheere Se", "Kumar Sanu, Anuradha Paudwal"),
        ("Mera Dil Bhi Kitna Pagal Hai", "Kumar Sanu, Alka Yagnik"),
        ("Ek Ladki Ko Dekha", "Kumar Sanu"),
        ("Pardesi Pardesi", "Udit Narayan, Alka Yagnik"),
        ("Aankhon Ki Gustakhiyan", "Kumar Sanu, Kavita Krishnamurthy"),
        ("Sandese Aate Hain", "Sonu Nigam"),
        ("Main Koi Aisa Geet Gaoon", "Abhijeet"),
        ("Chura Ke Dil Mera", "Kumar Sanu, Alka Yagnik"),
        ("Tip Tip Barsa Pani", "Udit Narayan, Alka Yagnik"),
        ("Bahut Pyar Karte Hain", "Anuradha Paudwal"),
        ("Saanson Ki Zarurat Hai", "Kumar Sanu"),
        ("Dil Hai Ke Manta Nahin", "Anuradha Paudwal, Kumar Sanu"),
        ("Yeh Kaali Kaali Aankhen", "Kumar Sanu"),
        ("Ole Ole", "Abhijeet"),
    ]
    return [{"name": n, "artist": a, "image": svg_cover(n, a), "youtube": "https://www.youtube.com/results?search_query=" + quote_plus(n + " " + a)} for n, a in data]

def get_songs(query="90s hindi songs", limit=20):
    songs = fetch_saavn(query, limit)
    return songs if songs else fallback_songs()[:limit]

# ---------------------------
# Mood recommendation
# ---------------------------
def mood_query(mood):
    mood = (mood or "classic").lower()
    mapping = {
        "classic": "90s hindi songs Kumar Sanu Udit Narayan Alka Yagnik",
        "romantic": "90s hindi romantic songs Kumar Sanu Alka Yagnik",
        "sad": "90s hindi sad songs Kumar Sanu Sonu Nigam",
        "happy": "90s hindi happy songs Udit Narayan Abhijeet",
        "relax": "90s hindi soft songs Anuradha Paudwal Sadhana Sargam",
        "party": "90s bollywood dance songs Udit Narayan Alka Yagnik",
        "focus": "old hindi lofi songs 90s",
    }
    return mapping.get(mood, mapping["classic"])

def get_playlists():
    return [
        {"title": "90s Hindi Classics", "subtitle": "Kumar Sanu • Udit • Alka", "query": "90s hindi songs", "image": svg_cover("90s Hindi", "Classics")},
        {"title": "Romantic 90s", "subtitle": "Love songs collection", "query": "90s hindi romantic songs", "image": svg_cover("Romantic", "90s Hindi")},
        {"title": "Kumar Sanu Hits", "subtitle": "Evergreen voice", "query": "Kumar Sanu 90s hindi songs", "image": svg_cover("Kumar Sanu", "Hits")},
        {"title": "Udit Narayan Mix", "subtitle": "Melody playlist", "query": "Udit Narayan 90s hindi songs", "image": svg_cover("Udit Narayan", "Mix")},
        {"title": "Alka Yagnik Hits", "subtitle": "Queen of melody", "query": "Alka Yagnik 90s hindi songs", "image": svg_cover("Alka Yagnik", "Hits")},
        {"title": "Sonu Nigam Classics", "subtitle": "Golden voice", "query": "Sonu Nigam 90s hindi songs", "image": svg_cover("Sonu Nigam", "Classics")},
        {"title": "Anuradha Paudwal", "subtitle": "Soft devotional + romantic", "query": "Anuradha Paudwal 90s hindi songs", "image": svg_cover("Anuradha", "Paudwal")},
        {"title": "Abhijeet Special", "subtitle": "Energetic 90s vocals", "query": "Abhijeet 90s hindi songs", "image": svg_cover("Abhijeet", "Special")},
    ]

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ASHPLEX</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'Poppins',sans-serif}
body{background:#0b0b0f;color:white;overflow-x:hidden}
.app{display:flex;min-height:100vh}
.sidebar{width:250px;background:#111217;padding:30px 20px;position:fixed;top:0;left:0;bottom:0;border-right:1px solid rgba(255,255,255,.06)}
.logo{font-size:34px;font-weight:800;color:#1db954;margin-bottom:42px}
.menu{display:flex;flex-direction:column;gap:14px}
.menu a{text-decoration:none;color:#bbb;padding:15px 18px;border-radius:16px;transition:.25s;font-weight:500}
.menu a:hover,.menu .active{background:#1db954;color:white}
.main{margin-left:250px;flex:1;padding:30px;padding-bottom:145px}
.top{display:flex;justify-content:space-between;align-items:center;margin-bottom:28px;gap:18px}
.search{width:460px}
.search input{width:100%;padding:18px 22px;border:0;outline:0;background:#1a1c22;border-radius:18px;color:white;font-size:15px}
.profile{color:#cfd0d5;white-space:nowrap}
.hero{min-height:330px;border-radius:34px;padding:42px;display:flex;justify-content:space-between;align-items:center;background:linear-gradient(135deg,#1db954,#121212 75%);overflow:hidden;margin-bottom:38px;position:relative}
.hero:after{content:"";position:absolute;right:-80px;top:-90px;width:360px;height:360px;background:rgba(255,255,255,.12);filter:blur(70px);border-radius:50%}
.hero h1{font-size:66px;line-height:1;margin-bottom:18px;position:relative;z-index:2}
.hero p{font-size:18px;color:#e6e6e6;max-width:640px;line-height:1.6;position:relative;z-index:2}
.hero-buttons{margin-top:28px;display:flex;gap:15px;position:relative;z-index:2}
.btn{padding:15px 28px;border:0;border-radius:40px;font-size:15px;font-weight:700;cursor:pointer;text-decoration:none;display:inline-block}
.play{background:white;color:black}.explore{background:rgba(255,255,255,.16);color:white}
.hero img{width:270px;height:270px;object-fit:cover;border-radius:30px;box-shadow:0 24px 60px rgba(0,0,0,.5);position:relative;z-index:2}
.section{margin-top:34px}
.section-title{display:flex;justify-content:space-between;align-items:center;margin-bottom:18px}
.section-title h2{font-size:32px}.section-title span{color:#aaa}
.mood-row{display:flex;gap:12px;overflow-x:auto;padding-bottom:8px}
.mood-row a{flex:0 0 auto;text-decoration:none;color:white;background:#181a20;border:1px solid rgba(255,255,255,.07);padding:12px 18px;border-radius:999px;font-weight:700}
.mood-row a.active{background:#1db954}
.playlist-row{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:18px}
.playlist-card{background:linear-gradient(135deg,#1b1d24,#111217);border-radius:24px;padding:14px;text-decoration:none;color:white;transition:.25s;border:1px solid rgba(255,255,255,.06)}
.playlist-card:hover{transform:translateY(-6px);background:#22252e}
.playlist-card img{width:100%;aspect-ratio:1/1;border-radius:18px;object-fit:cover;margin-bottom:12px}
.playlist-card h3{font-size:17px}.playlist-card p{font-size:13px;color:#aaa}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:22px}
.card{background:#181a20;padding:15px;border-radius:22px;transition:.25s;position:relative}
.card:hover{transform:translateY(-8px);background:#22252e}
.card img{width:100%;aspect-ratio:1/1;border-radius:18px;object-fit:cover;margin-bottom:14px;background:#111}
.card h3{font-size:17px;margin-bottom:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.card p{font-size:13px;color:#aaa;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.play-btn{position:absolute;right:20px;bottom:92px;width:54px;height:54px;border-radius:50%;background:#1db954;display:flex;align-items:center;justify-content:center;font-size:22px;opacity:0;transform:translateY(12px);transition:.25s}
.card:hover .play-btn{opacity:1;transform:translateY(0)}
.actions{display:flex;gap:10px;margin-top:14px}.actions button{border:0;background:#262932;color:white;padding:10px 14px;border-radius:12px;cursor:pointer}
.player{position:fixed;bottom:0;left:250px;right:0;height:95px;background:#111217;border-top:1px solid rgba(255,255,255,.06);display:grid;grid-template-columns:300px 1fr 220px;align-items:center;padding:0 25px;z-index:99}
.now{display:flex;align-items:center;gap:15px}.now img{width:65px;height:65px;border-radius:14px;object-fit:cover}
.song-name{font-size:16px;font-weight:700}.artist{font-size:13px;color:#aaa}
.center{display:flex;flex-direction:column;align-items:center;gap:10px}.controls{display:flex;align-items:center;gap:22px;font-size:22px}
.big{width:56px;height:56px;border-radius:50%;background:white;color:black;display:flex;align-items:center;justify-content:center;font-size:24px}
.bar{width:70%;height:5px;background:#2f3138;border-radius:20px;overflow:hidden}.bar div{width:45%;height:100%;background:#1db954}
.mobile-nav{display:none}
.ad{margin-top:24px;background:linear-gradient(135deg,#22252e,#15161b);border:1px solid rgba(255,255,255,.06);padding:18px;border-radius:22px;text-align:center;color:#bbb}
@media(max-width:850px){
.sidebar{display:none}.main{margin-left:0;padding:18px;padding-bottom:180px}.top{display:block}.search{width:100%;margin-bottom:20px}.profile{display:none}
.hero{height:auto;flex-direction:column;text-align:center;padding:25px}.hero h1{font-size:42px}.hero img{width:100%;max-width:280px;height:auto;margin-top:25px}
.playlist-row{display:flex;overflow-x:auto;gap:14px;padding-bottom:8px}.playlist-card{min-width:165px}
.grid{grid-template-columns:1fr}.player{left:10px;right:10px;bottom:82px;height:82px;border-radius:22px;grid-template-columns:1fr auto;padding:12px 16px}
.center .bar,.right{display:none}.controls{gap:14px;font-size:18px}.big{width:48px;height:48px}
.mobile-nav{display:grid;grid-template-columns:repeat(5,1fr);position:fixed;bottom:0;left:0;right:0;height:75px;background:#111217;border-top:1px solid rgba(255,255,255,.06)}
.mobile-nav a{display:flex;flex-direction:column;justify-content:center;align-items:center;color:white;text-decoration:none;font-size:12px}
}
</style>
<script>
function shareSong(name){
  if(navigator.share){
    navigator.share({title:name, text:"Listen on ASHPLEX", url:window.location.href});
  }else{
    alert("Share: " + window.location.href);
  }
}
</script>
</head>
<body>
<div class="app">
<div class="sidebar">
  <div class="logo">ASHPLEX</div>
  <div class="menu">
    <a class="active" href="/">🏠 Home</a>
    <a href="#search">🔍 Search</a>
    <a href="#moods">🤖 Mood AI</a>
    <a href="#playlists">🎵 Playlists</a>
    <a href="#premium">👑 Premium</a>
    <a href="#rewards">💰 Rewards</a>
  </div>
</div>

<div class="main">
  <div class="top" id="search">
    <form class="search" method="GET">
      <input name="q" value="{{ query }}" placeholder="Search 90s Hindi Songs...">
      <input type="hidden" name="mood" value="{{ mood }}">
    </form>
    <div class="profile">👑 Premium • Created by Ashutosh Pandey</div>
  </div>

  <div class="hero">
    <div>
      <h1>Your Mood.<br>Your Music.<br>Your World.</h1>
      <p>AI-powered Hindi music platform with full playlists, real covers, mood suggestions, rewards and premium UI.</p>
      <div class="hero-buttons">
        <a class="btn play" href="#trending">▶ Play</a>
        <a class="btn explore" href="#moods">🤖 Mood AI</a>
      </div>
    </div>
    <img src="{{ songs[0].image }}">
  </div>

  <div class="section" id="moods">
    <div class="section-title">
      <h2>🤖 Mood Suggestions</h2>
      <span>Music according to your mood</span>
    </div>
    <div class="mood-row">
      <a class="{{ 'active' if mood=='classic' else '' }}" href="/?mood=classic">🎧 Classic</a>
      <a class="{{ 'active' if mood=='romantic' else '' }}" href="/?mood=romantic">❤️ Romantic</a>
      <a class="{{ 'active' if mood=='sad' else '' }}" href="/?mood=sad">💔 Sad</a>
      <a class="{{ 'active' if mood=='happy' else '' }}" href="/?mood=happy">😊 Happy</a>
      <a class="{{ 'active' if mood=='relax' else '' }}" href="/?mood=relax">🌙 Relax</a>
      <a class="{{ 'active' if mood=='party' else '' }}" href="/?mood=party">💃 Party</a>
      <a class="{{ 'active' if mood=='focus' else '' }}" href="/?mood=focus">🎯 Focus</a>
    </div>
  </div>

  <div class="section" id="playlists">
    <div class="section-title">
      <h2>🎵 Full Playlists</h2>
      <span>Click any playlist to open full songs</span>
    </div>
    <div class="playlist-row">
      {% for p in playlists %}
      <a class="playlist-card" href="/?q={{ p.query }}">
        <img src="{{ p.image }}">
        <h3>{{ p.title }}</h3>
        <p>{{ p.subtitle }}</p>
      </a>
      {% endfor %}
    </div>
  </div>

  <div class="section" id="trending">
    <div class="section-title">
      <h2>🔥 Recommended Songs</h2>
      <span>{{ songs|length }} tracks</span>
    </div>
    <div class="grid">
      {% for song in songs %}
      <div class="card">
        <img src="{{ song.image }}">
        <a class="play-btn" href="{{ song.youtube }}" target="_blank" style="color:white;text-decoration:none">▶</a>
        <h3>{{ song.name }}</h3>
        <p>{{ song.artist }}</p>
        <div class="actions">
          <button>❤️</button>
          <button onclick="shareSong('{{ song.name }}')">📤</button>
          <button>➕</button>
        </div>
      </div>
      {% endfor %}
    </div>
  </div>

  <div class="ad" id="premium">📢 Advertisement Banner • Upgrade to Premium for ad-free ASHPLEX</div>
</div>

<div class="player">
  <div class="now">
    <img src="{{ songs[0].image }}">
    <div>
      <div class="song-name">{{ songs[0].name }}</div>
      <div class="artist">{{ songs[0].artist }}</div>
    </div>
  </div>
  <div class="center">
    <div class="controls">⏮ <div class="big">❚❚</div> ⏭</div>
    <div class="bar"><div></div></div>
  </div>
  <div class="right">🔊 Volume</div>
</div>

<div class="mobile-nav">
  <a href="/">🏠<br>Home</a>
  <a href="#moods">🤖<br>Mood</a>
  <a href="#playlists">🎵<br>Playlist</a>
  <a href="#premium">👑<br>Premium</a>
  <a href="#trending">➕<br>Create</a>
</div>
</div>
</body>
</html>
"""

@app.route("/")
def home():
    mood = request.args.get("mood", "classic")
    q = request.args.get("q")
    query = q or mood_query(mood)
    songs = get_songs(query, 24)
    playlists = get_playlists()
    return render_template_string(HTML, songs=songs, playlists=playlists, query=query, mood=mood)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

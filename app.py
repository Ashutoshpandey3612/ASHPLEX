from flask import Flask, render_template_string, request
import base64
import html
from urllib.parse import quote_plus

app = Flask(__name__)

def svg_cover(title="ASHPLEX", subtitle="Your Music"):
    title = html.escape(str(title))[:24]
    subtitle = html.escape(str(subtitle))[:32]
    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="700" height="700">
      <defs>
        <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#ff2d55"/>
          <stop offset="45%" stop-color="#18213a"/>
          <stop offset="100%" stop-color="#08080b"/>
        </linearGradient>
        <radialGradient id="r" cx="30%" cy="20%" r="80%">
          <stop offset="0%" stop-color="#ffffff" stop-opacity="0.28"/>
          <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
        </radialGradient>
      </defs>
      <rect width="700" height="700" rx="70" fill="url(#g)"/>
      <rect width="700" height="700" rx="70" fill="url(#r)"/>
      <circle cx="565" cy="115" r="88" fill="#ffffff" opacity="0.10"/>
      <circle cx="120" cy="585" r="115" fill="#ffffff" opacity="0.08"/>
      <text x="58" y="100" fill="#ffffff" font-size="38" font-family="Arial" font-weight="700">ASHPLEX</text>
      <text x="58" y="350" fill="#ffffff" font-size="52" font-family="Arial" font-weight="800">{title}</text>
      <text x="58" y="410" fill="#e8e8f3" font-size="28" font-family="Arial">{subtitle}</text>
      <text x="58" y="610" fill="#ffffff" opacity="0.72" font-size="24" font-family="Arial">Your Mood. Your Music. Your World.</text>
    </svg>
    """
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()

SONGS = [
    {"title":"Pehla Nasha", "artist":"Udit Narayan", "mood":"romantic", "cover":svg_cover("Pehla Nasha","Udit Narayan")},
    {"title":"Tujhe Dekha To", "artist":"Kumar Sanu", "mood":"romantic", "cover":svg_cover("Tujhe Dekha To","Kumar Sanu")},
    {"title":"Dheere Dheere Se", "artist":"Kumar Sanu, Anuradha Paudwal", "mood":"relax", "cover":svg_cover("Dheere Dheere","Kumar Sanu")},
    {"title":"Chura Ke Dil Mera", "artist":"Kumar Sanu, Alka Yagnik", "mood":"happy", "cover":svg_cover("Chura Ke Dil","Alka Yagnik")},
    {"title":"Main Koi Aisa Geet Gaoon", "artist":"Abhijeet", "mood":"happy", "cover":svg_cover("Aisa Geet","Abhijeet")},
    {"title":"Sandese Aate Hain", "artist":"Sonu Nigam", "mood":"sad", "cover":svg_cover("Sandese","Sonu Nigam")},
    {"title":"Bahut Pyar Karte Hain", "artist":"Anuradha Paudwal", "mood":"sad", "cover":svg_cover("Bahut Pyar","Anuradha")},
    {"title":"Pardesi Pardesi", "artist":"Udit Narayan, Alka Yagnik", "mood":"sad", "cover":svg_cover("Pardesi","Udit • Alka")},
    {"title":"Tip Tip Barsa Pani", "artist":"Udit Narayan, Alka Yagnik", "mood":"party", "cover":svg_cover("Tip Tip","Party Mix")},
    {"title":"Ole Ole", "artist":"Abhijeet", "mood":"party", "cover":svg_cover("Ole Ole","Abhijeet")},
    {"title":"Aankhon Ki Gustakhiyan", "artist":"Kumar Sanu, Kavita Krishnamurthy", "mood":"romantic", "cover":svg_cover("Gustakhiyan","Kavita • Sanu")},
    {"title":"Saanson Ki Zarurat Hai", "artist":"Kumar Sanu", "mood":"relax", "cover":svg_cover("Saanson Ki","Kumar Sanu")},
]

PLAYLISTS = [
    {"name":"90s Hindi Classics","desc":"Evergreen Bollywood hits","query":"classic","cover":svg_cover("90s Hindi","Classics")},
    {"name":"Romantic 90s","desc":"Love songs collection","query":"romantic","cover":svg_cover("Romantic","90s Collection")},
    {"name":"Sad Classics","desc":"Emotional melodies","query":"sad","cover":svg_cover("Sad","Classics")},
    {"name":"Party Retro","desc":"Dance & energy","query":"party","cover":svg_cover("Party","Retro Mix")},
    {"name":"Relax Mood","desc":"Soft listening","query":"relax","cover":svg_cover("Relax","Soft 90s")},
    {"name":"Happy Vibes","desc":"Feel-good tracks","query":"happy","cover":svg_cover("Happy","Vibes")},
]

def filter_songs(q="", mood="classic"):
    q = (q or "").lower().strip()
    mood = (mood or "classic").lower()
    data = SONGS
    if mood != "classic":
        data = [s for s in data if s["mood"] == mood]
    if q:
        data = [s for s in SONGS if q in s["title"].lower() or q in s["artist"].lower()]
    return data or SONGS

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ASHPLEX</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:Poppins,sans-serif}
:root{--bg:#07070b;--panel:#111118;--card:#171821;--muted:#9b9baa;--pink:#ff2d55;--green:#1db954}
body{background:radial-gradient(circle at 70% 0%,rgba(255,45,85,.22),transparent 34%),linear-gradient(180deg,#12121a,#050506 58%,#000);color:white;overflow:hidden}
.app{width:100vw;height:100vh;display:grid;grid-template-columns:260px 1fr;grid-template-rows:1fr 96px}
.sidebar{background:rgba(17,17,24,.92);border-right:1px solid rgba(255,255,255,.06);padding:26px 18px}
.logo{font-size:30px;font-weight:900;margin-bottom:34px;color:white;letter-spacing:-1px}.logo span{color:var(--pink)}
.nav a{display:flex;gap:12px;align-items:center;color:#c9c9d3;text-decoration:none;padding:14px 16px;border-radius:16px;margin-bottom:8px;font-weight:650}
.nav a.active,.nav a:hover{background:linear-gradient(135deg,var(--pink),#7b2cff);color:white;box-shadow:0 14px 35px rgba(255,45,85,.25)}
.creator{position:absolute;bottom:24px;color:#ff9aaa;font-size:12px;line-height:1.5}
.main{padding:26px 34px 125px;overflow-y:auto}
.top{display:flex;align-items:center;justify-content:space-between;margin-bottom:24px}
.search{width:min(520px,100%)}.search input{width:100%;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.08);outline:none;color:white;padding:15px 18px;border-radius:18px}
.profile{color:#ccc;background:rgba(255,255,255,.07);padding:12px 16px;border-radius:999px;font-size:14px}
.hero{min-height:330px;border-radius:34px;padding:34px;display:grid;grid-template-columns:1fr 290px;gap:30px;align-items:center;background:linear-gradient(135deg,rgba(255,45,85,.55),rgba(29,185,84,.23),rgba(255,255,255,.04));border:1px solid rgba(255,255,255,.10);box-shadow:0 32px 100px rgba(0,0,0,.45);overflow:hidden}
.eyebrow{color:#ffd8df;text-transform:uppercase;font-size:12px;font-weight:800;letter-spacing:1.4px;margin-bottom:12px}
.hero h1{font-size:68px;line-height:.96;letter-spacing:-2px;margin-bottom:18px}
.hero p{color:#ececf3;font-size:17px;line-height:1.65;max-width:720px}
.hero .btns{display:flex;gap:14px;margin-top:25px}.btn{border:0;border-radius:999px;padding:14px 22px;font-weight:800;text-decoration:none;color:white;cursor:pointer}.primary{background:white;color:#111}.secondary{background:rgba(255,255,255,.14)}
.hero-cover{width:290px;height:290px;border-radius:34px;object-fit:cover;box-shadow:0 26px 80px rgba(0,0,0,.55)}
.section{margin-top:34px}.section-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:18px}.section h2{font-size:30px}.section-head span{color:var(--muted)}
.moods{display:flex;gap:12px;overflow-x:auto;padding-bottom:4px}.moods a{white-space:nowrap;text-decoration:none;color:white;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.08);padding:11px 16px;border-radius:999px;font-weight:700}.moods a.active{background:var(--pink)}
.playlists{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:18px}.playlist{background:linear-gradient(135deg,rgba(255,255,255,.09),rgba(255,255,255,.03));border:1px solid rgba(255,255,255,.08);border-radius:24px;padding:14px;text-decoration:none;color:white;transition:.25s}.playlist:hover{transform:translateY(-7px)}.playlist img{width:100%;aspect-ratio:1/1;border-radius:19px;object-fit:cover;margin-bottom:12px}.playlist p{color:var(--muted);font-size:13px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(185px,1fr));gap:20px}.card{background:rgba(255,255,255,.065);border:1px solid rgba(255,255,255,.07);border-radius:24px;padding:14px;position:relative;transition:.25s}.card:hover{transform:translateY(-8px);background:rgba(255,255,255,.10)}.card img{width:100%;aspect-ratio:1/1;border-radius:19px;object-fit:cover;margin-bottom:12px}.card h3{font-size:16px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.card p{color:var(--muted);font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.play-float{position:absolute;right:22px;bottom:88px;width:48px;height:48px;border-radius:50%;background:var(--pink);color:white;border:0;font-size:18px;cursor:pointer;opacity:0;transition:.2s}.card:hover .play-float{opacity:1}.actions{display:flex;gap:8px;margin-top:12px}.actions button{background:#242633;border:0;color:white;border-radius:12px;padding:9px 12px;cursor:pointer}
.player{grid-column:1/3;background:rgba(10,10,14,.92);border-top:1px solid rgba(255,255,255,.08);backdrop-filter:blur(22px);display:grid;grid-template-columns:330px 1fr 240px;align-items:center;padding:0 26px}.now{display:flex;gap:15px;align-items:center}.now img{width:68px;height:68px;border-radius:16px;object-fit:cover}.now h4{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:210px}.now p{color:var(--muted);font-size:12px}.controls{text-align:center}.buttons{display:flex;justify-content:center;align-items:center;gap:22px;margin-bottom:10px}.round{width:54px;height:54px;border-radius:50%;border:0;background:white;color:#111;font-size:22px;font-weight:900;cursor:pointer}.ctrl{background:transparent;border:0;color:white;font-size:20px;cursor:pointer}.bar{height:5px;background:#2d2d35;border-radius:999px;overflow:hidden;width:75%;margin:auto}.fill{height:100%;width:38%;background:var(--pink)}.volume{text-align:right;color:#ccc}
.mobilebar{display:none}
@media(max-width:850px){
body{overflow:auto}.app{display:block;height:auto;min-height:100vh;padding-bottom:160px}.sidebar{display:none}.main{padding:16px 14px 145px}.top{display:block}.profile{display:none}.search{width:100%;margin-bottom:14px}.hero{display:block;text-align:left;min-height:auto;padding:20px;border-radius:30px}.hero h1{font-size:39px;letter-spacing:-1px}.hero-cover{width:100%;height:auto;aspect-ratio:1/1;margin-top:20px;border-radius:28px}.playlists{display:flex;overflow-x:auto;gap:14px}.playlist{min-width:165px}.grid{grid-template-columns:1fr;gap:12px}.card{display:grid;grid-template-columns:78px 1fr;gap:13px;align-items:center}.card img{margin:0}.play-float{opacity:1;right:14px;bottom:14px;width:38px;height:38px}.player{position:fixed;left:10px;right:10px;bottom:82px;height:78px;grid-template-columns:1fr auto;border-radius:24px;padding:10px 14px;z-index:20}.now img{width:56px;height:56px}.controls .bar,.volume,.ctrl{display:none}.round{width:48px;height:48px}.mobilebar{display:grid;grid-template-columns:repeat(5,1fr);position:fixed;left:0;right:0;bottom:0;height:76px;background:rgba(8,8,10,.96);backdrop-filter:blur(20px);z-index:30}.mobilebar a{text-decoration:none;color:#ddd;display:flex;flex-direction:column;align-items:center;justify-content:center;font-size:11px}.mobilebar span{font-size:22px;margin-bottom:3px}}
</style>
<script>
const songs = {{ songs|tojson }};
let current = 0;
function playSong(i){
  current=i;
  const s=songs[i];
  document.getElementById("pimg").src=s.cover;
  document.getElementById("ptitle").innerText=s.title;
  document.getElementById("partist").innerText=s.artist;
  document.getElementById("mainBtn").innerText="Ⅱ";
}
function shareSong(title){
  if(navigator.share){navigator.share({title:title,text:"Listen on ASHPLEX",url:location.href});}
  else alert("Share ASHPLEX: "+location.href);
}
</script>
</head>
<body>
<div class="app">
  <aside class="sidebar">
    <div class="logo">ASH<span>PLEX</span></div>
    <nav class="nav">
      <a class="active" href="/">🏠 Home</a>
      <a href="#moods">🤖 Mood AI</a>
      <a href="#playlists">🎵 Playlists</a>
      <a href="#songs">❤️ Songs</a>
      <a href="#premium">👑 Premium</a>
      <a href="#rewards">💰 Rewards</a>
    </nav>
    <div class="creator">Created by<br><b>Ashutosh Pandey</b></div>
  </aside>

  <main class="main">
    <div class="top">
      <form class="search"><input name="q" value="{{ q }}" placeholder="Search 90s Hindi songs..."></form>
      <div class="profile">👑 Premium • ASHPLEX</div>
    </div>

    <section class="hero">
      <div>
        <div class="eyebrow">AI Music Platform</div>
        <h1>Your Mood.<br>Your Music.<br>Your World.</h1>
        <p>A real music-app style ASHPLEX dashboard with mood suggestions, playlists, premium UI, like/share, and responsive phone + Mac layout.</p>
        <div class="btns">
          <a class="btn primary" href="#songs">▶ Play Now</a>
          <a class="btn secondary" href="#playlists">🎵 Explore</a>
        </div>
      </div>
      <img class="hero-cover" src="{{ songs[0].cover }}">
    </section>

    <section class="section" id="moods">
      <div class="section-head"><h2>🤖 Mood Suggestions</h2><span>Choose your mood</span></div>
      <div class="moods">
        {% for m in moods %}
        <a class="{{ 'active' if mood==m.id else '' }}" href="/?mood={{m.id}}">{{m.icon}} {{m.name}}</a>
        {% endfor %}
      </div>
    </section>

    <section class="section" id="playlists">
      <div class="section-head"><h2>🎵 Full Playlists</h2><span>Curated sections</span></div>
      <div class="playlists">
        {% for p in playlists %}
        <a class="playlist" href="/?mood={{p.mood}}">
          <img src="{{p.cover}}">
          <h3>{{p.name}}</h3>
          <p>{{p.desc}}</p>
        </a>
        {% endfor %}
      </div>
    </section>

    <section class="section" id="songs">
      <div class="section-head"><h2>🔥 Recommended Songs</h2><span>{{ songs|length }} tracks</span></div>
      <div class="grid">
        {% for s in songs %}
        <div class="card">
          <img src="{{s.cover}}">
          <button class="play-float" onclick="playSong({{loop.index0}})">▶</button>
          <div>
            <h3>{{s.title}}</h3>
            <p>{{s.artist}}</p>
            <div class="actions">
              <button>❤️</button>
              <button onclick="shareSong('{{s.title}}')">📤</button>
              <button>➕</button>
            </div>
          </div>
        </div>
        {% endfor %}
      </div>
    </section>

    <div class="section" id="premium">
      <div class="section-head"><h2>👑 Premium</h2><span>Ad-free future feature</span></div>
      <div style="background:rgba(255,255,255,.07);border-radius:24px;padding:20px;color:#ddd">Premium users can get ad-free experience, special themes and reward boosters.</div>
    </div>
  </main>

  <footer class="player">
    <div class="now">
      <img id="pimg" src="{{songs[0].cover}}">
      <div><h4 id="ptitle">{{songs[0].title}}</h4><p id="partist">{{songs[0].artist}}</p></div>
    </div>
    <div class="controls">
      <div class="buttons"><button class="ctrl">⏮</button><button id="mainBtn" class="round">▶</button><button class="ctrl">⏭</button></div>
      <div class="bar"><div class="fill"></div></div>
    </div>
    <div class="volume">🔊 Volume</div>
  </footer>

  <nav class="mobilebar">
    <a href="/"><span>🏠</span>Home</a>
    <a href="#moods"><span>🤖</span>Mood</a>
    <a href="#playlists"><span>🎵</span>Playlist</a>
    <a href="#premium"><span>👑</span>Premium</a>
    <a href="#songs"><span>➕</span>Create</a>
  </nav>
</div>
</body>
</html>
"""

@app.route("/")
def home():
    q = request.args.get("q","")
    mood = request.args.get("mood","classic")
    songs = filter_songs(q, mood)
    moods = [
        {"id":"classic","name":"Classic","icon":"🎧"},
        {"id":"romantic","name":"Romantic","icon":"❤️"},
        {"id":"sad","name":"Sad","icon":"💔"},
        {"id":"happy","name":"Happy","icon":"😊"},
        {"id":"relax","name":"Relax","icon":"🌙"},
        {"id":"party","name":"Party","icon":"💃"},
    ]
    playlists = [
        {"name":"90s Hindi Classics","desc":"Evergreen voices","mood":"classic","cover":svg_cover("90s Hindi","Classics")},
        {"name":"Romantic 90s","desc":"Love collection","mood":"romantic","cover":svg_cover("Romantic","90s")},
        {"name":"Sad Classics","desc":"Emotional songs","mood":"sad","cover":svg_cover("Sad","Classics")},
        {"name":"Happy Vibes","desc":"Feel good tracks","mood":"happy","cover":svg_cover("Happy","Vibes")},
        {"name":"Relax Mode","desc":"Soft listening","mood":"relax","cover":svg_cover("Relax","Mode")},
        {"name":"Party Retro","desc":"Dance hits","mood":"party","cover":svg_cover("Party","Retro")},
    ]
    return render_template_string(HTML, songs=songs, moods=moods, playlists=playlists, mood=mood, q=q)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

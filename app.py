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
      <text x="58" y="610" fill="#ffffff" opacity="0.72" font-size="24" font-family="Arial">Search. Play. Like. Share.</text>
    </svg>
    """
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()

AUDIO = [
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-6.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-7.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-9.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-10.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-11.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-12.mp3",
]

CATALOG = [
    ("Pehla Nasha","Udit Narayan","romantic"),
    ("Tujhe Dekha To","Kumar Sanu","romantic"),
    ("Dheere Dheere Se","Kumar Sanu, Anuradha Paudwal","relax"),
    ("Mera Dil Bhi Kitna Pagal Hai","Kumar Sanu, Alka Yagnik","romantic"),
    ("Ek Ladki Ko Dekha","Kumar Sanu","romantic"),
    ("Pardesi Pardesi","Udit Narayan, Alka Yagnik","sad"),
    ("Aankhon Ki Gustakhiyan","Kumar Sanu, Kavita Krishnamurthy","romantic"),
    ("Sandese Aate Hain","Sonu Nigam","sad"),
    ("Main Koi Aisa Geet Gaoon","Abhijeet","happy"),
    ("Chura Ke Dil Mera","Kumar Sanu, Alka Yagnik","party"),
    ("Tip Tip Barsa Pani","Udit Narayan, Alka Yagnik","party"),
    ("Bahut Pyar Karte Hain","Anuradha Paudwal","sad"),
    ("Saanson Ki Zarurat Hai","Kumar Sanu","relax"),
    ("Ole Ole","Abhijeet","party"),
    ("Yeh Kaali Kaali Aankhen","Kumar Sanu","party"),
    ("Do Dil Mil Rahe Hain","Kumar Sanu","romantic"),
    ("Ab Tere Bin","Kumar Sanu","sad"),
    ("Jaadu Teri Nazar","Udit Narayan","romantic"),
    ("Raja Ko Rani Se","Udit Narayan, Alka Yagnik","romantic"),
    ("Kal Ho Naa Ho","Sonu Nigam","sad"),
]

SONGS = []
for i, (title, artist, mood) in enumerate(CATALOG):
    SONGS.append({
        "id": i,
        "title": title,
        "artist": artist,
        "mood": mood,
        "cover": svg_cover(title, artist),
        "audio": AUDIO[i % len(AUDIO)],
        "search": f"{title} {artist} {mood} 90s hindi bollywood".lower()
    })

def filter_songs(q="", mood="all"):
    q = (q or "").strip().lower()
    mood = (mood or "all").lower()
    data = SONGS
    if mood != "all":
        data = [s for s in data if s["mood"] == mood]
    if q:
        data = [s for s in SONGS if q in s["search"]]
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
.sidebar{background:rgba(17,17,24,.92);border-right:1px solid rgba(255,255,255,.06);padding:26px 18px;position:relative}
.logo{font-size:30px;font-weight:900;margin-bottom:34px;color:white;letter-spacing:-1px}.logo span{color:var(--pink)}
.nav a{display:flex;gap:12px;align-items:center;color:#c9c9d3;text-decoration:none;padding:14px 16px;border-radius:16px;margin-bottom:8px;font-weight:650}
.nav a.active,.nav a:hover{background:linear-gradient(135deg,var(--pink),#7b2cff);color:white;box-shadow:0 14px 35px rgba(255,45,85,.25)}
.creator{position:absolute;bottom:24px;color:#ff9aaa;font-size:12px;line-height:1.5}
.main{padding:26px 34px 125px;overflow-y:auto}
.top{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:24px}
.search{flex:1;max-width:650px;display:flex;gap:10px}.search input{flex:1;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.08);outline:none;color:white;padding:15px 18px;border-radius:18px}.search button{border:0;background:var(--pink);color:white;border-radius:18px;padding:0 22px;font-weight:800;cursor:pointer}
.profile{color:#ccc;background:rgba(255,255,255,.07);padding:12px 16px;border-radius:999px;font-size:14px}
.hero{min-height:290px;border-radius:34px;padding:32px;display:grid;grid-template-columns:1fr 250px;gap:30px;align-items:center;background:linear-gradient(135deg,rgba(255,45,85,.55),rgba(29,185,84,.20),rgba(255,255,255,.04));border:1px solid rgba(255,255,255,.10);box-shadow:0 32px 100px rgba(0,0,0,.45);overflow:hidden}
.eyebrow{color:#ffd8df;text-transform:uppercase;font-size:12px;font-weight:800;letter-spacing:1.4px;margin-bottom:12px}
.hero h1{font-size:56px;line-height:.98;letter-spacing:-2px;margin-bottom:16px}
.hero p{color:#ececf3;font-size:16px;line-height:1.65;max-width:760px}
.hero-cover{width:250px;height:250px;border-radius:32px;object-fit:cover;box-shadow:0 26px 80px rgba(0,0,0,.55)}
.section{margin-top:30px}.section-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}.section h2{font-size:28px}.section-head span{color:var(--muted)}
.moods{display:flex;gap:12px;overflow-x:auto;padding-bottom:4px}.moods a{white-space:nowrap;text-decoration:none;color:white;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.08);padding:11px 16px;border-radius:999px;font-weight:700}.moods a.active{background:var(--pink)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(185px,1fr));gap:20px}.card{background:rgba(255,255,255,.065);border:1px solid rgba(255,255,255,.07);border-radius:24px;padding:14px;position:relative;transition:.25s}.card:hover{transform:translateY(-8px);background:rgba(255,255,255,.10)}.card img{width:100%;aspect-ratio:1/1;border-radius:19px;object-fit:cover;margin-bottom:12px}.card h3{font-size:16px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.card p{color:var(--muted);font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.play-float{position:absolute;right:22px;bottom:92px;width:48px;height:48px;border-radius:50%;background:var(--pink);color:white;border:0;font-size:18px;cursor:pointer;opacity:0;transition:.2s}.card:hover .play-float{opacity:1}.actions{display:flex;gap:8px;margin-top:12px}.actions button{background:#242633;border:0;color:white;border-radius:12px;padding:9px 12px;cursor:pointer}.actions button.liked{background:var(--pink)}
.player{grid-column:1/3;background:rgba(10,10,14,.92);border-top:1px solid rgba(255,255,255,.08);backdrop-filter:blur(22px);display:grid;grid-template-columns:330px 1fr 240px;align-items:center;padding:0 26px}.now{display:flex;gap:15px;align-items:center}.now img{width:68px;height:68px;border-radius:16px;object-fit:cover}.now h4{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:210px}.now p{color:var(--muted);font-size:12px}.controls{text-align:center}.buttons{display:flex;justify-content:center;align-items:center;gap:22px;margin-bottom:10px}.round{width:54px;height:54px;border-radius:50%;border:0;background:white;color:#111;font-size:22px;font-weight:900;cursor:pointer}.ctrl{background:transparent;border:0;color:white;font-size:20px;cursor:pointer}.bar{height:5px;background:#2d2d35;border-radius:999px;overflow:hidden;width:75%;margin:auto;cursor:pointer}.fill{height:100%;width:0%;background:var(--pink)}.volume{text-align:right;color:#ccc}
.mobilebar{display:none}
@media(max-width:850px){
body{overflow:auto}.app{display:block;height:auto;min-height:100vh;padding-bottom:160px}.sidebar{display:none}.main{padding:16px 14px 145px}.top{display:block}.profile{display:none}.search{max-width:none;display:flex;margin-bottom:14px}.search button{padding:0 16px}.hero{display:block;text-align:left;min-height:auto;padding:20px;border-radius:30px}.hero h1{font-size:36px;letter-spacing:-1px}.hero-cover{width:100%;height:auto;aspect-ratio:1/1;margin-top:20px;border-radius:28px}.grid{grid-template-columns:1fr;gap:12px}.card{display:grid;grid-template-columns:78px 1fr;gap:13px;align-items:center}.card img{margin:0}.play-float{opacity:1;right:14px;bottom:14px;width:38px;height:38px}.player{position:fixed;left:10px;right:10px;bottom:82px;height:78px;grid-template-columns:1fr auto;border-radius:24px;padding:10px 14px;z-index:20}.now img{width:56px;height:56px}.controls .bar,.volume,.ctrl{display:none}.round{width:48px;height:48px}.mobilebar{display:grid;grid-template-columns:repeat(5,1fr);position:fixed;left:0;right:0;bottom:0;height:76px;background:rgba(8,8,10,.96);backdrop-filter:blur(20px);z-index:30}.mobilebar a{text-decoration:none;color:#ddd;display:flex;flex-direction:column;align-items:center;justify-content:center;font-size:11px}.mobilebar span{font-size:22px;margin-bottom:3px}}
</style>
<script>
const songs = {{ songs|tojson }};
let current = 0;
let liked = JSON.parse(localStorage.getItem("ashplex_liked") || "[]");

function audioEl(){ return document.getElementById("audio"); }

function playSong(i){
  current=i;
  const s=songs[i];
  document.getElementById("pimg").src=s.cover;
  document.getElementById("ptitle").innerText=s.title;
  document.getElementById("partist").innerText=s.artist;
  const a=audioEl();
  a.src=s.audio;
  a.play();
  document.getElementById("mainBtn").innerText="Ⅱ";
}

function togglePlay(){
  const a=audioEl();
  if(!a.src){ playSong(current); return; }
  if(a.paused){ a.play(); document.getElementById("mainBtn").innerText="Ⅱ"; }
  else{ a.pause(); document.getElementById("mainBtn").innerText="▶"; }
}

function nextSong(){ current=(current+1)%songs.length; playSong(current); }
function prevSong(){ current=(current-1+songs.length)%songs.length; playSong(current); }

function updateProgress(){
  const a=audioEl();
  if(a.duration){ document.getElementById("fill").style.width=((a.currentTime/a.duration)*100)+"%"; }
}

function seekBar(e){
  const a=audioEl();
  if(!a.duration) return;
  const r=e.currentTarget.getBoundingClientRect();
  a.currentTime=((e.clientX-r.left)/r.width)*a.duration;
}

function likeSong(id, btn){
  if(liked.includes(id)){ liked = liked.filter(x=>x!==id); btn.classList.remove("liked"); btn.innerText="♡"; }
  else{ liked.push(id); btn.classList.add("liked"); btn.innerText="❤️"; }
  localStorage.setItem("ashplex_liked", JSON.stringify(liked));
}

function shareSong(title){
  if(navigator.share){navigator.share({title:title,text:"Listen on ASHPLEX",url:location.href});}
  else alert("Share ASHPLEX: "+location.href);
}

window.addEventListener("DOMContentLoaded", ()=>{
  audioEl().addEventListener("timeupdate", updateProgress);
  audioEl().addEventListener("ended", nextSong);
});
</script>
</head>
<body>
<div class="app">
  <aside class="sidebar">
    <div class="logo">ASH<span>PLEX</span></div>
    <nav class="nav">
      <a class="active" href="/">🏠 Home</a>
      <a href="#moods">🤖 Mood AI</a>
      <a href="#songs">🔍 Search Songs</a>
      <a href="#liked">❤️ Like</a>
      <a href="#premium">👑 Premium</a>
      <a href="#rewards">💰 Rewards</a>
    </nav>
    <div class="creator">Created by<br><b>Ashutosh Pandey</b></div>
  </aside>

  <main class="main">
    <div class="top">
      <form class="search">
        <input name="q" value="{{ q }}" placeholder="Search song or singer...">
        <button>Search</button>
      </form>
      <div class="profile">👑 Premium • ASHPLEX</div>
    </div>

    <section class="hero">
      <div>
        <div class="eyebrow">Search Based Music App</div>
        <h1>Search. Play.<br>Like. Share.</h1>
        <p>Search any available 90s Hindi song in ASHPLEX, play it inside the app, like it, and share it like a real music application.</p>
      </div>
      <img class="hero-cover" src="{{ songs[0].cover }}">
    </section>

    <section class="section" id="moods">
      <div class="section-head"><h2>🤖 Mood Suggestions</h2><span>Quick filter</span></div>
      <div class="moods">
        {% for m in moods %}
        <a class="{{ 'active' if mood==m.id else '' }}" href="/?mood={{m.id}}">{{m.icon}} {{m.name}}</a>
        {% endfor %}
      </div>
    </section>

    <section class="section" id="songs">
      <div class="section-head"><h2>🎵 Search Results</h2><span>{{ songs|length }} tracks</span></div>
      <div class="grid">
        {% for s in songs %}
        <div class="card">
          <img src="{{s.cover}}">
          <button class="play-float" onclick="playSong({{loop.index0}})">▶</button>
          <div>
            <h3>{{s.title}}</h3>
            <p>{{s.artist}}</p>
            <div class="actions">
              <button onclick="likeSong({{s.id}}, this)">♡</button>
              <button onclick="shareSong('{{s.title}}')">📤</button>
              <button onclick="playSong({{loop.index0}})">▶</button>
            </div>
          </div>
        </div>
        {% endfor %}
      </div>
    </section>

    <div class="section" id="premium">
      <div class="section-head"><h2>👑 Premium</h2><span>Future feature</span></div>
      <div style="background:rgba(255,255,255,.07);border-radius:24px;padding:20px;color:#ddd">Premium users get ad-free ASHPLEX, special themes and reward boosters.</div>
    </div>
  </main>

  <footer class="player">
    <div class="now">
      <img id="pimg" src="{{songs[0].cover}}">
      <div><h4 id="ptitle">{{songs[0].title}}</h4><p id="partist">{{songs[0].artist}}</p></div>
    </div>
    <div class="controls">
      <div class="buttons"><button class="ctrl" onclick="prevSong()">⏮</button><button id="mainBtn" class="round" onclick="togglePlay()">▶</button><button class="ctrl" onclick="nextSong()">⏭</button></div>
      <div class="bar" onclick="seekBar(event)"><div id="fill" class="fill"></div></div>
    </div>
    <div class="volume">🔊 In-app Player</div>
  </footer>
  <audio id="audio"></audio>

  <nav class="mobilebar">
    <a href="/"><span>🏠</span>Home</a>
    <a href="#moods"><span>🤖</span>Mood</a>
    <a href="#songs"><span>🔍</span>Search</a>
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
    mood = request.args.get("mood","all")
    songs = filter_songs(q, mood)
    moods = [
        {"id":"all","name":"All","icon":"🎧"},
        {"id":"romantic","name":"Romantic","icon":"❤️"},
        {"id":"sad","name":"Sad","icon":"💔"},
        {"id":"happy","name":"Happy","icon":"😊"},
        {"id":"relax","name":"Relax","icon":"🌙"},
        {"id":"party","name":"Party","icon":"💃"},
    ]
    return render_template_string(HTML, songs=songs, moods=moods, mood=mood, q=q)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

from flask import Flask, render_template_string
import requests

app = Flask(__name__)

# =========================================
# JIOSAAVN API SONG FETCH
# =========================================

def get_songs():

    url = "https://saavn.dev/api/search/songs?query=90s%20hindi"

    response = requests.get(url)

    data = response.json()

    return data["data"]["results"][:12]

# =========================================
# HTML
# =========================================

HTML = """

<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>ASHPLEX</title>

<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">

<style>

*{
margin:0;
padding:0;
box-sizing:border-box;
font-family:'Poppins',sans-serif;
}

body{
background:#0b0b0f;
color:white;
overflow-x:hidden;
}

/* ======================= */
/* APP */
/* ======================= */

.app{
display:flex;
min-height:100vh;
}

/* ======================= */
/* SIDEBAR */
/* ======================= */

.sidebar{

width:250px;
background:#111217;

padding:30px 20px;

position:fixed;
top:0;
left:0;
bottom:0;

border-right:1px solid rgba(255,255,255,0.05);
}

.logo{

font-size:38px;
font-weight:800;

color:#1db954;

margin-bottom:45px;
}

.menu{

display:flex;
flex-direction:column;
gap:14px;
}

.menu a{

text-decoration:none;
color:#bbb;

padding:15px 18px;

border-radius:16px;

transition:0.3s;
font-weight:500;
}

.menu a:hover{

background:#1b1d24;
color:white;
}

.active{

background:#1db954;
color:white !important;
}

/* ======================= */
/* MAIN */
/* ======================= */

.main{

margin-left:250px;

flex:1;

padding:30px;
padding-bottom:140px;
}

/* ======================= */
/* SEARCH */
/* ======================= */

.top{

display:flex;
justify-content:space-between;
align-items:center;

margin-bottom:30px;
}

.search{
width:450px;
}

.search input{

width:100%;

padding:18px 22px;

border:none;
outline:none;

background:#1a1c22;

border-radius:18px;

color:white;

font-size:15px;
}

/* ======================= */
/* HERO */
/* ======================= */

.hero{

height:320px;

border-radius:32px;

padding:40px;

display:flex;
justify-content:space-between;
align-items:center;

background:
linear-gradient(
135deg,
#1db954,
#121212
);

overflow:hidden;

margin-bottom:40px;
}

.hero h1{

font-size:70px;
line-height:1;
margin-bottom:18px;
}

.hero p{

font-size:18px;
color:#ddd;

max-width:580px;
line-height:1.6;
}

.hero-buttons{

margin-top:28px;

display:flex;
gap:15px;
}

.btn{

padding:15px 28px;

border:none;

border-radius:40px;

font-size:15px;
font-weight:600;

cursor:pointer;
}

.play{
background:white;
color:black;
}

.explore{
background:rgba(255,255,255,0.15);
color:white;
}

.hero img{

width:270px;
height:270px;

object-fit:cover;

border-radius:26px;

box-shadow:0 20px 50px rgba(0,0,0,0.5);
}

/* ======================= */
/* SECTION */
/* ======================= */

.section{
margin-top:20px;
}

.section-title{

display:flex;
justify-content:space-between;
align-items:center;

margin-bottom:22px;
}

.section-title h2{
font-size:34px;
}

/* ======================= */
/* GRID */
/* ======================= */

.grid{

display:grid;

grid-template-columns:
repeat(auto-fill,minmax(220px,1fr));

gap:24px;
}

/* ======================= */
/* CARD */
/* ======================= */

.card{

background:#181a20;

padding:16px;

border-radius:22px;

transition:0.3s;

position:relative;
}

.card:hover{

transform:translateY(-8px);

background:#22252e;
}

.card img{

width:100%;
aspect-ratio:1/1;

border-radius:18px;

object-fit:cover;

margin-bottom:14px;
}

.card h3{

font-size:18px;
margin-bottom:4px;
}

.card p{

font-size:13px;
color:#aaa;
}

.play-btn{

position:absolute;

right:20px;
bottom:95px;

width:58px;
height:58px;

border-radius:50%;

background:#1db954;

display:flex;
align-items:center;
justify-content:center;

font-size:24px;

opacity:0;

transform:translateY(12px);

transition:0.3s;
}

.card:hover .play-btn{

opacity:1;
transform:translateY(0);
}

.actions{

display:flex;
gap:10px;

margin-top:14px;
}

.actions button{

border:none;

background:#262932;

color:white;

padding:10px 14px;

border-radius:12px;

cursor:pointer;
}

/* ======================= */
/* PLAYER */
/* ======================= */

.player{

position:fixed;

bottom:0;
left:250px;
right:0;

height:95px;

background:#111217;

border-top:1px solid rgba(255,255,255,0.05);

display:grid;

grid-template-columns:300px 1fr 220px;

align-items:center;

padding:0 25px;

z-index:999;
}

.now{

display:flex;
align-items:center;
gap:15px;
}

.now img{

width:65px;
height:65px;

border-radius:14px;
}

.song-name{

font-size:16px;
font-weight:600;
}

.artist{

font-size:13px;
color:#aaa;
}

.center{

display:flex;
flex-direction:column;
align-items:center;
gap:10px;
}

.controls{

display:flex;
align-items:center;
gap:22px;

font-size:22px;
}

.big{

width:56px;
height:56px;

border-radius:50%;

background:white;
color:black;

display:flex;
align-items:center;
justify-content:center;

font-size:24px;
}

.bar{

width:70%;
height:5px;

background:#2f3138;

border-radius:20px;

overflow:hidden;
}

.bar div{

width:45%;
height:100%;

background:#1db954;
}

/* ======================= */
/* MOBILE */
/* ======================= */

.mobile-nav{
display:none;
}

@media(max-width:850px){

.sidebar{
display:none;
}

.main{

margin-left:0;

padding:18px;
padding-bottom:180px;
}

.top{
display:block;
}

.search{

width:100%;
margin-bottom:20px;
}

.hero{

height:auto;

flex-direction:column;
text-align:center;

padding:25px;
}

.hero h1{
font-size:48px;
}

.hero img{

width:100%;
max-width:280px;
height:auto;

margin-top:25px;
}

.grid{
grid-template-columns:1fr;
}

.player{

left:10px;
right:10px;
bottom:82px;

height:82px;

border-radius:22px;

grid-template-columns:1fr auto;

padding:12px 16px;
}

.center .bar{
display:none;
}

.controls{
gap:14px;
font-size:18px;
}

.big{
width:48px;
height:48px;
}

.mobile-nav{

display:grid;

grid-template-columns:repeat(5,1fr);

position:fixed;

bottom:0;
left:0;
right:0;

height:75px;

background:#111217;

border-top:1px solid rgba(255,255,255,0.05);
}

.mobile-nav a{

display:flex;
flex-direction:column;

justify-content:center;
align-items:center;

color:white;

text-decoration:none;

font-size:12px;
}

}

/* ======================= */

</style>

</head>

<body>

<div class="app">

<!-- SIDEBAR -->

<div class="sidebar">

<div class="logo">
ASHPLEX
</div>

<div class="menu">

<a class="active" href="#">🏠 Home</a>
<a href="#">🔍 Search</a>
<a href="#">🎵 Library</a>
<a href="#">❤️ Liked</a>
<a href="#">👑 Premium</a>
<a href="#">💰 Rewards</a>

</div>

</div>

<!-- MAIN -->

<div class="main">

<!-- SEARCH -->

<div class="top">

<div class="search">

<input type="text"
placeholder="Search 90s Hindi Songs...">

</div>

</div>

<!-- HERO -->

<div class="hero">

<div>

<h1>
Your Mood.
Your Music.
Your World.
</h1>

<p>

AI-powered Hindi music platform inspired by premium music streaming apps.
Created by Ashutosh Pandey.

</p>

<div class="hero-buttons">

<button class="btn play">
▶ Play
</button>

<button class="btn explore">
❤️ Explore
</button>

</div>

</div>

<img src="https://c.saavncdn.com/editorial/logo/JioSaavn_20211117134141_500x500.jpg">

</div>

<!-- PLAYLIST -->

<div class="section">

<div class="section-title">

<h2>🔥 Trending 90s</h2>

</div>

<div class="grid">

{% for song in songs %}

<div class="card">

<img src="{{ song.image[2].url }}">

<div class="play-btn">
▶
</div>

<h3>{{ song.name }}</h3>

<p>{{ song.primaryArtists }}</p>

<div class="actions">

<button>❤️</button>
<button>📤</button>
<button>➕</button>

</div>

</div>

{% endfor %}

</div>

</div>

</div>

<!-- PLAYER -->

<div class="player">

<div class="now">

<img src="{{ songs[0].image[2].url }}">

<div>

<div class="song-name">
{{ songs[0].name }}
</div>

<div class="artist">
{{ songs[0].primaryArtists }}
</div>

</div>

</div>

<div class="center">

<div class="controls">

⏮

<div class="big">
❚❚
</div>

⏭

</div>

<div class="bar">
<div></div>
</div>

</div>

<div>

🔊 Volume

</div>

</div>

<!-- MOBILE NAV -->

<div class="mobile-nav">

<a href="#">🏠<br>Home</a>

<a href="#">🔍<br>Search</a>

<a href="#">🎵<br>Library</a>

<a href="#">👑<br>Premium</a>

<a href="#">➕<br>Create</a>

</div>

</div>

</body>
</html>

"""

# =========================================
# ROUTE
# =========================================

@app.route("/")
def home():

    songs = get_songs()

    return render_template_string(HTML, songs=songs)

# =========================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

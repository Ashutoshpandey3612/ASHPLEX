<!-- ========================================= -->
<!-- 🔥 ASHPLEX PREMIUM PROFESSIONAL UI -->
<!-- Spotify + Apple Music Inspired -->
<!-- ========================================= -->

<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>ASHPLEX</title>

<link rel="preconnect" href="https://fonts.googleapis.com">

<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">

<style>

*{
margin:0;
padding:0;
box-sizing:border-box;
font-family:'Poppins',sans-serif;
}

body{

background:
radial-gradient(circle at top left,#4d1220 0%,transparent 30%),
radial-gradient(circle at top right,#102040 0%,transparent 30%),
#050505;

color:white;
overflow:hidden;
height:100vh;
}

/* ========================= */
/* APP LAYOUT */
/* ========================= */

.app{

display:grid;
grid-template-columns:260px 1fr;
height:100vh;
}

/* ========================= */
/* SIDEBAR */
/* ========================= */

.sidebar{

background:rgba(255,255,255,0.04);

backdrop-filter:blur(20px);

border-right:1px solid rgba(255,255,255,0.05);

padding:30px 20px;
}

.logo{

font-size:34px;
font-weight:800;

margin-bottom:40px;

display:flex;
align-items:center;
gap:12px;
}

.logo span{

color:#ff004c;
}

.menu{

display:flex;
flex-direction:column;
gap:14px;
}

.menu a{

text-decoration:none;
color:#ccc;

padding:16px;
border-radius:16px;

transition:0.3s;

font-weight:500;
}

.menu a:hover{

background:rgba(255,255,255,0.08);

color:white;
transform:translateX(5px);
}

.menu .active{

background:#ff004c;
color:white;
box-shadow:0 10px 30px rgba(255,0,76,0.4);
}

/* ========================= */
/* MAIN */
/* ========================= */

.main{

padding:30px;
overflow-y:auto;
}

/* ========================= */
/* TOPBAR */
/* ========================= */

.topbar{

display:flex;
justify-content:space-between;
align-items:center;

margin-bottom:30px;
}

.search{

width:420px;
}

.search input{

width:100%;
padding:18px 24px;

border:none;
outline:none;

border-radius:20px;

background:rgba(255,255,255,0.08);

color:white;

font-size:15px;
}

.profile{

display:flex;
align-items:center;
gap:15px;
}

.profile img{

width:50px;
height:50px;
border-radius:50%;
}

/* ========================= */
/* HERO */
/* ========================= */

.hero{

height:340px;

border-radius:35px;

padding:35px;

display:flex;
align-items:center;
justify-content:space-between;

background:

linear-gradient(
135deg,
rgba(255,255,255,0.08),
rgba(255,255,255,0.03)
);

backdrop-filter:blur(25px);

overflow:hidden;

position:relative;
}

.hero::before{

content:"";

position:absolute;

width:500px;
height:500px;

background:#ff004c;

filter:blur(160px);

opacity:0.25;

right:-100px;
top:-150px;
}

.hero-left{

z-index:2;
max-width:600px;
}

.hero h1{

font-size:68px;
line-height:1;

margin-bottom:20px;
}

.hero p{

color:#ccc;
font-size:18px;

line-height:1.7;
}

.hero-buttons{

margin-top:30px;

display:flex;
gap:15px;
}

.btn{

padding:16px 28px;

border:none;

border-radius:40px;

cursor:pointer;

font-weight:600;

transition:0.3s;
}

.play{

background:#ff004c;
color:white;
}

.play:hover{

transform:scale(1.05);
box-shadow:0 15px 40px rgba(255,0,76,0.5);
}

.secondary{

background:rgba(255,255,255,0.08);
color:white;
}

.hero-cover{

width:320px;
height:320px;

border-radius:35px;

object-fit:cover;

box-shadow:0 25px 70px rgba(0,0,0,0.6);

z-index:2;
}

/* ========================= */
/* SECTION */
/* ========================= */

.section{

margin-top:40px;
}

.section-title{

display:flex;
justify-content:space-between;
align-items:center;

margin-bottom:22px;
}

.section-title h2{

font-size:32px;
}

/* ========================= */
/* SONG GRID */
/* ========================= */

.grid{

display:grid;

grid-template-columns:
repeat(auto-fill,minmax(220px,1fr));

gap:24px;
}

.card{

background:
linear-gradient(
180deg,
rgba(255,255,255,0.07),
rgba(255,255,255,0.03)
);

padding:18px;

border-radius:28px;

transition:0.4s;

position:relative;

overflow:hidden;
}

.card:hover{

transform:translateY(-10px);

box-shadow:
0 20px 60px rgba(0,0,0,0.5);
}

.card img{

width:100%;
aspect-ratio:1/1;

object-fit:cover;

border-radius:22px;

margin-bottom:18px;
}

.card h3{

font-size:18px;
margin-bottom:5px;
}

.card p{

font-size:13px;
color:#bbb;
}

.hover-play{

position:absolute;

bottom:105px;
right:25px;

width:60px;
height:60px;

background:#ff004c;

border-radius:50%;

display:flex;
align-items:center;
justify-content:center;

font-size:22px;

opacity:0;

transform:translateY(15px);

transition:0.3s;
}

.card:hover .hover-play{

opacity:1;
transform:translateY(0);
}

.card-actions{

margin-top:15px;

display:flex;
gap:10px;
}

.small-btn{

padding:10px 14px;

border:none;

border-radius:14px;

background:rgba(255,255,255,0.08);

color:white;

cursor:pointer;
}

/* ========================= */
/* PLAYER */
/* ========================= */

.player{

position:fixed;

bottom:0;
left:260px;
right:0;

height:95px;

background:rgba(0,0,0,0.7);

backdrop-filter:blur(20px);

border-top:1px solid rgba(255,255,255,0.05);

display:grid;

grid-template-columns:320px 1fr 220px;

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

border-radius:16px;
}

.controls{

display:flex;
flex-direction:column;
align-items:center;
gap:10px;
}

.buttons{

display:flex;
align-items:center;
gap:20px;
}

.big-play{

width:58px;
height:58px;

border-radius:50%;

background:white;
color:black;

display:flex;
align-items:center;
justify-content:center;

font-size:24px;

font-weight:bold;
}

.progress{

width:100%;
height:5px;

background:#333;

border-radius:20px;

overflow:hidden;
}

.progress div{

width:45%;
height:100%;

background:#ff004c;
}

/* ========================= */
/* MOBILE UI */
/* ========================= */

.mobile-nav{

display:none;
}

@media(max-width:850px){

.app{

display:block;
}

.sidebar{

display:none;
}

.main{

padding:18px 18px 130px;
}

.topbar{

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

font-size:42px;
}

.hero-cover{

width:100%;
max-width:320px;
height:auto;
margin-top:25px;
}

.grid{

grid-template-columns:1fr;
}

.player{

left:10px;
right:10px;
bottom:80px;

height:80px;

border-radius:24px;

grid-template-columns:1fr auto;

padding:12px 18px;
}

.controls .progress{

display:none;
}

.mobile-nav{

display:grid;

grid-template-columns:repeat(5,1fr);

position:fixed;

bottom:0;
left:0;
right:0;

height:75px;

background:rgba(0,0,0,0.92);

backdrop-filter:blur(20px);

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

</style>
</head>

<body>

<div class="app">

<!-- ========================= -->
<!-- SIDEBAR -->
<!-- ========================= -->

<div class="sidebar">

<div class="logo">
🎧 <span>ASHPLEX</span>
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

<!-- ========================= -->
<!-- MAIN -->
<!-- ========================= -->

<div class="main">

<div class="topbar">

<div class="search">

<input type="text"
placeholder="Search 90s Hindi songs...">

</div>

<div class="profile">

👑 Premium User

<img src="https://i.pravatar.cc/100">

</div>

</div>

<!-- HERO -->

<div class="hero">

<div class="hero-left">

<h1>
Your Mood.
Your Music.
Your World.
</h1>

<p>

AI-powered music recommendation platform
focused on legendary 90s Hindi singers.

Created by Ashutosh Pandey.

</p>

<div class="hero-buttons">

<button class="btn play">
▶ Play Now
</button>

<button class="btn secondary">
❤️ Explore
</button>

</div>

</div>

<img class="hero-cover"
src="https://i.imgur.com/FY6hZ4G.jpeg">

</div>

<!-- TRENDING -->

<div class="section">

<div class="section-title">

<h2>🔥 Trending 90s</h2>

<span>Show all</span>

</div>

<div class="grid">

<!-- CARD -->

<div class="card">

<img src="https://i.imgur.com/FY6hZ4G.jpeg">

<div class="hover-play">
▶
</div>

<h3>Pehla Nasha</h3>

<p>Udit Narayan</p>

<div class="card-actions">

<button class="small-btn">
❤️
</button>

<button class="small-btn">
📤
</button>

<button class="small-btn">
➕
</button>

</div>

</div>

<!-- CARD -->

<div class="card">

<img src="https://i.imgur.com/q6P4D5N.jpeg">

<div class="hover-play">
▶
</div>

<h3>Tujhe Dekha To</h3>

<p>Kumar Sanu</p>

<div class="card-actions">

<button class="small-btn">
❤️
</button>

<button class="small-btn">
📤
</button>

<button class="small-btn">
➕
</button>

</div>

</div>

<!-- CARD -->

<div class="card">

<img src="https://i.imgur.com/sx6QX7T.jpeg">

<div class="hover-play">
▶
</div>

<h3>Dheere Dheere</h3>

<p>Alka Yagnik</p>

<div class="card-actions">

<button class="small-btn">
❤️
</button>

<button class="small-btn">
📤
</button>

<button class="small-btn">
➕
</button>

</div>

</div>

</div>

</div>

</div>

<!-- ========================= -->
<!-- PLAYER -->
<!-- ========================= -->

<div class="player">

<div class="now">

<img src="https://i.imgur.com/FY6hZ4G.jpeg">

<div>

<h4>Pehla Nasha</h4>

<p>Udit Narayan</p>

</div>

</div>

<div class="controls">

<div class="buttons">

⏮

<div class="big-play">
❚❚
</div>

⏭

</div>

<div class="progress">
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

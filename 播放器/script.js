
let songData=[];


fetch('http://iibread.xyz/player/player.php?audio_id=all') // 替换为您的API端点
  .then(response => response.json())
  .then(data => {
    // 在这里处理返回的数据
    console.log('Success:', data);
    console.log('data.length',data.length);
    for (let i = 0; i < data.length; i++) {
      if (data[i].audio_date == getdate){
        songIndex = i;
      }
      songData[i]={name:data[i].audio_name,
                   artist:'AI speakers',
                   src:data[i].audio_content};
    };

    // 调用 loadSong() 来加载播放器的初始歌曲
    console.log('songIndex=',songIndex)
    loadSong(songIndex);
  })
  .catch(error => {
    console.error('Error:', error);

  });





// const songData = [
//   {
//     name: "NHK Easy News 07-10",
//     artist: "AI speakers",
//     src: "0710",
//   },
//   {
//     name: "NHK Easy News 07-11",
//     artist: "AI speakers",
//     src: "0711",
//   },
//   {
//     name: "NHK Easy News 07-12",
//     artist: "AI speakers",
//     src: "0712",
//   },
//   {
//     name: "Easter egg: Love belike fire",
//     artist: "Na Yi Nas",
//     src: "Love belike fire",
//   },
// ];

const container = document.querySelector(".container");
const songName = document.querySelector(".song-name");
const songArtist = document.querySelector(".song-artist");
const cover = document.querySelector(".cover");
const playPauseBtn = document.querySelector(".play-pause");
const prevBtn = document.querySelector(".prev-btn");
const nextBtn = document.querySelector(".next-btn");
const audio = document.querySelector(".audio");
const songTime = document.querySelector(".song-time");
const songProgress = document.querySelector(".song-progress");
const coverArtist = document.querySelector(".cover span:nth-child(1)");
const coverName = document.querySelector(".cover span:nth-child(2)");


const urlParams = new URLSearchParams(window.location.search);
const getdate = urlParams.get('date');
console.log('index_info',getdate);
let songIndex;


window.addEventListener("load", () => {
  loadSong(songIndex);
});

const loadSong = (index) => {
  console.log('在loadsong里收到的',songData);
  coverName.textContent = songData[index].name;
  coverArtist.textContent = songData[index].artist;
  songName.textContent = songData[index].name;
  songArtist.textContent = songData[index].artist;
  // audio.src = `music/${songData[index].src}.mp3`;
  //audio.src = `${songData[index].src}.mp3`;
  audio.src = songData[index].src;
};

const playSong = () => {
  container.classList.add("pause");
  cover.classList.add("rotate");
  playPauseBtn.firstElementChild.className = "fa-solid fa-pause";
  audio.play();
};

const pauseSong = () => {
  container.classList.remove("pause");
  cover.classList.remove("rotate");
  playPauseBtn.firstElementChild.className = "fa-solid fa-play";
  audio.pause();
};

playPauseBtn.addEventListener("click", () => {
  if (container.classList.contains("pause")) {
    pauseSong();
  } else {
    playSong();
  }
});

const prevSongPlay = () => {
  songIndex--;
  if (songIndex < 0) {
    songIndex = songData.length - 1;
  }

  loadSong(songIndex);
  playSong();
};

const nextSongPlay = () => {
  songIndex++;
  if (songIndex > songData.length - 1) {
    songIndex = 0;
  }

  loadSong(songIndex);
  playSong();
};

prevBtn.addEventListener("click", prevSongPlay);
nextBtn.addEventListener("click", nextSongPlay);

audio.addEventListener("timeupdate", (e) => {
  const currentTime = e.target.currentTime;
  const duration = e.target.duration;
  let currentTimeWidth = (currentTime / duration) * 100;
  songProgress.style.width = `${currentTimeWidth}%`;

  let songCurrentTime = document.querySelector(".time span:nth-child(1)");
  let songDuration = document.querySelector(".time span:nth-child(2)");

  audio.addEventListener("loadeddata", () => {
    let audioDuration = audio.duration;
    let totalMinutes = Math.floor(audioDuration / 60);
    let totalSeconds = Math.floor(audioDuration % 60);

    if (totalSeconds < 10) {
      totalSeconds = `0${totalSeconds}`;
    }

    songDuration.textContent = `${totalMinutes}:${totalSeconds}`;
  });

  let currentMinutes = Math.floor(currentTime / 60);
  let currentSeconds = Math.floor(currentTime % 60);

  if (currentSeconds < 10) {
    currentSeconds = `0${currentSeconds}`;
  }

  songCurrentTime.textContent = `${currentMinutes}:${currentSeconds}`;
});

songTime.addEventListener("click", (e) => {
  let progressWidth = songTime.clientWidth;
  let clickedOffsetX = e.offsetX;
  let songDuration = audio.duration;
  audio.currentTime = (clickedOffsetX / progressWidth) * songDuration;

  playSong();
});

audio.addEventListener("ended", nextSongPlay);

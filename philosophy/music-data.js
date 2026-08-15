/* ============================================================
   MUSIC JOURNAL — DATA FILE
   This is the only file you edit. The page builds itself from it.

   ADD an artist (goes straight to "Yet To Hear"):
       { name: "Deep Purple", genre: "60s Rock Gods" },

   MARK one as heard (moves it up to "Have Heard"):
       { name: "Deep Purple", genre: "60s Rock Gods", heard: true, days: 12 },

   A genre not listed in GENRE_ORDER still works — its card just
   appears at the end. Add it to GENRE_ORDER to place it deliberately.
   ============================================================ */

/* Hand-tracked totals. Artist count is computed automatically. */
const MUSIC_STATS = {
  albums:    556,
  playlists: 50,
  days: 556, 
};

/* Card order on the page. */
const GENRE_ORDER = [
  /* Rock */
  "60s Rock Gods",
  "70s Rock Gods",
  "80s Rock Gods",
  "90s Grunge",
  "90s Rock Gods",
  "21st Century Rock",
  "Solo Rock Projects",
  /* Metal */
  "70s Metal",
  "80s Metal",
  "American Thrash",
  "American Metal",
  "Solo Metal Projects",
  /* Soul & R&B */
  "Soul Legends",
  "Pop-Soul Legends",
  "Rhythm & Blues",
  "21st Century Pop-Soul",
  /* Hip-Hop */
  "Golden Era Heroes of Rap",
  "Classic Rap Icons",
  "Turn-of-Century Rap Legends",
  "Lyrical & Conscious Rap",
  "2010s Hip-Hop",
  "2020s Hip-Hop",
  "Rage & Trap",
  /* Elsewhere */
  "Reggae",
  "Instrumental Music",
  "Hawaiian Soul"
];

/* Every artist. Order here does not matter — cards sort alphabetically. */
const MUSIC_DATA = [

  /* --- 60s Rock Gods --- */
  { name: "Bob Dylan", genre: "60s Rock Gods" },
  { name: "Deep Purple", genre: "60s Rock Gods" },
  { name: "Jimi Hendrix", genre: "60s Rock Gods" },
  { name: "Led Zeppelin", genre: "60s Rock Gods", heard: true, days: 9 },
  { name: "Lynyrd Skynyrd", genre: "60s Rock Gods" },
  { name: "Neil Young", genre: "60s Rock Gods" },
  { name: "Pink Floyd", genre: "60s Rock Gods", heard: true, days: 17 },
  { name: "The Beatles", genre: "60s Rock Gods" },

  /* --- 80s Rock Gods --- */
  { name: "Bon Jovi", genre: "80s Rock Gods", heard: true, days: 19 },
  { name: "Guns N' Roses", genre: "80s Rock Gods" },
  { name: "Mötley Crüe", genre: "80s Rock Gods" },
  { name: "Van Halen", genre: "80s Rock Gods" },

  /* --- 70s Metal --- */
  { name: "Black Sabbath", genre: "70s Metal", heard: true, days: 21 },
  { name: "Judas Priest", genre: "70s Metal", heard: true, days: 20 },
  { name: "Motörhead", genre: "70s Metal", heard: true, days: 22 },

  /* --- 80s Metal --- */
  { name: "Armored Saint", genre: "80s Metal" },
  { name: "Dio", genre: "80s Metal" },
  { name: "Dokken", genre: "80s Metal" },
  { name: "Iron Maiden", genre: "80s Metal", heard: true, days: 19 },

  /* --- American Thrash --- */
  { name: "Anthrax", genre: "American Thrash", heard: true, days: 14 },
  { name: "Megadeth", genre: "American Thrash", heard: true, days: 18 },
  { name: "Metallica", genre: "American Thrash", heard: true, days: 14 },
  { name: "Slayer", genre: "American Thrash", heard: true, days: 14 },

  /* --- 90s Rock Gods --- */
  { name: "Pantera", genre: "90s Rock Gods", heard: true, days: 9 },
  { name: "Tool", genre: "90s Rock Gods" },

  /* --- 90s Grunge --- */
  { name: "Nirvana", genre: "90s Grunge", heard: true, days: 3 },
  { name: "Alice In Chains", genre: "90s Grunge", heard: true, days: 7 },
  { name: "Pearl Jam", genre: "90s Grunge" },

  /* --- Pop-Soul Legends --- */
  { name: "George Michael", genre: "Pop-Soul Legends" },
  { name: "Michael Jackson", genre: "Pop-Soul Legends", heard: true, days: 13 },
  { name: "Prince", genre: "Pop-Soul Legends" },
  { name: "Wham!", genre: "Pop-Soul Legends" },

  /* --- Rhythm & Blues --- */
  { name: "Boyz II Men", genre: "Rhythm & Blues" },
  { name: "Brent Faiyaz", genre: "Rhythm & Blues" },
  { name: "Luther Vandross", genre: "Rhythm & Blues" },
  { name: "PARTYNEXTDOOR (PND)", genre: "Rhythm & Blues", heard: true, days: 10 },
  { name: "Tory Lanez", genre: "Rhythm & Blues" },
  { name: "Yebba", genre: "Rhythm & Blues" },

  /* --- Hawaiian Soul --- */
  { name: "Israel Kamakawiwoʻole", genre: "Hawaiian Soul" },

  /* --- Indie --- */
  { name: "Tame Impala", genre: "Indie" },

  /* --- 21st Century Pop-Soul --- */
  { name: "Bruno Mars", genre: "21st Century Pop-Soul" },
  { name: "Frank Ocean", genre: "21st Century Pop-Soul", heard: true, days: 5 },
  { name: "James Fauntleroy", genre: "21st Century Pop-Soul", heard: true, days: 6 },
  { name: "Majid Jordan", genre: "21st Century Pop-Soul" },
  { name: "Pharrell Williams", genre: "21st Century Pop-Soul" },
  { name: "Sampha", genre: "21st Century Pop-Soul" },
  { name: "The Weeknd", genre: "21st Century Pop-Soul", heard: true, days: 8 },
  { name: "Usher", genre: "21st Century Pop-Soul" },

  /* --- Golden Era Heroes of Rap --- */
  { name: "2Pac", genre: "Golden Era Heroes of Rap", heard: true, days: 14 },
  { name: "A Tribe Called Quest", genre: "Golden Era Heroes of Rap" },
  { name: "Common", genre: "Golden Era Heroes of Rap" },
  { name: "Eric B.", genre: "Golden Era Heroes of Rap" },
  { name: "Outkast", genre: "Golden Era Heroes of Rap", heard: true, days: 6 },
  { name: "Rakim", genre: "Golden Era Heroes of Rap" },
  { name: "The Notorious B.I.G.", genre: "Golden Era Heroes of Rap", heard: true, days: 6 },

  /* --- Classic Rap Icons --- */
  { name: "DMX", genre: "Classic Rap Icons" },
  { name: "Dr. Dre", genre: "Classic Rap Icons", heard: true, days: 4 },
  { name: "Eazy-E", genre: "Classic Rap Icons" },
  { name: "Ice Cube", genre: "Classic Rap Icons" },
  { name: "JAY-Z", genre: "Classic Rap Icons", heard: true, days: 16 },
  { name: "N.W.A.", genre: "Classic Rap Icons" },
  { name: "Nas", genre: "Classic Rap Icons", heard: true, days: 20 },
  { name: "Wu-Tang Clan", genre: "Classic Rap Icons" },

  /* --- Turn-of-Century Rap Legends --- */
  { name: "50 Cent", genre: "Turn-of-Century Rap Legends", heard: true, days: 6 },
  { name: "Clipse", genre: "Turn-of-Century Rap Legends" },
  { name: "D12", genre: "Turn-of-Century Rap Legends" },
  { name: "Eminem", genre: "Turn-of-Century Rap Legends", heard: true, days: 13 },
  { name: "Kanye West", genre: "Turn-of-Century Rap Legends", heard: true, days: 21 },
  { name: "Lil Wayne", genre: "Turn-of-Century Rap Legends", heard: true, days: 23 },

  /* --- Lyrical & Conscious Rap --- */
  { name: "Ab-Soul", genre: "Lyrical & Conscious Rap" },
  { name: "Denzel Curry", genre: "Lyrical & Conscious Rap" },
  { name: "Isaiah Rashad", genre: "Lyrical & Conscious Rap" },
  { name: "J. Cole", genre: "Lyrical & Conscious Rap", heard: true, days: 16 },
  { name: "JID", genre: "Lyrical & Conscious Rap" },
  { name: "Kendrick Lamar", genre: "Lyrical & Conscious Rap", heard: true, days: 10 },
  { name: "MF DOOM", genre: "Lyrical & Conscious Rap" },
  { name: "Pusha T", genre: "Lyrical & Conscious Rap", heard: true, days: 8 },
  { name: "Vince Staples", genre: "Lyrical & Conscious Rap" },
  { name: "A$AP Rocky", genre: "Lyrical & Conscious Rap" },
  { name: "JPEGMAFIA", genre: "Lyrical & Conscious Rap" },


  /* --- 2020s Hip-Hop --- */
  { name: "21 Savage", genre: "2020s Hip-Hop", heard: true, days: 11 },
  { name: "BigXthaPlug", genre: "2020s Hip-Hop" },
  { name: "King Von", genre: "2020s Hip-Hop" },
  { name: "Pop Smoke", genre: "2020s Hip-Hop", heard: true, days: 5 },
  { name: "Ty Dolla $ign", genre: "2020s Hip-Hop" },
  { name: "Baby Keem", genre: "2020s Hip-Hop", heard: true, days: 5 },
  { name: "Don Toliver", genre: "2020s Hip-Hop", heard: true, days: 7 },
  { name: "Travis Scott", genre: "2020s Hip-Hop", heard: true, days: 9 },
  { name: "Tyler, the Creator", genre: "2020s Hip-Hop", heard: true, days: 9 },
  { name: "Yeat", genre: "2020s Hip-Hop", heard: true, days: 12 },


  /* --- Rage & Trap --- */
  { name: "EsDeeKid", genre: "Rage & Trap", heard: true, days: 2 },
  { name: "Ken Carson", genre: "Rage & Trap", heard: true, days: 1 },
  { name: "North West", genre: "Rage & Trap", heard: true, days: 1 },
  { name: "Playboi Carti", genre: "Rage & Trap", heard: true, days: 6 },

  /* --- 70s Rock Gods --- */
  { name: "AC/DC", genre: "70s Rock Gods" },
  { name: "Aerosmith", genre: "70s Rock Gods", heard: true, days: 16 },
  { name: "Boston", genre: "70s Rock Gods" },
  { name: "Journey", genre: "70s Rock Gods" },
  { name: "Queen", genre: "70s Rock Gods" },

  /* --- 21st Century Rock --- */
  { name: "Creed", genre: "21st Century Rock" },
  { name: "Foo Fighters", genre: "21st Century Rock" },
  { name: "The HU", genre: "21st Century Rock" },
  { name: "Yungblud", genre: "21st Century Rock" },

  /* --- Reggae --- */
  { name: "Bob Marley & The Wailers", genre: "Reggae" },
  { name: "Damian Marley", genre: "Reggae" },

  /* --- Solo Metal Projects --- */
  { name: "Adrian Smith", genre: "Solo Metal Projects" },
  { name: "Blaze Bayley", genre: "Solo Metal Projects" },
  { name: "Bruce Dickinson", genre: "Solo Metal Projects" },
  { name: "Chris Poland", genre: "Solo Metal Projects" },
  { name: "Jerry Cantrell", genre: "Solo Metal Projects" },
  { name: "Kerry King", genre: "Solo Metal Projects" },
  { name: "Kiko Loureiro", genre: "Solo Metal Projects" },
  { name: "Marty Friedman", genre: "Solo Metal Projects" },
  { name: "Ozzy Osbourne", genre: "Solo Metal Projects" },
  { name: "Steve Harris", genre: "Solo Metal Projects" },
  { name: "Tony Iommi", genre: "Solo Metal Projects" },

  /* --- Solo Rock Projects --- */
  { name: "David Gilmour", genre: "Solo Rock Projects" },
  { name: "Phil Collins", genre: "Solo Rock Projects" },
  { name: "Richard Wright", genre: "Solo Rock Projects" },
  { name: "Roger Waters", genre: "Solo Rock Projects" },
  { name: "Steve Overland", genre: "Solo Rock Projects" },
  { name: "Syd Barrett", genre: "Solo Rock Projects" },

  /* --- Instrumental Music --- */
  { name: "Hans Zimmer", genre: "Instrumental Music" },
  { name: "John Williams", genre: "Instrumental Music" },
  { name: "Kenny G", genre: "Instrumental Music" },
  { name: "Ludwig Göransson", genre: "Instrumental Music" },

  /* --- Soul Legends --- */
  { name: "Charlie Wilson", genre: "Soul Legends", heard: true, days: 9 },
  { name: "Erykah Badu", genre: "Soul Legends" },
  { name: "Marvin Gaye", genre: "Soul Legends" },
  { name: "Otis Redding", genre: "Soul Legends" },
  { name: "Ray Charles", genre: "Soul Legends" },
  { name: "Stevie Wonder", genre: "Soul Legends" },
  { name: "The Gap Band", genre: "Soul Legends" },

  /* --- 2010s Hip-Hop --- */
  { name: "Fetty Wap", genre: "2010s Hip-Hop" },
  { name: "Kid Cudi", genre: "2010s Hip-Hop" },
  { name: "Lil Uzi Vert", genre: "2010s Hip-Hop" },
  { name: "Odd Future", genre: "2010s Hip-Hop" },
  { name: "Offset", genre: "2010s Hip-Hop" },
  { name: "Quavo", genre: "2010s Hip-Hop" },
  { name: "Skepta", genre: "2010s Hip-Hop" },
  { name: "Takeoff", genre: "2010s Hip-Hop" },
  { name: "Drake", genre: "2010s Hip-Hop", heard: true, days: 19 },
  { name: "Future", genre: "2010s Hip-Hop", heard: true, days: 24 },
  { name: "Metro Boomin", genre: "2010s Hip-Hop", heard: true, days: 10 },
  { name: "Migos", genre: "2010s Hip-Hop" },
  { name: "Young Thug", genre: "2010s Hip-Hop" },
];

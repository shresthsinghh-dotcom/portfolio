const images = document.querySelectorAll('.carousel-img');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');

let currentIndex = 0;

// Hide all images except the first
function updateCarousel() {
  images.forEach((img, index) => {
    img.style.display = (index === currentIndex) ? 'block' : 'none';
  });
}

nextBtn.addEventListener('click', () => {
  currentIndex = (currentIndex + 1) % images.length;
  updateCarousel();
});

prevBtn.addEventListener('click', () => {
  currentIndex = (currentIndex - 1 + images.length) % images.length;
  updateCarousel();
});

// Initialize
updateCarousel();
// Fade-in on scroll
function handleScrollFade() {
  const faders = document.querySelectorAll('.fade-in');
  const windowBottom = window.innerHeight + window.scrollY;

  faders.forEach(fader => {
    if (windowBottom > fader.offsetTop + 100) {
      fader.classList.add('visible');
    }
  });
}

window.addEventListener('scroll', handleScrollFade);

const backToTopBtn = document.getElementById("backToTop");

window.addEventListener("scroll", () => {
  if (window.scrollY > 400) {
    backToTopBtn.classList.add("visible");
  } else {
    backToTopBtn.classList.remove("visible");
  }
});

backToTopBtn.addEventListener("click", () => {
  window.scrollTo({ top: 0, behavior: "smooth" });
});
const themeBtn = document.getElementById("themeToggle");

// Load saved theme from localStorage
if (localStorage.getItem("theme") === "dark") {
  document.body.classList.add("dark-mode");
  themeBtn.textContent = "Light Mode";
}

themeBtn.addEventListener("click", () => {
  document.body.classList.toggle("dark-mode");

  const isDark = document.body.classList.contains("dark-mode");
  themeBtn.textContent = isDark ? "Light Mode" : "Dark Mode";

  localStorage.setItem("theme", isDark ? "dark" : "light");
});

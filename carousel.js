// =========================
// Carousel with fade animation
// =========================

const images = document.querySelectorAll('.carousel-img');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
let currentIndex = 0;

function updateCarousel() {
  images.forEach((img, index) => {
    img.style.opacity = (index === currentIndex) ? '1' : '0';
    img.style.transform = (index === currentIndex) ? 'translateX(0)' : 'translateX(20px)';
    img.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    img.style.position = 'absolute';
  });
}

nextBtn && nextBtn.addEventListener('click', () => {
  currentIndex = (currentIndex + 1) % images.length;
  updateCarousel();
});

prevBtn && prevBtn.addEventListener('click', () => {
  currentIndex = (currentIndex - 1 + images.length) % images.length;
  updateCarousel();
});

updateCarousel();

// =========================
// IntersectionObserver for scroll fade-ins
// =========================

const observerOptions = {
  threshold: 0.1
};

const fadeObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      fadeObserver.unobserve(entry.target);
    }
  });
}, observerOptions);

document.querySelectorAll('.fade-in').forEach(el => {
  fadeObserver.observe(el);
});

// =========================
// Back to Top Button
// =========================

const backToTopBtn = document.getElementById("backToTop");

window.addEventListener("scroll", () => {
  backToTopBtn && backToTopBtn.classList.toggle("visible", window.scrollY > 400);
});

backToTopBtn && backToTopBtn.addEventListener("click", () => {
  window.scrollTo({ top: 0, behavior: "smooth" });
});

// =========================
// Theme Toggle
// =========================

const themeBtn = document.getElementById("themeToggle");

// Apply saved theme from localStorage
if (themeBtn && localStorage.getItem("theme") === "dark") {
  document.body.classList.add("dark-mode");
  themeBtn.textContent = "Light Mode";
}

themeBtn && themeBtn.addEventListener("click", () => {
  document.body.classList.toggle("dark-mode");
  const isDark = document.body.classList.contains("dark-mode");
  themeBtn.textContent = isDark ? "Light Mode" : "Dark Mode";
  localStorage.setItem("theme", isDark ? "dark" : "light");
});

// Add smooth transition for theme switching
document.body.style.transition = "background 0.4s ease, color 0.4s ease";

// =========================
// Optional: Smooth page anchor scroll
// Only if the target exists on this page
// =========================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    const targetId = this.getAttribute('href').substring(1);
    const targetEl = document.getElementById(targetId);

    if (targetEl) {
      e.preventDefault();
      targetEl.scrollIntoView({ behavior: 'smooth' });
    }
  });
});

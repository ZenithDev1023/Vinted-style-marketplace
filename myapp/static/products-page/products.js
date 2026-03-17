let current = 0;

// Automatically counts however many slides Django generates
const track = document.querySelector('.carousel-track');
const slides = document.querySelectorAll('.container');
const total = slides.length;

function updateCarousel() {
    if (!track) return;
    track.style.transform = `translateX(-${current * 100}%)`;
}

function next() {
    if (total === 0) return;
    current = (current + 1) % total;  // Loops back to start
    updateCarousel();
}

function prev() {
    if (total === 0) return;
    current = (current - 1 + total) % total;  // Loops back to end
    updateCarousel();
}


/* Open the side navigation */
function openNav() {
  document.getElementById("mySidenav").classList.add("open");
  document.getElementById("main").style.marginLeft = "250px";
}

/* Close the side navigation */
function closeNav() {
  document.getElementById("mySidenav").classList.remove("open");
  document.getElementById("main").style.marginLeft = "0";
}

document.getElementById("openNavBtn").addEventListener("click", openNav);
document.getElementById("closeNavBtn").addEventListener("click", closeNav);
let current = 0;

// Automatically counts however many slides Django generates
const track = document.querySelector('.carousel-track');
const slides = document.querySelectorAll('.container');
const total = slides.length;

function updateCarousel() {
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
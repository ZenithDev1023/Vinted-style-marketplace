let current = 0;
const itemsPerPage = 4;

// Automatically counts however many slides Django generates
const track = document.querySelector('.carousel-track');
const slides = document.querySelectorAll('.container');
const total = slides.length;

function updateCarousel() {
    if (!track) return;
    track.style.transform = `translateX(-${current * 25}%)`;
}

function next() {
    if (total === 0) return;
    
    if (current + itemsPerPage < total) {
        current += itemsPerPage;
    } else {
        current = 0; 
    }
    updateCarousel();
}

function prev() {
    if (total === 0) return;
    if (current - itemsPerPage >= 0) {
        current -= itemsPerPage;
    } else {
        current = Math.floor((total - 1) / itemsPerPage) * itemsPerPage;
    }
    updateCarousel();
}

function openNav() {
    document.getElementById("mySidenav").classList.add("open");
}

function closeNav() {
    document.getElementById("mySidenav").classList.remove("open");
}

document.getElementById("openNavBtn").addEventListener("click", openNav);
document.getElementById("closeNavBtn").addEventListener("click", closeNav);

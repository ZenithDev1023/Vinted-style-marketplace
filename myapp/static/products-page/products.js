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

// Filter functionality
// function shows all products by default
function filterSelection(c) {
    var x, i;
    x = document.getElementsByClassName("filterButtonContainer");
    if (c == "all") c = "";

    for (i = 0; i < x.length; i++) {
        removeClass(x[i], "show");
        // If the element's class name contains the filter value, add the "show" class (display it)
        if (x[i].className.indexOf(c) > -1) addClass(x[i], "show");
    }
}

  // Show filtered elements
function addClass(element, name) {
  var i, arr1, arr2;
  arr1 = element.className.split(" ");
  arr2 = name.split(" ");
  for (i = 0; i < arr2.length; i++) {
    if (arr1.indexOf(arr2[i]) === -1) {
      element.className += " " + arr2[i];
    }
  }
}

// Hide elements that are not selected
function removeClass(element, name) {
  var i, arr1, arr2;
  arr1 = element.className.split(" ");
  arr2 = name.split(" ");
  for (i = 0; i < arr2.length; i++) {
    while (arr1.indexOf(arr2[i]) > -1) {
      arr1.splice(arr1.indexOf(arr2[i]), 1);
    }
  }
  element.className = arr1.join(" ");
}

var btnContainer = document.getElementById("filterButtons");
var buttons = btnContainer.getElementsByClassName("filter-btn");
for (var i = 0; i < buttons.length; i++) {
  buttons[i].addEventListener("click", function(){
    var current = document.getElementsByClassName("active");
    if (current.length > 0) { 
      current[0].className = current[0].className.replace(" active", "");
    }
    this.className += " active";
  });
}

// Show all items on page load
filterSelection("all");
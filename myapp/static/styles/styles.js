/* Open the side navigation */
function openNav() {
  document.getElementById("mySidenav").classList.add("open");
}

/* Close the side navigation */
function closeNav() {
  document.getElementById("mySidenav").classList.remove("open");
}

document.getElementById("openNavBtn").addEventListener("click", openNav);
document.getElementById("closeNavBtn").addEventListener("click", closeNav);
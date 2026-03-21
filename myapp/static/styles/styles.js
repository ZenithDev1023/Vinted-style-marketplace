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
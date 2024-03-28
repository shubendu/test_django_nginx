// load the document
document.addEventListener("DOMContentLoaded", function () {
   // get all the elements with hideable class
   const msg_elements = document.querySelectorAll(".hideable");
   // loop through the elements and hide them
   msg_elements.forEach(element => {
      setTimeout(function () {
         element.style.display = "none";
      }, 5000);
    });
});
// load the document
document.addEventListener("DOMContentLoaded", function () {
   
   var message_ele = document.getElementById("message_container");
   if (message_ele) {
      setTimeout(function () {
         message_ele.style.display = "none";
      }, 3000);
   }
});
function flipCard(button) {
  const flipCard = button.closest(".flip-card");
  flipCard.classList.toggle("flip-card-flipped");
}

// document
//   .getElementById("postAdButton")
//   .addEventListener("click", function (event) {
//     event.preventDefault(); // Prevent the default action

//     // Check for the session cookie
//     let cookies = document.cookie.split(";").reduce((cookies, cookie) => {
//       let [name, value] = cookie.split("=").map((c) => c.trim());
//       cookies[name] = value;
//       return cookies;
//     }, {});

//     if (cookies.session) {
//       // If session cookie exists, redirect to addCarPage
//       window.location.href = "/addCarPage/";
//     } else {
//       // If session cookie does not exist, show the login popup
//       openPopup();
//     }
//   });

// function openPopup() {
//   document.getElementById("popup").style.display = "block";
// }

// function closePopup() {
//   document.getElementById("popup").style.display = "none";
// }

document.getElementById("postAdButton").addEventListener("click", function () {
  fetch("/check_signin_status")
    .then((response) => response.json())
    .then((data) => {
      if (data.signed_in) {
        window.location.href = "/addCarPage/";
      } else {
        window.location.href = "/signin/";
      }
    })
    .catch((error) => {
      console.error("Error checking sign-in status:", error);
      window.location.href = "/signin/";
    });
});

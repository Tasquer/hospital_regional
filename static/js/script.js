//document.addEventListener("DOMContentLoaded", function () {
const imageInput = document.getElementById("id_image");
const customImageButton = document.getElementById("customImageButton");
const nameImg = document.getElementById("nameImg");

customImageButton.addEventListener("click", function () {
  imageInput.click();
});

imageInput.addEventListener("change", function () {
  const file = imageInput.files[0];
  if (file) {
    nameImg.textContent = "Nueva imagen: " + file.name;
  } else {
    nameImg.textContent = "";
  }
});
//});

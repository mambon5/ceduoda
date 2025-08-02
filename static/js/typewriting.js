const text = document.getElementById("hidden_typewriter_title").innerHTML;
const typewriter = document.getElementById("typewriter");
const cursor = document.querySelector(".cursor");

let i = 0;
function typeEffect() {
    if (i < text.length) {
        typewriter.innerHTML += text.charAt(i);
        i++;
        setTimeout(typeEffect, 120);
    }
}

window.onload = () => {
    typeEffect();

    // 🔹 Atura el cursor després de 10 segons
    setTimeout(() => {
        cursor.style.animation = "none";
        cursor.style.opacity = 0;
    }, 3000+20); // 5 segs approx
};

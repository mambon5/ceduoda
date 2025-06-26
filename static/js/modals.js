function openModal(id) {
  const modal = document.getElementById(id);
  modal.style.display = "block";

  // Reinicia animació a la icona dins el modal
  const icon = modal.querySelector('i');
  if (icon) {
    icon.classList.remove('rotate-icon');  // treu classe per reiniciar
    void icon.offsetWidth;                  // forçem reflow per reiniciar animació
    icon.classList.add('rotate-icon');     // torna a posar la classe per animar
  }
}

function closeModal(id) {
  document.getElementById(id).style.display = "none";
}
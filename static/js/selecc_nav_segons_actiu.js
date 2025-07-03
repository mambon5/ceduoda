// Captura tots els enllaços del menú
const menuLinks = document.querySelectorAll('.side-menu a');

// Funció que detecta quina secció està visible
function onScroll() {
  let fromTop = window.scrollY + 150; // +150 per activar una mica abans

  menuLinks.forEach(link => {
    const sectionId = link.getAttribute('href');
    if (!sectionId.startsWith('#')) return;

    const section = document.querySelector(sectionId);

    if (!section) return; // Evita error si no existeix la secció

    if (
      section.offsetTop <= fromTop &&
      section.offsetTop + section.offsetHeight > fromTop
    ) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });
}

window.addEventListener('scroll', onScroll);

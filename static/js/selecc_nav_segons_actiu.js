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

function toggleMenu() {
  const menu = document.querySelector('.side-menu');
  menu.classList.toggle('visible');
}


// amagar el side menu quan es cliqui a un altre lloc de la pantalla:
const menu = document.querySelector('.side-menu');
  const toggleBtn = document.querySelector('.menu-toggle');

  function toggleMenu() {
    if (menu.classList.contains('visible') &&  window.innerWidth <= 768) {
      menu.classList.remove('visible');
      menu.classList.add('hidden');
    } else {
      menu.classList.add('visible');
      menu.classList.remove('hidden');
    }
  }

  // Al carregar la pàgina, assegura que el menú està amagat
  if (window.innerWidth <= 768)   menu.classList.add('hidden');

  document.addEventListener('click', function(event) {
    const isClickInsideMenu = menu.contains(event.target);
    const isClickOnToggle = toggleBtn.contains(event.target);

    // Si el clic NO és dins menú ni toggle i el menú és visible, l'amaguem
    if (!isClickInsideMenu && !isClickOnToggle && menu.classList.contains('visible')) {
      menu.classList.remove('visible');
      menu.classList.add('hidden');
    }
  });
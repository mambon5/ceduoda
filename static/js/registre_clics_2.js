function registraClick(pagina) {
    fetch('/registre_click', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ pagina: pagina })
    });
}

// En registrar l'obertura inicial de la pàgina
window.addEventListener('load', () => {
    registraClick("pag_principal");
});

// Registrar clics en seccions
document.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
        const href = link.getAttribute('href');
        if (href.startsWith("#")) {
            registraClick(href.replace("#", ""));
        } else {
            registraClick("enllac_extern");
        }
    });
});

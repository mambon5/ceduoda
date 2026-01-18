function enviarVisita(pagina, durada=null) {
    const data = {
        pagina: pagina,
        idioma: document.body.dataset.lang,
        resolucio: window.screen.width + "x" + window.screen.height,
        referer: document.referrer,
    };
    if (durada !== null) {
        data.durada = durada;
    }

    fetch('/registre_click', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(data)
    });
}

let temps_inici = Date.now();

window.addEventListener('load', () => {
    enviarVisita("pag_principal");
});

// Capturar clics a links amb href que comencen per #
document.querySelectorAll('.side-menu a').forEach(el => {
    el.addEventListener('click', e => {
        e.preventDefault(); // Prevenir scroll automàtic o navegació
        const href = el.getAttribute('href') || '';
        if (href.startsWith('#')) {
            const seccio = href.substring(1); // treure #
            enviarVisita(seccio);
            
            // Opcional: fer scroll manual a la secció després d'enviar la visita
            const seccioElement = document.getElementById(seccio);
            if (seccioElement) {
                seccioElement.scrollIntoView({behavior: 'smooth'});
            }
        } else {
            // Enllaç extern o altre, pots enviar "enllac_extern" o res
            enviarVisita('enllac_extern');
            window.location.href = href; // seguir l'enllaç normal
        }
    });
});

window.addEventListener('beforeunload', () => {
    let durada = Math.floor((Date.now() - temps_inici) / 1000);

    navigator.sendBeacon('/registre_click', JSON.stringify({
        pagina: 'pag_principal',
        idioma: document.body.dataset.lang,
        resolucio: window.screen.width + "x" + window.screen.height,
        referer: document.referrer,
        durada: durada
    }));
});

// 1️⃣ Captura del temps d'inici de la sessió
let scroll_max = 0;
let ultima_pagina = "entra_usuari";
let ultim_temps = Date.now();;

window.addEventListener("scroll", () => {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const percent = Math.round((scrollTop / docHeight) * 100);

    if (percent > scroll_max) {
        scroll_max = percent;
    }
});

// 2️⃣ Funció per enviar visites o clics
function enviarVisita(pagina) {

    

    let idiomaComplet = navigator.language || navigator.userLanguage || "desconegut";
    let paisNatiu = (idiomaComplet.split('-')[1] || null);
    if (paisNatiu) paisNatiu = paisNatiu.toUpperCase();

    
    
    let durada = Math.floor((Date.now() - ultim_temps) / 1000);
    ultim_temps = Date.now();

    const data = {
        pagina: ultima_pagina,
        idioma: idiomaComplet,
        idioma_base: document.body.dataset.lang,
        codi_pais_natiu: paisNatiu,
        resolucio: window.screen.width + "x" + window.screen.height,
        referer: document.referrer || "",
        hora_local: new Date().toLocaleString(),
        zona_horaria: Intl.DateTimeFormat().resolvedOptions().timeZone,
        scroll_max: scroll_max,
        durada: durada
    };

    scroll_max = 0;

    fetch('/registre_click', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(data)
    });

    ultima_pagina = pagina; // actualitza ultima pagina visitada
}

// 3️⃣ Enviem la visita de la pàgina principal al carregar
window.addEventListener('load', () => {
    enviarVisita("pag_principal");
});

// 4️⃣ Captura de clics a links amb href que comencen per #
document.querySelectorAll('.side-menu a').forEach(el => {
    el.addEventListener('click', e => {
        e.preventDefault();
        const href = el.getAttribute('href') || '';
        if (href.startsWith('#')) {
            const seccio = href.substring(1);
            enviarVisita(seccio);

            const seccioElement = document.getElementById(seccio);
            if (seccioElement) {
                seccioElement.scrollIntoView({behavior: 'smooth'});
            }
        } else {
            enviarVisita('enllac_extern');
            window.location.href = href;
        }
    });
});

// 5️⃣ Enviem durada al tancar la pàgina amb sendBeacon
window.addEventListener('beforeunload', () => {
    let durada = Math.floor((Date.now() - ultim_temps) / 1000);
    let idiomaComplet = navigator.language || navigator.userLanguage || "desconegut";
    let paisNatiu = (idiomaComplet.split('-')[1]?.toUpperCase() || "DESCONEGUT");

    const data = {
        pagina: ultima_pagina,
        idioma: idiomaComplet,
        codi_pais_natiu: paisNatiu,
        resolucio: window.screen.width + "x" + window.screen.height,
        referer: document.referrer || "",
        durada: durada,
        scroll_max: scroll_max,
        hora_local: new Date().toLocaleString(),
        zona_horaria: Intl.DateTimeFormat().resolvedOptions().timeZone
    };

    navigator.sendBeacon('/registre_click', JSON.stringify(data));
});

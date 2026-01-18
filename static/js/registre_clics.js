// 1️⃣ Captura del temps d'inici de la sessió
let temps_inici = Date.now();

let scroll_max = 0;

window.addEventListener("scroll", () => {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const percent = Math.round((scrollTop / docHeight) * 100);

    if (percent > scroll_max) {
        scroll_max = percent;
    }
});


// 2️⃣ Funció per enviar visites o clics
function enviarVisita(pagina, durada = null) {
    let idiomaComplet = navigator.language || navigator.userLanguage || "desconegut";
    let paisNatiu = (idiomaComplet.split('-')[1] || null);
    if (paisNatiu) paisNatiu = paisNatiu.toUpperCase();

    const data = {
        pagina: pagina,
        idioma: idiomaComplet,
        idioma_base: document.body.dataset.lang,
        codi_pais_natiu: paisNatiu,
        resolucio: window.screen.width + "x" + window.screen.height,
        referer: document.referrer || "",
    };

    if (durada !== null) data.durada = durada;

    fetch('/registre_click', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(data)
    });
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
    let durada = Math.floor((Date.now() - temps_inici) / 1000);
    let idiomaComplet = navigator.language || navigator.userLanguage || "desconegut";
    let paisNatiu = (idiomaComplet.split('-')[1]?.toUpperCase() || "DESCONEGUT");

    navigator.sendBeacon('/registre_click', JSON.stringify({
        pagina: 'pag_principal',
        idioma: idiomaComplet,
        codi_pais_natiu: paisNatiu,
        resolucio: window.screen.width + "x" + window.screen.height,
        referer: document.referrer || "",
        durada: durada
    }));
});

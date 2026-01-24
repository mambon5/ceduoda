let scroll_max = 0;
let ultima_pagina = "inici";   // 👈 ja comencem a la principal
let ultim_temps = Date.now();

window.addEventListener("scroll", () => {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const percent = Math.round((scrollTop / docHeight) * 100);
    if (percent > scroll_max) scroll_max = percent;
});

window.addEventListener("DOMContentLoaded", () => {
    enviarVisita(ultima_pagina); // envia "pag_principal"
    ultima_pagina="pag_principal";
    ultim_temps = Date.now();
});


function enviarVisita(pagina) {

    let idiomaComplet = navigator.language || "desconegut";
    let paisNatiu = idiomaComplet.split('-')[1]?.toUpperCase() || null;

    let ara = Date.now();
    let durada = Math.floor((ara - ultim_temps) / 1000);
    ultim_temps = ara;

    const data = {
        pagina: ultima_pagina,   // enviem la secció anterior
        idioma: idiomaComplet,
        idioma_base: document.body.dataset.lang,
        codi_pais_natiu: paisNatiu,
        resolucio: screen.width + "x" + screen.height,
        referer: document.referrer || "",
        hora_local: new Date().toLocaleString(),
        zona_horaria: Intl.DateTimeFormat().resolvedOptions().timeZone,
        scroll_max: scroll_max,
        durada: durada
    };

    scroll_max = 0;
    ultima_pagina = pagina;

    fetch('/registre_click', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(data)
    });
}

document.querySelectorAll('[data-lang-switch]').forEach(el => {
    el.addEventListener("click", e => {
        e.preventDefault();

        const lang = el.dataset.langSwitch;

        // Tanquem la secció actual com a canvi d’idioma
        enviarVisita("canvi_idioma_" + lang);

        // deixem respirar el navegador perquè el fetch surti
        setTimeout(() => {
            switchLang(lang);  // 👈 reutilitzem la teva funció
        }, 120);
    });
});


// 4️⃣ Captura de clics a links amb href que comencen per #
document.querySelectorAll('.side-menu a').forEach(el => {
    el.addEventListener('click', e => {

        if (el.hasAttribute("data-lang-switch")) return;

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
// clicks menú igual que tens ✔️


// 🔄 Event correcte per tancament
window.addEventListener("pagehide", () => {
    console.log("Pagehide disparat! ultima_pagina=", ultima_pagina, "scroll_max=", scroll_max);

    let idiomaComplet = navigator.language || "desconegut";
    let paisNatiu = idiomaComplet.split('-')[1]?.toUpperCase() || null;

    let durada = Math.floor((Date.now() - ultim_temps) / 1000);

    navigator.sendBeacon('/registre_click', JSON.stringify({
        pagina: ultima_pagina,
        idioma: idiomaComplet,
        idioma_base: document.body.dataset.lang,
        codi_pais_natiu: paisNatiu,
        resolucio: screen.width + "x" + screen.height,
        referer: document.referrer || "",
        durada: durada,
        scroll_max: scroll_max,
        hora_local: new Date().toLocaleString(),
        zona_horaria: Intl.DateTimeFormat().resolvedOptions().timeZone
    }));
});













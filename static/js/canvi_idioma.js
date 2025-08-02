function switchLang(lang) {
  const currentHash = window.location.hash; // guarda la secció actual, ex: #equip
  window.location.href = `/${lang}${currentHash}`; // redirecciona mantenint l’anchor
}
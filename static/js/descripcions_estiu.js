document.querySelectorAll("details > summary").forEach((summary) => {
    summary.addEventListener("click", function (event) {
      const clickedSummary = this;

      // Retarda l’scroll perquè es faci després de l’expansió
      setTimeout(() => {
        clickedSummary.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 100); // temps suficient per deixar expandir el details
    });
  });

  // També tanquem els altres <details> si se’n clica un de nou
  document.addEventListener("click", function(event) {
    document.querySelectorAll("details[open]").forEach((detail) => {
      if (!detail.contains(event.target)) {
        detail.removeAttribute("open");
      }
    });
  });
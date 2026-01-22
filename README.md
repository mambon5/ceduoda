# ceduoda
pagina web del centre d'estudis duoda

# Com usar el codi

1. Hi ha un fitxer de python `crea_dades.py` que crea les taules necessàries a la base de dades mysql.
2. Després ja es pot executar la app `app.py`.
   
   S'ha de tenir en compte que cal crear una base de dades, usuari, i un entorn virtual per poder fer que tot funcioni.


## Com crear un usuari en mysql

    CREATE USER 'sammy'@'localhost' IDENTIFIED BY 'password';
    GRANT ALL PRIVILEGES ON *.* TO 'sammy'@'localhost' WITH GRANT OPTION;
    FLUSH PRIVILEGES;

### Afegir paràmetres a la bbdd

1. Afegir un idioma estàndard i unificat:
    ALTER TABLE visites ADD COLUMN idioma_base VARCHAR(20) DEFAULT NULL;

2. Afegirm un codi del possible país natiu de l'usuari
    ALTER TABLE visites ADD COLUMN codi_pais_natiu VARCHAR(5) DEFAULT NULL;

3. Afegir nom del país
   ALTER TABLE visites ADD COLUMN pais_natiu VARCHAR(50) DEFAULT NULL;

4. Afegir tot de variables sobre l'orígen del tràfic web:

    ALTER TABLE visites ADD lat VARCHAR(20) NULL;
    ALTER TABLE visites ADD lon VARCHAR(20) NULL;
    ALTER TABLE visites ADD ciutat VARCHAR(100) NULL;
    ALTER TABLE visites ADD regio VARCHAR(100) NULL;
    ALTER TABLE visites ADD pais_fisic VARCHAR(100) NULL;
    ALTER TABLE visites ADD codi_pais_fisic VARCHAR(5) NULL;
    ALTER TABLE visites ADD zip VARCHAR(15) NULL;
    ALTER TABLE visites ADD isp VARCHAR(150) NULL;
    ALTER TABLE visites ADD org VARCHAR(150) NULL;
    ALTER TABLE visites ADD as_name VARCHAR(150) NULL;

5. Afegir variables sobre el dispositiu que ens visita:

    ALTER TABLE visites 
    ADD COLUMN tipus_dispositiu VARCHAR(20),
    ADD COLUMN navegador VARCHAR(30),
    ADD COLUMN sistema_operatiu VARCHAR(30),
    ADD COLUMN model_dispositiu VARCHAR(50);

6. afegir zona horaria i scroll max
   
    ALTER TABLE visites 
    ADD COLUMN hora_local VARCHAR(40),
    ADD COLUMN zona_horaria VARCHAR(40),
    ADD COLUMN scroll_max INT;


## Estructura d'arbre

    rtree -I venv
    .
    ├── app.py
    ├── config.py
    ├── config.wsgi
    ├── crea_dades.py
    ├── nova_visita.py
    ├── __pycache__
    │   ├── config.cpython-310.pyc
    │   └── crea_dades.cpython-310.pyc
    ├── README.md
    ├── requirements.txt
    ├── static
    │   ├── css
    │   │   ├── style.css
    │   │   └── w3.css
    │   ├── images
    │   │   ├── elenap.jpeg
    │   │   ├── logo_10.png
    │   │   ├── logo_9.png
    │   │   ├── marcs.jpg
    │   │   ├── roma.jpg
    │   │   ├── sergi.png
    │   │   └── superficie_backg.jpg
    │   ├── js
    │   │   ├── canvi_idioma.js
    │   │   ├── descripcions_estiu.js
    │   │   ├── modals.js
    │   │   ├── registre_clics_2.js
    │   │   ├── registre_clics.js
    │   │   ├── selecc_nav_segons_actiu.js
    │   │   └── typewriting.js
    │   └── translations
    │       ├── ca copy.json
    │       ├── ca.json
    │       ├── en.json
    │       └── es.json
    ├── templates
    │   ├── estadistiques.html
    │   ├── index copy 06_2025.html
    │   ├── index copy 08_2025.html
    │   ├── index.html
    │   └── visites.html
    └── veure_visites.py

    7 directories, 35 files

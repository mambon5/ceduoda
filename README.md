# ceduoda
pagina web del centre d'estudis duoda

# Afegir wsgi al vh

Afegir la següent linia un cop creat el certificat ssl amb certbot:

```
# Línia per executar Flask/WSGI:
# Activa mode dimoni amb el teu entorn virtual Python
    WSGIDaemonProcess ceduoda python-home=/var/www/ceduoda/venv python-path=/var/www/ceduoda
    WSGIProcessGroup ceduoda
    WSGIScriptAlias / /var/www/ceduoda/config.wsgi
```
al fitxer: 

```
ceduoda.com-le-ssl.con
```

El fitxer ha de quedar una cosa aixi:

```
romanov@mireia77serv:/etc/apache2/sites-available$ more ceduoda.com-le-ssl.conf 
<IfModule mod_ssl.c>
<VirtualHost *:443>
    ServerName ceduoda.com
   # ServerAlias www.ceduoda.com

    DocumentRoot /var/www/ceduoda

    # Activa mode dimoni amb el teu entorn virtual Python
    WSGIDaemonProcess ceduoda python-home=/var/www/ceduoda/envi python-path=/var/www/ceduoda
    WSGIProcessGroup ceduoda
    WSGIScriptAlias / /var/www/ceduoda/config.wsgi

    <Directory /var/www/ceduoda>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/ceduoda_error.log
    CustomLog ${APACHE_LOG_DIR}/ceduoda_access.log combined
RewriteEngine on
# Some rewrite rules in this file were disabled on your HTTPS site,
# because they have the potential to create redirection loops.

# RewriteCond %{SERVER_NAME} =ceduoda.com [OR]
# #RewriteCond %{SERVER_NAME} =www.ceduoda.com
# RewriteRule ^ https://%{SERVER_NAME}%{REQUEST_URI} [END,NE,R=permanent]

SSLCertificateFile /etc/letsencrypt/live/ceduoda.com/fullchain.pem
SSLCertificateKeyFile /etc/letsencrypt/live/ceduoda.com/privkey.pem
Include /etc/letsencrypt/options-ssl-apache.conf
</VirtualHost>
</IfModule>
```

## fer test per veure si funciona:


```
sudo -u www-data /var/www/ceduoda/envi/bin/python3 -c 'import sys; sys.path.insert(0, "/var/www/ceduoda"); from app import app; print("CARREGAT OK")'
```

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


# Instalar numpy a servidor antic.

✅ Pla net i segur

1️⃣ Elimina l’entorn trencat:

cd /var/www/ceduoda
rm -rf envi


2️⃣ Crea entorn nou:

python3 -m venv envi
source envi/bin/activate
pip install --upgrade pip setuptools wheel


3️⃣ Instal·la versions modernes (amb wheels):

pip3 install "numpy<2.0,>=1.26.0"

pip3 install pandas matplotlib flask gunicorn


⚠️ NO posis --no-binary

💡 Per què ara funcionarà?

Les versions modernes:

numpy ≥2.x

pandas recents

matplotlib recents

👉 ja tenen wheels per Python 3.12 → no compilen → no tarden hores → no pete


# Executar app

```
python app.py
```


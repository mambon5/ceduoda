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
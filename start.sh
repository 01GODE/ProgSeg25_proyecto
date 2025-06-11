#!/bin/bash

echo "Introduce la contraseña:"
read -s pass

while read -r linea; do    
    export "$linea"
done < <(ccrypt -c -K "$pass" .env.cpt)

echo $DB_ENGINE

python3 manage.py runserver 0.0.0:8000
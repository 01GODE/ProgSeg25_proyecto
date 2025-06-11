#!/bin/bash

echo "Introduce la contraseña:"
read -s pass

while read -r linea; do    
    export "$linea"
done < <(ccrypt -c -K "$pass" .env.cpt)

echo $VARIABLES

python3 manage.py runserver

#!/bin/bash

echo "Introduce la contraseña:"
read -s pass

while read -r linea; do    
    export "$linea"
done < <(ccrypt -c -K "$pass" .env.cpt)

echo $VARIABLES

sudo docker-compose down && sudo docker-compose up -d

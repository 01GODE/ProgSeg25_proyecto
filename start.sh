#!/bin/bash

echo "Introduce la contraseña:"
read -s pass

ccrypt -d -K "$pass" .env.cpt

# Exportar las variables del archivo .env
export $(grep -v '^#' .env | xargs)

echo $DB_ENGINE

python3 manage.py runserver 0.0.0:8000

ccrypt -e -K "$pass" .env

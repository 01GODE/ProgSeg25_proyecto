#!/bin/bash

# ========= CONFIGURACIÓN =========
SSH_USER="debian"
SSH_HOST="192.168.1.239"
SSH_PASS="debian"   # Reemplaza por la contraseña real del servidor
DB_FILE="/home/debian/proyecto/db/db.sql"
DOCKER_DJANGO="django"
DOCKER_MYSQL="mysql"
DB_NAME="django"  # Asegúrate que este sea el mismo que definiste en el .env

# ========= VERIFICAR ARCHIVO DB =========
if [ ! -f "$DB_FILE" ]; then
  echo "❌ El archivo $DB_FILE no existe. Cancelo la operación."
  exit 1
fi

# ========= GENERAR LLAVE SSH EN EL CONTENEDOR SI NO EXISTE =========
echo "🔐 Verificando clave SSH dentro del contenedor Django..."
sudo docker exec -u debian "$DOCKER_DJANGO" bash -c '
  if [ ! -f /home/debian/.ssh/id_rsa ]; then
    mkdir -p /home/debian/.ssh
    ssh-keygen -t rsa -b 4096 -f /home/debian/.ssh/id_rsa -N "" -q
    echo "✅ Clave SSH generada."
  else
    echo "🟢 Clave SSH ya existe."
  fi
'

# ========= COPIAR CLAVE PÚBLICA AL SERVIDOR REMOTO =========
echo "🚀 Instalando clave pública en el servidor remoto..."
sudo docker exec -u debian "$DOCKER_DJANGO" sshpass -p "$SSH_PASS" \
  ssh -o StrictHostKeyChecking=no "$SSH_USER@$SSH_HOST" \
  "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys" < ~/.ssh/id_rsa.pub

echo "✅ Clave autorizada en $SSH_HOST."

# ========= COPIAR Y RESTAURAR BASE DE DATOS =========
echo "💾 Copiando base de datos al contenedor MySQL..."
sudo docker cp "$DB_FILE" "$DOCKER_MYSQL":/db.sql

echo "🔄 Restaurando base de datos en el contenedor..."
sudo docker exec -i "$DOCKER_MYSQL" bash -c \
  'mysql -u root -p"$MYSQL_ROOT_PASSWORD" '"$DB_NAME"' < /db.sql'

echo "✅ Base de datos restaurada correctamente."

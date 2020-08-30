sudo -u postgres psql << EOF
  CREATE USER ekpogo PASSWORD 'sOnsCzkzuewHY6pG';
  CREATE DATABASE ekpogo OWNER ekpogo;
  \c ekpogo
  CREATE EXTENSION postgis;
  CREATE EXTENSION citext;
EOF

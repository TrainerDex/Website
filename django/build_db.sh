sudo -u postgres psql << EOF
  CREATE USER tdx PASSWORD 'password';
  CREATE DATABASE tdx OWNER tdx;
  \c tdx
  CREATE EXTENSION postgis;
  CREATE EXTENSION citext;
EOF

sudo -u postgres psql << EOF
  CREATE USER ekpogo PASSWORD '***REMOVED***';
  CREATE DATABASE ekpogo OWNER ekpogo;
  \c ekpogo
  CREATE EXTENSION postgis;
  CREATE EXTENSION citext;
EOF

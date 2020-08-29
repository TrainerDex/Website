psql << EOF
  \c ekpogo
  CREATE EXTENSION postgis;
  CREATE EXTENSION citext;
EOF

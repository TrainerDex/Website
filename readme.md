![Django CI & Lint](https://github.com/JayTurnr/trainerdex.co.uk/workflows/Django%20CI%20&%20Lint/badge.svg?branch=feature%2Fdjango3majorrewrite)

# django

## Environment setup
```
source env/bin/activate
```

### Compiles and hot-reloads for development
```
python manage.py runserver
```

### Compiles and minifies for production
```
python manage.py collectstatic --clear
python manage.py migrate
```

### Fixes files
```
python manage.py makemessages --no-wrap --ignore=env/* -l en -l de -l es -l fr -l it -l ja -l ko -l pt-br -l zh-hant
```

# vue

## Project setup
```
npm install
```

### Compiles and hot-reloads for development
```
npm run serve
```

### Compiles and minifies for production
```
npm run build
```

### Lints and fixes files
```
npm run lint
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).

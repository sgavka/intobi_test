# Stack
- python3.9
- Django 3
- Postgres — for DB

# Env requirements
- Linux OS
- Docker
- Docker Compose

# Project Structure
- dir `main` all project's configs;
- dir `app` all project's logics;

# Develop

## Start
1. Build & setup project

Hard re-build:
```shell
docker-compose -f docker-compose-prod.yml down -v
```

Init prod:
```shell
docker-compose -f docker-compose-prod.yml build

docker-compose -f docker-compose-prod.yml run web python manage.py migrate
docker-compose -f docker-compose-prod.yml run web python manage.py createsuperuser

docker-compose -f docker-compose-prod.yml up -d
```

## Allow editing files
```shell
sudo chown -R $USER:$USER .
```

## Run command in container
```shell
docker-compose run [container] [command]
```

## Set up debug for django commands

1.Open Run/Config Configuration.
2. Set Script path to `manage.py`.
3. In Parameters set name of command.
4. Set up Work directory to project root.
5. Select new configuration and run Debug.

## Migrations

### Reverse to specific migration
```shell
docker-compose run web python3 manage.py migrate [app] [last_migration]
```

### Reverse all migrations
```shell
docker-compose run web python3 manage.py migrate [app] zero
```

### Create migrations
```shell
docker-compose run web python manage.py makemigrations
```

### Migrate
```shell
docker-compose run web python manage.py migrate
```

## Create Admin superuser
```shell
docker-compose run web python manage.py createsuperuser
```

## Fixtures

### Load fixtures
```shell
docker-compose run web python manage.py loaddata <fixturename>
```

### Create fixtures from database
```shell
docker-compose run web python manage.py dumpdata <module>.<table> --format=yaml > <app>/fixtures/<file_name>.yaml
```

## Translation

### Generate po file
```shell
docker-compose run web python manage.py makemessages -l <lang_code>
```

### Compile messages
```shell
docker-compose run web python manage.py compilemessages
```

## Run to develop
1. Config Django server (in files .run/);
2. Start Django server in debug mode;

# Production

## Build server
```shell
docker-compose -f docker-compose-prod.yml build
```

## Start server
```shell
docker-compose -f docker-compose-prod.yml up -d
```

## Migrate
```shell
docker-compose -f docker-compose-prod.yml run web python manage.py migrate
```

## Create Admin superuser
```shell
docker-compose -f docker-compose-prod.yml run web python manage.py createsuperuser
```

## Load fixtures
```shell
docker-compose -f docker-compose-prod.yml run web python manage.py loaddata <fixturename>
```

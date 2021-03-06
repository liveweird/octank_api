# How to create a virtual env?

pyenv virtualenv octank_api

# How to dump dependencies?

pip freeze > requirements.txt

# How to restore dependencies?

pip install -r requirements.txt

# How to set up DB?

docker run --name pg_octank_api -e POSTGRES_PASSWORD=postgres -d -p 5432:5432 postgres:alpine

# How to run migrations? (DB has to be created already!)

alembic upgrade head

# How to run API?

export FLASK_APP=octank_api
python -m flask run

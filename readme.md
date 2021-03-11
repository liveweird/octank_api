# How to create a virtual env?

pyenv install 3.9.1
pyenv virtualenv 3.9.1 octank_api

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

# How to build a Docker image?

docker login -u AWS -p $(aws ecr get-login-password --region eu-central-1) {ECR registry}

docker build -t octank_api .
docker tag octank_api:latest {ECR registry}/octank_api:latest

aws ecr create-repository \
    --repository-name octank_api \
    --image-scanning-configuration scanOnPush=false \
    --region eu-central-1
docker push {ECR registry}/octank_api:latest

docker build -t octank_task -f Dockerfile.task .
docker tag octank_task:latest {ECR registry}/octank_task:latest

aws ecr create-repository \
    --repository-name octank_task \
    --image-scanning-configuration scanOnPush=false \
    --region eu-central-1
docker push {ECR registry}/octank_task:latest

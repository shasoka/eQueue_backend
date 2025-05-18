# docker-compose up
docker compose build --no-cache && docker compose up -d
# alembic upgrade head
docker exec -it equeue_backend python -m alembic upgrade head

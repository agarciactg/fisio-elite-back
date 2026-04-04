# correr migraciones:

sudo docker exec -it backend-app-web-1 alembic revision --autogenerate -m "Add full relations schemas"

sudo docker exec -it backend-app-web-1 alembic upgrade head

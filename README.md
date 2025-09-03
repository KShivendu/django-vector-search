## Django Vector Search Demo



```py
# Setup the DB
uv run manage.py makemigrations
uv run manage.py makemigrations ecommerce
uv run manage.py migrate
uv run manage.py populate_db

# Setup Elasticsearch
uv run manage.py search_index --create
uv run manage.py search_index --populate
uv run manage.py search_index --rebuild

# Run server:
uv run manage.py runserver
```

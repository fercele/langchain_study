FROM 3.11.3-alpine3.17

WORKDIR /usr/src/app

COPY requirements.txt .

python -m pip install -r requirements.txt

COPY gerenciador_api_keys .
COPY quickstart .



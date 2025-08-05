#!/usr/bin/env bash
# start.sh — inicialização do projeto Django + Postgres (Docker) no macOS/Linux
# Como usar (na raiz do projeto):
#   chmod +x start.sh
#   ./start.sh

set -euo pipefail

# Garante que estamos na pasta do script (raiz do projeto)
cd "$(dirname "$0")"

echo "==> Subindo Postgres via Docker Compose..."
# Sobe o serviço do banco em segundo plano (cria rede, volume e container se não existirem)
docker compose up -d

echo "==> Containers:"
docker compose ps

# Cria venv se não existir e ativa
if [ ! -d ".venv" ]; then
  echo "==> Criando virtualenv (.venv)..."
  python3 -m venv .venv
fi

# Ativa a venv no shell atual
# shellcheck disable=SC1091
# os/lnx 
# source .venv/bin/activate
# win
source .venv/Scripts/activate

# Instala dependências se houver requirements.txt (idempotente)
if [ -f "requirements.txt" ]; then
  echo "==> Instalando dependências (pip)..."
  pip install -r requirements.txt
fi

# Aplica migrações (cria/atualiza tabelas no banco configurado)
echo "==> Aplicando migrações..."
python manage.py migrate

# Sobe o servidor de desenvolvimento (CTRL+C para parar)
echo "==> Iniciando Django (http://127.0.0.1:8000) ..."
python manage.py runserver

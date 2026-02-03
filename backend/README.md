# FastAPI Backend

## Setup
cd backend
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install "fastapi[standard]"

## Run
.venv\Scripts\activate
cd app
fastapi dev main.py

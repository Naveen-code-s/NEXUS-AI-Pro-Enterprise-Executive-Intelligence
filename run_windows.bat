@echo off
if not exist .venv\Scripts\python.exe python -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
if not exist .env copy .env.example .env
streamlit run app.py

streamlit run ui/app.py

uvicorn backend.api.main:app --reload


\l
\c loan_db
\dt
SELECT * FROM users
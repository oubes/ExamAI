# ExamAI Setup Guide

## Project Overview

ExamAI is an AI-powered educational platform for:

* Adaptive exam generation
* Intelligent grading
* Personalized feedback generation
* Student performance analytics
* RAG-powered educational retrieval

---

# 1) Clone The Project

Clone the repository:

```bash id="q4t8nm"
git clone https://github.com/oubes/ExamAI
cd ExamAI
```

Repository:

* [ExamAI GitHub Repository](https://github.com/oubes/ExamAI?utm_source=chatgpt.com)

---

# 2) Create Conda Environment

Create a new conda environment using Python 3.11:

```bash id="x7m2pr"
conda create -n exam_ai python=3.11
```

Activate the environment:

```bash id="c1v9zs"
conda activate exam_ai
```

Install project requirements:

```bash id="l5r3wd"
pip install -r requirements.txt
```

---

# 3) Install PostgreSQL

Download and install PostgreSQL:

* [PostgreSQL Official Website](https://www.postgresql.org/download/?utm_source=chatgpt.com)

After installation:

* Open PostgreSQL
* Create a database named:

```text id="b8y1qk"
exam_ai_db
```

---

# 4) Enable PostgreSQL Extensions

Open PostgreSQL Query Tool and execute:

```sql id="n6w4tf"
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

These extensions are required for:

* Vector embeddings search
* Semantic retrieval
* Hybrid RAG search
* Trigram similarity matching

---

# 5) Open The Project In VSCode Or Any IDE

Recommended IDEs:

* [Visual Studio Code](https://code.visualstudio.com/?utm_source=chatgpt.com)
* [PyCharm](https://www.jetbrains.com/pycharm/?utm_source=chatgpt.com)

---

# 6) Create Alibaba DashScope API Key

ExamAI uses Alibaba DashScope for:

* LLM inference
* Embedding models

Create an account here:

* [Alibaba DashScope](https://dashscope.console.aliyun.com/?utm_source=chatgpt.com)

Generate your API key.

---

# 7) Configure Gmail SMTP

ExamAI uses Gmail SMTP for:

* Verification emails
* Password reset emails
* Notification emails

---

## Step 1 — Enable 2-Step Verification

Open Google Account Security:

* [Google Account Security](https://myaccount.google.com/security?utm_source=chatgpt.com)

Enable:

```text id="q9f4wk"
2-Step Verification
```

Direct link:

* [Enable 2-Step Verification](https://myaccount.google.com/signinoptions/two-step-verification?utm_source=chatgpt.com)

---

## Step 2 — Generate Gmail App Password

Open App Passwords:

* [Google App Passwords](https://myaccount.google.com/apppasswords?utm_source=chatgpt.com)

Then:

1. Select:

```text id="t3m8xy"
Mail
```

2. Select device:

```text id="g5w2lh"
Other (Custom name)
```

3. Enter:

```text id="u1r7zc"
ExamAI
```

4. Click:

```text id="y6k9vd"
Generate
```

Google will generate a 16-character password.

Example:

```text id="m2q4pe"
abcd efgh ijkl mnop
```

Use this generated password inside:

```text id="h8v1rk"
SMTP_PASSWORD
```

---

# 8) Configure Environment Variables

Inside the project root:

* Copy `.env.example`
* Rename the copied file to `.env`
* Update all variables according to your local machine and accounts

Example:

```bash id="d7x5mb"
cp .env.example .env
```

Update values such as:

* PostgreSQL credentials
* Alibaba API key
* JWT secrets
* Gmail SMTP credentials
* Redis URLs

Example SMTP configuration:

```env id="w4n8qs"
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_generated_app_password
SMTP_FROM=your_email@gmail.com
```

---

# 9) Install Docker

Download and install Docker Desktop:

* [Docker Desktop](https://www.docker.com/products/docker-desktop/?utm_source=chatgpt.com)

After installation:

* Open Docker Desktop
* Make sure Docker is running

---

# 10) Run The Project

You will need multiple terminals.

---

## Terminal 1 — Run FastAPI

```bash id="s5k1qn"
uvicorn src.main:app --reload
```

---

## Terminal 2 — Start Redis Container

```bash id="j8w3pm"
docker compose up -d
```

---

## Terminal 3 — Run Celery Worker

```bash id="f6x9tv"
celery -A src.infra.queue.celery_app.celery_app worker --loglevel=info --concurrency=4 --pool=solo -E
```

---

## Terminal 4 (Optional) — Run Flower Dashboard

```bash id="r2v7yc"
celery -A src.infra.queue.celery_app.celery_app flower
```

Flower is used for:

* Monitoring Celery tasks
* Monitoring queues and workers
* Debugging async jobs

---

# 11) Access The API

Open:

```text id="k1m6we"
127.0.0.1:8000
```

Swagger documentation:

```text id="p9t3xs"
127.0.0.1:8000/docs
```

You can now start using the APIs.

---

# Recommended Tools

## API Testing

* [Postman](https://www.postman.com/?utm_source=chatgpt.com)
* [Insomnia](https://insomnia.rest/?utm_source=chatgpt.com)

---

# Main Technologies Used

| Component        | Technology        |
| ---------------- | ----------------- |
| Backend          | FastAPI           |
| Database         | PostgreSQL        |
| Vector Search    | pgvector          |
| Async Tasks      | Celery            |
| Queue Broker     | Redis             |
| LLM Provider     | Alibaba DashScope |
| ORM              | SQLAlchemy        |
| Validation       | Pydantic          |
| Containerization | Docker            |

---

# Notes

* PostgreSQL must be running before starting the backend.
* Docker Desktop must be running before starting Redis.
* Redis is required for Celery tasks.
* Make sure all environment variables are configured correctly before running the system.

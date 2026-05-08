# ExamAI Setup Guide

## Project Overview

ExamAI is an AI-powered educational platform for:

* Adaptive exam generation
* Intelligent grading
* Personalized feedback generation
* Student performance analytics
* RAG-powered educational retrieval

---

# 1) Install Prerequisites

## Install Python (3.11)

[https://www.python.org/downloads/](https://www.python.org/downloads/)

Verify:

```bash id="py1"
python --version
```

---

## Install Node.js (Frontend requirement)

[https://nodejs.org/](https://nodejs.org/)

Verify:

```bash id="node1"
node -v
npm -v
```

---

## Install Git

[https://git-scm.com/downloads](https://git-scm.com/downloads)

Verify:

```bash id="git1"
git --version
```

---

## Install Docker

[https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)

Make sure Docker is running.

---

# 2) Clone The Project

```bash id="cl1"
git clone https://github.com/oubes/ExamAI
cd ExamAI
```

[https://github.com/oubes/ExamAI](https://github.com/oubes/ExamAI)

---

# 3) Create Conda Environment

```bash id="co1"
conda create -n exam_ai python=3.11
conda activate exam_ai
```

---

# 4) Install Backend Dependencies

```bash id="pip1"
pip install -r requirements.txt
```

---

# 5) Install PostgreSQL

[https://www.postgresql.org/download/](https://www.postgresql.org/download/)

After installation:

* Create database:

```text id="db1"
exam_ai_db
```

---

# 6) Enable PostgreSQL Extensions

Run in PostgreSQL:

```sql id="sql1"
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

---

# 7) Create Alibaba API Key

[https://dashscope.console.aliyun.com/](https://dashscope.console.aliyun.com/)

Used for:

* LLM
* Embeddings

---

# 8) Configure Gmail SMTP

## Enable 2-Step Verification

[https://myaccount.google.com/signinoptions/two-step-verification](https://myaccount.google.com/signinoptions/two-step-verification)

---

## Generate App Password

[https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)

Use it as:

```text id="mail1"
SMTP_PASSWORD
```

---

# 9) Setup Environment Variables

```bash id="env1"
cp .env.example .env
```

Then update:

* PostgreSQL credentials
* Redis URLs
* JWT secrets
* Alibaba API key
* SMTP credentials

---

# 10) Run Backend System

## Terminal 1 — FastAPI

```bash id="b1"
uvicorn src.main:app --reload
```

---

## Terminal 2 — Redis (Docker)

```bash id="b2"
cd src
docker compose up -d
```

---

## Terminal 3 — Celery Worker

```bash id="b3"
celery -A src.infra.queue.celery_app.celery_app worker --loglevel=info --concurrency=4 --pool=solo -E
```

---

## Terminal 4 — (Optional) Flower

```bash id="b4"
celery -A src.infra.queue.celery_app.celery_app flower
```

---

# 11) Run Frontend (Next.js)

## Step 1 — Install Node Modules

```bash id="f1"
cd frontend
npm install
```

---

## Step 2 — Run Frontend

```bash id="f2"
npm run dev
```

---

## Step 3 — Open App

[http://localhost:3000](http://localhost:3000)

---

# ⚠️ Frontend Notes

If issues happen:

```bash id="f3"
rm -rf .next
npm install
npm run dev
```

Backend must be running at:

```text id="f4"
http://127.0.0.1:8000
```

---

# 12) Access API

* [http://127.0.0.1:8000](http://127.0.0.1:8000)
* [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

# Tech Stack

| Layer     | Tech              |
| --------- | ----------------- |
| Backend   | FastAPI           |
| DB        | PostgreSQL        |
| Vector DB | pgvector          |
| Queue     | Celery            |
| Broker    | Redis             |
| LLM       | Alibaba DashScope |
| Frontend  | Next.js           |
| UI        | shadcn            |

---

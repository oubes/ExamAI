# 🚀 ExamAI Setup Guide

## 🧠 Project Overview

ExamAI is an AI-powered educational platform for:

* Adaptive exam generation
* Intelligent grading
* Personalized feedback generation
* Student performance analytics
* RAG-powered educational retrieval

---

# 1️⃣ Install Prerequisites

## 🐍 Python (3.11)

Download:
[https://www.python.org/downloads/](https://www.python.org/downloads/)

Verify:

```bash
python --version
```

---

## 🌐 Node.js (Frontend)

Download:
[https://nodejs.org/](https://nodejs.org/)

Verify:

```bash
node -v
npm -v
```

---

## 🐳 Docker

Download:
[https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)

> تأكد إن Docker شغال قبل أي خطوة لاحقة

---

## 🧱 Visual Studio C++ Build Tools (Windows فقط)

Required for `pgvector` builds

* Install Visual Studio Community
  [https://visualstudio.microsoft.com/downloads/](https://visualstudio.microsoft.com/downloads/)
* اختر: **Desktop development with C++**

---

# 2️⃣ Clone Project

```bash
git clone https://github.com/oubes/ExamAI
cd ExamAI
```

---

# 3️⃣ Create Environment

```bash
conda create -n exam_ai python=3.11
conda activate exam_ai
```

---

# 4️⃣ Install Backend Dependencies

```bash
pip install -r requirements.txt
```

---

# 5️⃣ PostgreSQL + pgvector Setup

## 🗄️ Install PostgreSQL

* Version: 16+
* Components: Server + pgAdmin + CLI
* Set password for `postgres`

[https://www.postgresql.org/download/windows/](https://www.postgresql.org/download/windows/)

---

## ⚙️ Build pgvector

Run in **x64 Native Tools Command Prompt (Admin)**:

```bat
set "PGROOT=C:\Program Files\PostgreSQL\16"

cd %TEMP%
git clone https://github.com/pgvector/pgvector.git
cd pgvector
nmake /F Makefile.win
nmake /F Makefile.win install
```

---

## 🧪 Initialize DB

Restart PostgreSQL service → open pgAdmin → create DB:

```
exam_ai_db
```

ثم نفّذ:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE test_vector (
    id SERIAL PRIMARY KEY,
    embedding VECTOR(384)
);

DROP TABLE test_vector;
```

---

# 6️⃣ Alibaba API Key

[https://dashscope.console.aliyun.com/](https://dashscope.console.aliyun.com/)

---

# 7️⃣ Gmail SMTP Setup

## Enable 2FA

[https://myaccount.google.com/signinoptions/two-step-verification](https://myaccount.google.com/signinoptions/two-step-verification)

## Generate App Password

[https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)

---

# 8️⃣ Environment Variables

```bash
cp .env.example .env
```

## Fill:

* PostgreSQL config
* Redis URLs
* JWT secrets
* `DASHSCOPE_API_KEY`
* SMTP credentials

---

# 9️⃣ Run Backend

## FastAPI

```bash
uvicorn src.main:app --reload
```

---

## Redis (Docker)

```bash
cd src
docker compose up -d
```

---

## Celery Worker

```bash
celery -A src.infra.queue.celery_app.celery_app worker \
--loglevel=info --concurrency=4 --pool=solo -E
```

---

## Flower (Optional)

```bash
celery -A src.infra.queue.celery_app.celery_app flower
```

---

# 🔟 Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Open:

```
http://localhost:3000
```

---

# ⚠️ Troubleshooting

## Frontend Reset

```bash
rm -rf .next
npm install
npm run dev
```

---

## Backend URL

* API: [http://127.0.0.1:8000](http://127.0.0.1:8000)
* Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

# 🧱 Tech Stack

| Layer     | Tech                     |
| --------- | ------------------------ |
| Backend   | FastAPI                  |
| DB        | PostgreSQL 16+           |
| Vector DB | pgvector                 |
| Queue     | Celery                   |
| Broker    | Redis                    |
| AI        | Alibaba DashScope (Qwen) |
| Frontend  | Next.js 14               |
| UI        | Tailwind + shadcn/ui     |

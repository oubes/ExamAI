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

> **Note:** Ensure Docker Desktop is running before proceeding to subsequent steps.

---

## 🧱 Visual Studio C++ Build Tools (Windows Only)

Required for building `pgvector` from source.

* Install Visual Studio Community: [https://visualstudio.microsoft.com/downloads/](https://visualstudio.microsoft.com/downloads/)
* During installation, select the workload: **Desktop development with C++**

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

* **Version:** 16+
* **Components:** Server + pgAdmin + CLI
* Set a password for the `postgres` user and keep it secure.

Download: [https://www.postgresql.org/download/windows/](https://www.postgresql.org/download/windows/)

---

## ⚙️ Build pgvector

Run the following commands in the **x64 Native Tools Command Prompt for VS 2022** (Run as Administrator):

```bat
# Set the PostgreSQL root path (Update '16' if your version differs)
set "PGROOT=C:\Program Files\PostgreSQL\16"

cd %TEMP%
git clone https://github.com/pgvector/pgvector.git
cd pgvector
nmake /F Makefile.win
nmake /F Makefile.win install

```

---

## 🧪 Initialize Database

1. Restart the PostgreSQL service via Windows Services (`postgresql-x64-16`).
2. Open **pgAdmin** and create a new database named: `exam_ai_db`.
3. Open the **Query Tool** for `exam_ai_db` and execute:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Verify vector support
CREATE TABLE test_vector (
    id SERIAL PRIMARY KEY,
    embedding VECTOR(384)
);

DROP TABLE test_vector;

```

---

# 6️⃣ Alibaba API Key

Create and obtain your API key from the DashScope console:
[https://dashscope.console.aliyun.com/](https://dashscope.console.aliyun.com/)

---

# 7️⃣ Gmail SMTP Setup

## Enable 2FA

[https://myaccount.google.com/signinoptions/two-step-verification](https://myaccount.google.com/signinoptions/two-step-verification)

## Generate App Password

[https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
*Select 'Other' and name it 'ExamAI' to get your 16-character password.*

---

# 8️⃣ Environment Variables

```bash
cp .env.example .env

```

## Update values in `.env`:

* **Database:** PostgreSQL credentials and DB name.
* **Cache/Broker:** Redis URLs.
* **Security:** JWT secrets.
* **AI:** `DASHSCOPE_API_KEY`.
* **Mail:** SMTP credentials and App Password.

---

# 9️⃣ Run Backend

## Terminal 1: FastAPI

```bash
uvicorn src.main:app --reload

```

## Terminal 2: Redis (Docker)

```bash
cd src
docker compose up -d

```

## Terminal 3: Celery Worker

```bash
celery -A src.infra.queue.celery_app.celery_app worker \
--loglevel=info --concurrency=4 --pool=solo -E

```

## Terminal 4: Flower (Optional Monitoring)

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

Access the application at: `http://localhost:3000`

---

# ⚠️ Troubleshooting

## Frontend Reset

If the frontend behaves unexpectedly or fails to build:

```bash
rm -rf .next
npm install
npm run dev

```

## Backend Access

* **API Base:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
* **Interactive Docs (Swagger):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

# 🧱 Tech Stack

| Layer | Tech |
| --- | --- |
| **Backend** | FastAPI |
| **Database** | PostgreSQL 16+ |
| **Vector Engine** | pgvector |
| **Task Queue** | Celery |
| **Message Broker** | Redis |
| **AI Engine** | Alibaba DashScope (Qwen) |
| **Frontend** | Next.js 14 |
| **UI Library** | Tailwind CSS + shadcn/ui |

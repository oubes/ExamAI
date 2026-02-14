# 🎓 ExamAI — Intelligent Assessment & Feedback Ecosystem

<p align="center">

<img src="https://img.shields.io/badge/Timeline-Feb%202026%20--%20Present-blue?style=for-the-badge" />
<img src="https://img.shields.io/badge/Status-Active%20Development-success?style=for-the-badge" />
<img src="https://img.shields.io/badge/Architecture-Agentic%20AI-orange?style=for-the-badge" />

<br/>

<img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
<img src="https://img.shields.io/badge/LLMs-OpenAI%20Compatible-412991?style=for-the-badge&logo=openai&logoColor=white" />

<br/>

<img src="https://img.shields.io/badge/PostgreSQL-Relational%20DB-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" />
<img src="https://img.shields.io/badge/Vector%20DB-RAG%20Ready-yellow?style=for-the-badge" />
<img src="https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white" />

</p>

---

## 📌 Project Overview

**ExamAI** is an intelligent, end-to-end academic assessment ecosystem designed to **automate and enhance the entire examination lifecycle**.

By combining **Optical Character Recognition (OCR)**, **Generative AI**, and **Retrieval-Augmented Generation (RAG)**, the platform transforms traditional paper-based exams into structured, analyzable, and feedback-rich digital assets.

Unlike conventional assessment systems limited to MCQs, ExamAI supports **open-ended**, **analytical**, and **reasoning-based** answers while delivering **instant, explainable, and personalized feedback**.

---

## 🏗️ System Architecture & Workflow

ExamAI follows a **modular, agentic architecture**, where specialized AI components collaborate in a controlled workflow.

### 🔍 1. Ingestion & Document Understanding
- Accepts digital exam submissions and scanned handwritten sheets  
- OCR pipeline segments documents into **questions, sub-questions, and answers**  
- Text normalization and semantic cleanup ensure **high AI grading accuracy**

### 🧠 2. Rubric-Aware Automated Grading
- Semantic understanding agents evaluate **correctness, reasoning quality, and conceptual coverage**  
- Grading is aligned with **instructor-defined rubrics and policies**  
- Ensures **consistent and unbiased scoring at scale**

### 📚 3. RAG-Driven Personalized Feedback
- Uses a Vector Database to retrieve context such as:
  - Student historical performance
  - Previous misconceptions
  - Topic-level mastery trends
- Generates **context-aware, personalized feedback** per student

### 📊 4. Institutional-Level Analytics
- Aggregates insights at class, department, and institution levels  
- Provides dashboards and reports for:
  - Outcome-based tracking  
  - Performance gap analysis  
  - Curriculum evaluation and academic planning

---

## 🌟 Key Features

> **High-Fidelity OCR**  
> Accurate recognition of scanned and handwritten exams, structured into digital format.

> **Adaptive Assessment Logic**  
> Supports dynamic adjustment of exam difficulty and evaluation depth based on student performance.

> **Actionable AI Feedback**  
> Explainable feedback highlighting strengths, weaknesses, and targeted improvement steps.

> **Role-Based Dashboards**  
> Tailored interfaces for Students, Instructors, Administrators, and Institutions.

---

## 📂 Project Roadmap — MVP + Capability Expansion

<p align="center">

<img src="https://img.shields.io/badge/Phase%201-System%20Analysis-success?style=flat-square" />
<img src="https://img.shields.io/badge/Phase%202-System%20Architecture-blue?style=flat-square" />
<img src="https://img.shields.io/badge/Phase%203-First%20MVP-yellow?style=flat-square" />
<img src="https://img.shields.io/badge/Phase%204-Capability%20Expansion%20%231-orange?style=flat-square" />
<img src="https://img.shields.io/badge/Phase%205-Capability%20Expansion%20%232-red?style=flat-square" />
<img src="https://img.shields.io/badge/Phase%206-Capability%20Expansion%20%233-purple?style=flat-square" />
<img src="https://img.shields.io/badge/Phase%207-Pilot%20Deployment-lightblue?style=flat-square" />

</p>

---

### 🔹 Phase 1 — System Analysis
- Gather functional and non-functional requirements  
- Define user roles: Students, Instructors, Admins  
- Document workflows, edge cases, and constraints  
- Feasibility study for AI, OCR, and RAG integration  

### 🔹 Phase 2 — System Architecture
- Design **modular architecture** supporting agentic AI, RAG, and grading  
- Define **data flow**: Upload → OCR → AI → Feedback → Analytics  
- Plan API endpoints, DB models, service layers  
- Set up configuration management, logging, and security  

### 🔹 Phase 3 — First MVP
**Goal:** Minimal functional product for **1 digital subject/course**

- Process **full digital course/exam**  
- Detailed feedback for **each question/part**  
- Overall rubric/score based on **student’s history**  
- Minimal FastAPI app with config + Pydantic v2 models  
- Health check endpoint + manual grading fallback  
- Validate **end-to-end flow** on sample data  

### 🔹 Phase 4 — Capability Expansion #1
- Add support for **additional exam scenarios or question types**  
- Incorporate **tools or content** not in MVP  
- Extend grading to **new rubrics or scoring policies**  

### 🔹 Phase 5 — Capability Expansion #2
- Add **extra course materials or topics**  
- Handle **complex edge-case scenarios** in grading or feedback  
- Enhance dashboards or reporting per new use cases  

### 🔹 Phase 6 — Capability Expansion #3
- Integrate **optional tools/modules** for instructors (e.g., automated hints, analytics filters)  
- Extend system coverage to **advanced student interactions**  

### 🔹 Phase 7 — Pilot Deployment
- Deploy in **controlled academic environment**  
- Monitor system performance and grading accuracy  
- Collect **user feedback** and iterate  
- Prepare for **full-scale rollout**

---

## 🛠️ Technology Stack

- **Core Engine:** Python 3.10+  
- **API Layer:** FastAPI  
- **AI Layer:** LLMs for grading and feedback  
- **Databases:** PostgreSQL (relational) + Vector DB (RAG)  
- **Deployment:** Dockerized microservices  
- **MLOps:** Model versioning, monitoring, and evaluation pipelines  

---

## 📄 Documentation

Technical and functional documentation available in `/docs`:

- **System Analysis:** Functional and non-functional requirements  
- **Architecture:** Component interaction diagrams  
- **User Stories:** End-to-end usage scenarios for all roles  

---

## 🤝 Contributing

Contributions are welcome and highly appreciated.  
Whether improving documentation, system design, or experimental pipelines, your input helps push ExamAI forward.

---

## ⚖️ License

This project is licensed under the **MIT License**.  
See the `LICENSE` file for details.

---

**ExamAI** — *Redefining the Future of Academic Assessment.*

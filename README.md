# Indonesian Scientific Punctuation Checker

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Flask](https://img.shields.io/badge/Flask-3.1.3-black)
![License](https://img.shields.io/badge/License-MIT-green)

## 🚀 Key Features

- Rule-based punctuation detection based on EYD V
- Regular Expression and POS Tagging (Stanza)
- Automatic correction for DOCX scientific documents
- Background worker for asynchronous document processing

A web-based application for detecting and correcting Indonesian punctuation errors in scientific documents based on **EYD V (Ejaan Bahasa Indonesia Edisi Kelima)**. The system applies a rule-based approach using **Regular Expressions** and **Part-of-Speech (POS) Tagging** to identify punctuation errors and correct it automatically.

> This project was developed as the final project for the Diploma III Information Technology Program.

---

## 📄 Table of Contents

- Overview
- User Features
- Screenshots
- Tech Stack
- System Architecture
- Installation
- Project Structure
- Future Improvements
- License

---

## 📖 Overview

Scientific writing requires proper punctuation according to the Indonesian Spelling Guidelines (EYD V). However, punctuation errors remain common in academic documents and often require manual proofreading, especially in the use of:

- Period (.)
- Comma (,)
- Colon (:)
- Quotation Marks (" ")
- Hyphen (-)

This application helps users automatically detect and correct punctuation errors in DOCX scientific documents using a rule-based approach combined with Regular Expressions and POS Tagging.

---

## 🖼 Screenshots

### Upload Page

<img src="screenshots/upload.png" width="700">

### Document Processing Status

<img src="screenshots/document_processing.png" width="700">

### Detection & Correction Result

<img src="screenshots/detection_correction_result.png" width="700">

### Correction History (Authenticated Users)

<img src="screenshots/correction_history.png" width="700">

### About Application Page

<img src="screenshots/about_application.png" width="700">

---

## ✨ User Features

- Upload DOCX scientific documents
- Preview uploaded documents
- Track processing status
- Detect punctuation errors automatically
- View explanations for each detected error
- Correct punctuation errors automatically
- Download corrected documents
- View correction history (authenticated users)

---

## 🛠 Tech Stack

### Backend

- Python
- Flask
- Flask-SQLAlchemy
- Flask-Migrate

### Database

- MySQL
- PyMySQL

### NLP

- Stanza

### Document Processing

- python-docx

### Frontend

- HTML5
- CSS3
- JavaScript
- Jinja2 Templates

---

## 🏗 System Architecture

The application consists of several processing stages:

```text
DOCX Document
        │
        ▼
Text Extraction
        │
        ▼
Normalization
        │
        ▼
Sentence Segmentation
        │
        ▼
Tokenization
        │
        ▼
POS Tagging (Stanza)
        │
        ▼
Rule-Based Detection
        │
        ▼
Automatic Correction
        │
        ▼
Corrected Document
```

---

## 🚀 Installation

### 1. Clone repository

```bash
git clone https://github.com/selena2355/indonesian-punctuation-correction.git
cd indonesian-punctuation-correction
```

### 2. Create virtual environment

```bash
python -m venv .venv
```

### 3. Activate virtual environment

Windows

```bash
.venv\Scripts\activate
```

Linux / macOS

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Copy the example configuration file.

Windows

```powershell
copy .env.example .env
```

Linux / macOS

```bash
cp .env.example .env
```

Then edit the `.env` file according to your local environment.

Example configuration:

```env
SECRET_KEY=your-secret-key
DATABASE_URL=mysql+pymysql://username:password@localhost/database_name
```

### 6. Create Database

Create an empty MySQL database before running the migration.

For example:

```sql
CREATE DATABASE punctuation_checker;
```

Update the `DATABASE_URL` inside `.env`.

```env
DATABASE_URL=mysql+pymysql://username:password@localhost/punctuation_checker
```

### 7. Upgrade database

```bash
flask db upgrade
```

### 8. Start background worker

Open a terminal and run:

```bash
python worker.py
```

### 9. Start the web application

Open another terminal and run:

```bash
python app.py
```

---

## 📂 Project Structure

```text
.
├── app/
│   ├── controllers/     # Request handlers
│   ├── models/          # Database models
│   ├── routes/          # Application routes
│   ├── rules/           # Punctuation detection rules
│   ├── services/        # Core business logic
│   ├── static/          # CSS, JavaScript, images
│   ├── templates/       # Jinja2 templates
│   ├── utils/           # Utility functions
│   ├── config.py
│   ├── extensions.py
│   └── __init__.py
│
├── migrations/          # Flask-Migrate files
├── app.py               # Web application entry point
├── worker.py            # Background job worker
├── cleanup_jobs.py      # Cleanup expired jobs
├── requirements.txt
└── .env.example
```

---

## 📌 Future Improvements

- Support additional document formats (PDF, TXT)
- Improve detection accuracy by reducing false positives
- Expand punctuation rules based on future EYD revisions
- Optimize processing performance for large documents
- Support batch document processing

---

## 👩‍💻 Author

Hanifah Alya

Diploma III Information Technology

Politeknik Negeri Madiun

---

## 📄 License

This project is licensed under the MIT License.
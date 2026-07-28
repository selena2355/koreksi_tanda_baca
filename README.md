# Indonesian Scientific Punctuation Checker

A web-based application for detecting and correcting Indonesian punctuation errors in scientific documents based on **EYD V (Ejaan Bahasa Indonesia Edisi Kelima)**. The system applies a rule-based approach using **Regular Expressions** and **Part-of-Speech (POS) Tagging** to identify punctuation errors and provide correction suggestions.

> This project was developed as the final project for the Diploma III Information Technology Program.

---

## 📖 Overview

Writing scientific papers requires consistent punctuation according to the Indonesian spelling guidelines (EYD V). However, punctuation errors are still common, especially in the use of:

- Period (.)
- Comma (,)
- Colon (:)
- Quotation Marks (" ")
- Hyphen (-)

This application helps users automatically detect and correct those punctuation errors in DOCX documents.

---

## ✨ Features

- Upload scientific documents (.docx)
- Automatic document preprocessing
- Sentence segmentation
- Tokenization and POS Tagging using Stanza
- Rule-based punctuation error detection
- Error explanation for each detected issue
- Automatic punctuation correction
- Download corrected document
- Processing status using background worker

---

## 🖼 Screenshots

### Home Page

*(Insert screenshot here)*

---

### Detection Result

*(Insert screenshot here)*

---

### Correction Result

*(Insert screenshot here)*

---

## 🏗 System Architecture

The application consists of several processing stages:

1. Upload document
2. Text extraction
3. Text normalization
4. Sentence segmentation
5. Tokenization
6. POS Tagging (Stanza)
7. Rule-based punctuation detection
8. Automatic correction
9. Result generation

---

## 🛠 Tech Stack

### Backend

- Python
- Flask
- SQLAlchemy
- Flask-Migrate

### Database

- MySQL

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

## 📂 Project Structure

```
app/
│
├── controllers/
├── models/
├── routes/
├── rules/
├── services/
├── static/
├── templates/
├── utils/
├── __init__.py
├── config.py
├── extensions.py
│
migrations/
.env.example
.gitignore
README.md
app.py
cleanup_jobs.py
requirements.txt
worker.py
```

---

## 🚀 Installation

### 1. Clone repository

```bash
git clone https://github.com/USERNAME/indonesian-punctuation-checker.git
cd indonesian-punctuation-checker
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

### 5. Download Stanza model

```python
import stanza
stanza.download("id")
```

or

```bash
python download_stanza.py
```

*(Adjust according to your project.)*

### 6. Configure environment variables

Create a `.env` file.

Example:

```env
SECRET_KEY=your-secret-key

DATABASE_URL=mysql+pymysql://username:password@localhost/database_name

STANZA_DIR=models/stanza
```

---

### 7. Upgrade database

```bash
flask db upgrade
```

---

### 8. Start worker

```bash
python worker.py
```

---

### 9. Run application

```bash
flask run
```

---

## 📌 Future Improvements

- PDF document support
- Faster processing for large documents
- Additional punctuation rules
- REST API
- Batch document processing

---

## 👩‍💻 Author

Selena

Diploma III Information Technology

Politeknik Negeri Madiun

---

## 📄 License

This project is licensed under the MIT License.
# 🏛️ BICRS (Barangay / Campus Information & Retrieval System)

An integrated IT solution leveraging MySQL database management and Natural Language Processing (NLP) backend logic for efficient query resolution and structured information processing.

---

## 📌 Overview
The BICRS project aims to streamline localized data processing and information retrieval. Designed with a optimized relational database architecture, the system integrates Natural Language Processing (NLP) to parse user inputs, match relevant queries, and return prompt, accurate information.

---

## ✨ Key Features
* **Optimized MySQL Relational Database:** Designed with efficient indexing, custom schemas, and foreign keys to handle rapid data queries.
* **NLP Query Processing:** Parses user input strings using NLP backend logic to match keywords and extract intentional queries.
* **Structured Data Retrieval:** Ensures fast query-to-response generation for administrators and end-users.
* **Modular Backend Architecture:** Built for maintainability and easy integration with future modules or frontend interfaces.

---

## 🛠️ Tech Stack
* **Backend Language:** Python 
* **Database Management:** MySQL
* **NLP Integration:** Natural Language Processing Pipeline / Libraries
* **Tools Used:** VS Code, MySQL Workbench / phpMyAdmin

---

## 🗄️ Database Setup
1. Import the provided `.sql` file in the `/database` directory into your local MySQL server (e.g., via phpMyAdmin or MySQL Workbench).
2. Update your local environment settings or configuration files with your MySQL connection credentials:
   ```python
   DB_HOST = "localhost"
   DB_USER = "your_username"
   DB_PASSWORD = "your_password"
   DB_NAME = "bicrs_db"

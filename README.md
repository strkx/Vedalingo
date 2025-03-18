# VedaLingo - Sanskrit Tutor App

## Overview
**VedaLingo** is an interactive Sanskrit learning platform designed to provide an **AI-powered** and structured approach to mastering Sanskrit. It offers **real-time translations, guided lessons, and pronunciation assistance**, making Sanskrit learning accessible for everyone.

## Features
### 1. AI-Powered Sanskrit Translation
- Utilizes **Swami Tucat's M2M100_Sanskrit_English model** for Sanskrit to English translation.
- **GROQ/Llama-3.3-70b-versatile** for **Sanskrit to Hindi** and **contextual English translation**.

### 2. Interactive Learning Modules
- **Grammar Lessons**: Covers Sanskrit syntax and rules.
- **Vocabulary Builder**: Helps users expand their word bank.
- **Practice Exercises**: Includes quizzes and interactive activities.

### 3. Speech & Pronunciation Assistance
- Supports **speech-to-text input** for practice.
- Provides **audio feedback** for correct pronunciation.

### 4. User-Friendly Interface
- Modern UI with **React frontend**.
- Seamless backend communication via **FastAPI**.

## Tech Stack
| Component | Technology |
|-----------|------------|
| **Backend** | FastAPI (Python) |
| **Frontend** | React (TypeScript) |
| **LLM Models** | Swami Tucat's M2M100, GROQ/Llama-3.3-70b-versatile |
| **Speech Processing** | WebRTC & Speech-to-Text APIs |
| **Database** | PostgreSQL |

## Installation & Setup
### 1. Clone the Repository
```bash
git clone https://github.com/your-username/VedaLingo.git
cd VedaLingo
```
### 2. Backend Setup (FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
### 3. Frontend Setup (React)
```bash
cd frontend
npm install
npm start
```

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/translate/sanskrit-english` | Translates Sanskrit to English. |
| `POST` | `/api/translate/sanskrit-hindi` | Translates Sanskrit to Hindi. |
| `POST` | `/api/grammar-check` | Provides feedback on Sanskrit grammar. |
| `POST` | `/api/audio-feedback` | Returns pronunciation feedback. |

## Contributing
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-name`).
3. Commit changes (`git commit -m 'Added feature XYZ'`).
4. Push to the branch (`git push origin feature-name`).
5. Open a Pull Request.

## License
This project is licensed under the MIT License.

## Contact
For queries and collaboration, contact **[Umair Malim]** at **malimumair2@gmail.com**.


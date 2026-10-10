# 🎬 Trionix — AI-Powered Semantic Video Search & Retrieval Engine (RAG)

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.1-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Qdrant](https://img.shields.io/badge/Qdrant-Vector%20DB-DC382D?style=for-the-badge&logo=qdrant&logoColor=white)](https://qdrant.tech/)
[![AssemblyAI](https://img.shields.io/badge/AssemblyAI-Speech%20to%20Text-0052FF?style=for-the-badge)](https://www.assemblyai.com/)
[![HuggingFace](https://img.shields.io/badge/Sentence--Transformers-all--MiniLM--L6--v2-FFA800?style=for-the-badge&logo=huggingface&logoColor=white)](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Jenkins](https://img.shields.io/badge/Jenkins-CI%2FCD-D24939?style=for-the-badge&logo=jenkins&logoColor=white)](https://www.jenkins.io/)

> **Trionix** is an end-to-end semantic video indexing and retrieval engine. It converts long-form multimedia content into searchable vector embeddings, enabling users to query video libraries with natural language and jump directly to the exact second a topic is discussed.

---

## 📌 Problem & Motivation

Video content is rich with information, but searching through it is notoriously inefficient. Traditional video platforms rely on surface-level keyword metadata (titles, tags, and user descriptions) or require manual scrubbing through hours of video.

**Trionix solves this by:**
1. Ingesting arbitrary YouTube or uploaded audio/video streams.
2. Generating high-fidelity transcripts with millisecond-accurate timestamps using AI speech recognition.
3. Partitioning transcripts into semantic segments and encoding them with dense transformer embeddings.
4. Performing Approximate Nearest Neighbor (ANN) vector search via **Qdrant Vector Database** to return relevant answers ranked by cosine similarity.
5. Providing an interactive web UI where search results deep-link straight to the matching timestamp in an embedded video player.

---

## 🌟 Key Features

* **🧠 Semantic Video Search (RAG Pipeline):** Ask natural language questions (e.g., *"When is gradient descent explained?"*) and get pinpointed moments rather than simple keyword matches.
* **⏱️ Timestamp-Synchronized Video Playback:** Search results include confidence scores and clickable timestamps that automatically jump the embedded YouTube player to the exact moment.
* **🎙️ Speech-to-Text with Punctuation & Alignment:** Powered by **AssemblyAI** for robust, multi-speaker, and acoustically resilient transcription.
* **⚡ Vector Search Engine (Qdrant):** Dense vectors indexed in Qdrant with Cosine distance metric for sub-second retrieval across large transcript segments.
* **📥 Media Extraction Suite:** Built-in tools for YouTube video downloading, audio stream separation, and format conversion using `yt-dlp`, `moviepy`, and `pydub`.
* **📷 Computer Vision / Utility Modules:** Real-time QR Code scanning and URL content classification via OpenCV and `pyzbar`.
* **🐳 Production-Ready DevOps:** Containerized with Docker and Docker Compose, backed by an automated Jenkins CI/CD pipeline building and publishing to Azure Container Registry (ACR).

---

## 🏗️ Architecture & Data Pipeline

```text
+-----------------------------------------------------------------------------------------+
|                                1. INGESTION & INDEXING                                  |
+-----------------------------------------------------------------------------------------+
       YouTube / Video URL
               │
               ▼
      [ yt-dlp Extractor ] ──► Audio Track (MoviePy / PyDub)
                                       │
                                       ▼
                         [ AssemblyAI Speech-to-Text ]
                                       │
                                       ▼
                         [ Timestamped Segment Parser ]
                           (Start / End Milliseconds)
                                       │
                                       ▼
                         [ Sentence-Transformers Embedder ]
                           (all-MiniLM-L6-v2 • 384-dim)
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │   Qdrant Vector Database  │
                         │   (Cosine Metric Index)   │
                         └─────────────┬─────────────┘
                                       │
+--------------------------------------┼--------------------------------------------------+
|                              2. RETRIEVAL (RAG)                                         |
+--------------------------------------┼--------------------------------------------------+
       User Natural Language Query     │
               │                       │
               ▼                       │
     [ Query Embedding Engine ]        │
               │                       │
               ▼                       ▼
      [ Approximate Nearest Neighbor (ANN) Vector Search ]
               │
               ▼
      [ Ranked Timestamped Results + Similarity Scores ]
               │
               ▼
      [ Interactive Django UI: One-Click Seek to Exact Moment ]
```

---

## 🛠️ Tech Stack

| Domain | Technologies & Libraries |
| :--- | :--- |
| **Backend Framework** | Python 3.10+, Django 5.1 |
| **Speech & Audio** | AssemblyAI API, MoviePy, PyDub, SpeechRecognition |
| **NLP & Embeddings** | Sentence-Transformers (`all-MiniLM-L6-v2`), Scikit-learn, NumPy |
| **Vector Database** | Qdrant (`qdrant-client`), Cosine Metric |
| **Media Extraction** | `yt-dlp`, Requests |
| **Computer Vision** | OpenCV (`cv2`), PyZbar |
| **DevOps & Cloud** | Docker, Docker Compose, Jenkins CI/CD, Azure Container Registry (ACR) |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript, Django Template Engine |

---

## 📂 Project Structure

```plaintext
website/
├── .env                              # Local environment secrets (excluded from Git)
├── .gitignore                        # Git ignore patterns
├── Dockerfile                        # Multi-stage container build with system dependencies
├── docker-compose.yml                # Multi-container orchestration (Qdrant + Web)
├── Jenkinsfile                       # CI/CD pipeline for Azure Container Registry (ACR)
├── requirements.txt                  # Python dependencies
├── QR.py                             # OpenCV & PyZbar QR code scanner utility
├── project_6_trionix/                # Core Django Application
│   ├── manage.py                     # Django CLI
│   ├── project_6_trionix/            # Project configuration
│   │   ├── settings.py               # Django settings
│   │   ├── urls.py                   # Route definitions
│   │   ├── views.py                  # Controllers for search, index, download, and auth
│   │   └── static/                   # Static CSS assets and images
│   ├── python_scripts/               # Core AI & Search Pipeline
│   │   ├── all_con.py                # Pipeline controller coordinating ingest, index & query
│   │   ├── extract_audio.py          # AssemblyAI transcription & timestamp segmenter
│   │   ├── vector_embedding.py       # SentenceTransformer embedding & search logic
│   │   ├── qdrant_store.py           # Qdrant client connection & collection management
│   │   └── youtube_downv3.py         # YouTube stream downloader using yt-dlp
│   └── src/                          # HTML5 UI Templates
│       ├── youtube_trans.html        # Main ingestion portal (Schematic Query)
│       ├── query.html                # Interactive search interface & video player
│       ├── youtube_downloader.html   # Dedicated video download portal
│       ├── audio_down.html           # Dedicated audio download portal
│       ├── loader.html               # Asynchronous processing indicator
│       └── login/                    # Authentication views (Login & Register)
```

---

## 🚀 Getting Started

### Prerequisites

* **Python 3.10+**
* **Docker & Docker Compose** (for running Qdrant)
* **FFmpeg** installed on your system (or use the provided Docker container)
* **AssemblyAI API Key** ([Get a free key here](https://www.assemblyai.com/))

---

### 1. Clone the Repository

```bash
git clone https://github.com/menonkrishna57/trionix.git
cd trionix/website
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root:

```env
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=trionix-transcripts
EMBEDDING_DIM=384
```

---

### 3. Start the Qdrant Vector Database

Using Docker Compose to launch Qdrant:

```bash
docker-compose up -d qdrant
```

Verify Qdrant is running by visiting the web dashboard: [http://localhost:6333/dashboard](http://localhost:6333/dashboard)

---

### 4. Run Locally (Virtual Environment)

```bash
# Create and activate virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
cd project_6_trionix
python manage.py migrate

# Start the Django development server
python manage.py runserver
```

Open your browser and navigate to **`http://localhost:8000/`**.

---

### 5. Run with Docker (Full Stack)

To build and run the entire application containerized:

```bash
# Build the Docker image
docker build -t trionix-app:latest .

# Run the container linked to host network
docker run -p 8000:8000 --env-file .env trionix-app:latest
```

---

## 💻 How It Works (Step-by-Step)

1. **Ingest Video:**
   * Navigate to the home page (`/`) and paste any YouTube video link.
   * Click **Query**. Trionix downloads the audio track and submits it to AssemblyAI.
2. **Indexing:**
   * Sentences are aligned with their start/end timestamps.
   * `all-MiniLM-L6-v2` encodes each chunk into a 384-dimensional vector.
   * Points containing vector embeddings and timestamp payloads are upserted into Qdrant.
3. **Ask & Navigate:**
   * Enter natural language queries into the search bar (e.g., *"What is reinforcement learning?"*).
   * The top matches are returned with cosine similarity scores.
   * Clicking **Start at mm:ss** seeks the synchronized YouTube player directly to that segment.

---

## 🔄 CI/CD & Deployment

The repository includes a production-ready **Jenkinsfile** implementing automated continuous integration and delivery:

* **Stage 1 (Checkout):** Pulls latest commits from GitHub upon trigger.
* **Stage 2 (Build):** Compiles the containerized application using `Dockerfile`.
* **Stage 3 (Push):** Authenticates and pushes tagged images to **Azure Container Registry (ACR)** for downstream deployment.

---

## 📈 Engineering Highlights for Recruiters

* **RAG on Time-Series Media:** Applied Retrieval-Augmented Generation concepts to non-text media by combining speech processing, temporal alignment, and dense vector search.
* **Vector Database Integration:** Architectured resilient fallback connection strategies and collection lifecycle management in Qdrant.
* **Production Observability:** Integrated structured logging across the indexing and querying pipeline for performance and latency tracking.
* **Containerized Workflows:** Handled non-trivial native system dependencies (`ffmpeg`, `libzbar0`) inside Docker builds for consistent multi-environment runtime.

---

## 📜 License

This project is open-source and available under the [MIT License](LICENSE).

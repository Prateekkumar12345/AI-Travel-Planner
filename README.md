# 🌍 AI-Powered Travel Planner Assistant ✈️

An intelligent travel planning assistant that uses advanced AI tools (Groq LLM, SerpAPI, Sentence Transformers, FAISS, and Gradio) to generate **personalized travel itineraries**, recommend **attractions**, **hotels**, **restaurants**, and answer any travel-related queries with visual highlights.

---

## 🚀 Features

✅ Create detailed, day-by-day **custom travel itineraries**  
✅ Use **RAG (Retrieval-Augmented Generation)** to answer natural language travel questions  
✅ View top **attractions**, **restaurants**, and **hotels** with real-time data  
✅ Access **Wikipedia overviews** and **Google Images** via SerpAPI  
✅ Intelligent **semantic search** using `SentenceTransformer + FAISS`  
✅ User-friendly **Gradio web interface**  

---

## 🧠 Powered By

- 🧬 `groq.mixtral-8x7b-32768` – Groq's lightning-fast LLM API
- 🔍 [SerpAPI](https://serpapi.com/) – Search engine scraping for hotels, restaurants, and images
- 🧠 [SentenceTransformers](https://www.sbert.net/) – For dense vector encoding
- 🔎 [FAISS](https://github.com/facebookresearch/faiss) – Fast similarity search
- 🎨 [Gradio](https://gradio.app/) – UI interface
- 📚 [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) – Wikipedia parsing

---

## 🧱 Project Structure

travel_planner/
├── travel_planner.py # Main logic (retrieval, LLM generation, UI)
├── requirements.txt # Dependencies
├── README.md # You are here
└── .env # Store API keys (optional)


---

## 🔐 API Keys Required

- 🧠 **Groq API Key**  
  Sign up: https://console.groq.com/

- 🔎 **SerpAPI Key**  
  Get free credits: https://serpapi.com/users/sign_up

Set them as environment variables or directly in code:
```bash
export GROQ_API_KEY="your-groq-key"
export SERPAPI_KEY="your-serpapi-key"

git clone https://github.com/your-username/ai-travel-planner.git
cd ai-travel-planner

pip install -r requirements.txt
pip install faiss-cpu

```
# How TO RUN

python travel_planner.py


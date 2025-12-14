# 🏥 Health Compass

An AI-powered health literacy platform that helps people understand medical information through evidence-based explanations from trusted sources.

> **⚠️ IMPORTANT:** Health Compass provides educational information only. It is NOT a substitute for professional medical advice, diagnosis, or treatment.

## 🎯 Project Overview

Health Compass uses Retrieval-Augmented Generation (RAG) to provide accurate, source-backed health information by:
- Searching trusted medical sources (MedlinePlus, CDC, WHO)
- Retrieving relevant information using semantic search
- Generating clear, educational explanations
- Citing all sources for transparency

### Key Features

✅ **Evidence-Based Information** - All responses backed by trusted medical sources  
✅ **Safety First** - Emergency detection system for critical symptoms  
✅ **Source Transparency** - Clear citations from government health organizations  
✅ **Plain Language** - Complex medical information explained simply  
✅ **100% Free** - No paid APIs or subscriptions required  

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **LLM:** OpenRouter (Llama 3.2 - FREE)
- **Vector Database:** ChromaDB (local, free)
- **Embeddings:** sentence-transformers (local, free)
- **Data Sources:** MedlinePlus, CDC, WHO, NHS

## 📋 Prerequisites

- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended)
- Internet connection for data collection
- OpenRouter API key (free - get from https://openrouter.ai/)

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/health-compass.git
cd health-compass
```

### 2. Set Up Environment
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure API Key

Create a `.env` file in the project root:
```bash
OPENROUTER_API_KEY=sk-or-v1-your-key-here
SITE_URL=https://github.com/yourusername/health-compass
SITE_NAME=Health Compass
```

Get your free OpenRouter API key from: https://openrouter.ai/

### 4. Run Data Pipeline (One-Time Setup)
```bash
python run_pipeline.py
```

This will:
- Scrape health information from trusted sources (~10-15 minutes)
- Process and clean the data
- Build the vector database
- Test the system

### 5. Launch Application
```bash
streamlit run src/app.py
```

The app will open in your browser at `http://localhost:8501`

## 📁 Project Structure
```
health-compass/
├── data/
│   ├── raw/              # Scraped data
│   ├── processed/        # Cleaned data
│   └── chroma_db/        # Vector database
├── src/
│   ├── scrapers/         # Web scraping modules
│   ├── processors/       # Data processing
│   ├── rag/              # RAG system
│   ├── utils/            # Utilities
│   └── app.py            # Streamlit app
├── .env                  # API keys (create this)
├── .gitignore
├── requirements.txt
├── run_pipeline.py       # Setup script
└── README.md
```

## 💡 Usage Examples

### Good Questions:
- "What is type 2 diabetes?"
- "How does ibuprofen work?"
- "What are symptoms of dehydration?"
- "Explain high blood pressure"
- "What is an MRI scan?"

### Emergency Symptoms:
The system automatically detects emergency symptoms and displays immediate care instructions:
- Chest pain
- Difficulty breathing
- Stroke symptoms
- Severe bleeding
- Suicidal thoughts

## 🔒 Safety Features

1. **Emergency Detection** - Automatically identifies life-threatening symptoms
2. **Source Verification** - All information cited from trusted medical organizations
3. **Clear Disclaimers** - Prominent reminders to consult healthcare professionals
4. **No Diagnosis** - System explicitly avoids providing medical diagnoses

## 🧪 Testing
```bash
# Test individual components
python -m src.rag.openrouter_client  # Test LLM connection
python -m src.rag.vector_db          # Test vector database
python -m src.rag.rag_pipeline       # Test complete RAG system
python -m src.utils.safety           # Test safety checker
```

## 📊 Data Sources

All information is sourced from:
- **MedlinePlus** - U.S. National Library of Medicine
- **CDC** - Centers for Disease Control and Prevention
- **WHO** - World Health Organization
- **NHS** - UK National Health Service

## 🎥 Demo Video

[Link to YouTube demo video]

## 🤝 Contributing

This is an academic project for INFO 7390. Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## ⚠️ Disclaimer

**MEDICAL DISCLAIMER:**

Health Compass provides educational information only. It is NOT:
- A substitute for professional medical advice, diagnosis, or treatment
- Capable of diagnosing medical conditions
- A replacement for consultation with qualified healthcare providers
- Appropriate for medical emergencies

**Always consult qualified healthcare professionals for medical concerns.**  
**For emergencies, call 911 immediately.**

## 👨‍💻 Author

Manish - Northeastern University  
Master's in Information Systems  
INFO 7390 - Advanced Data Science and Architecture

## 🙏 Acknowledgments

- OpenRouter for free LLM access
- Anthropic for Claude assistance
- Trusted medical organizations for public health information
- INFO 7390 course staff

## 📞 Support

For questions or issues:
- Open a GitHub issue
- Email: [your-email]@northeastern.edu

---

Built with ❤️ for health literacy and education
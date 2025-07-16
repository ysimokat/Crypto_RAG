# 🧠 ArgumentRx - Retrieval-Augmented Argumentation System

ArgumentRx is an AI-powered system that generates fact-based, pro/con arguments on controversial or complex topics by retrieving real-time evidence from free internet sources. It combines state-of-the-art retrieval techniques with large language models (LLMs) to mimic human-style critical thinking.

## 🌟 Features

- **Real-time Source Retrieval**: Automatically gathers evidence from news APIs, Reddit, and crypto research sources
- **Structured Argument Generation**: Creates logically sound, stance-based arguments using retrieved content
- **Built-in Evaluation**: Scores argument strength using rule-based logic and optional LLM feedback
- **Source Transparency**: Shows all sources and evidence clearly for responsible AI use
- **Interactive Web Interface**: Streamlit-based UI for easy interaction
- **Export Capabilities**: Save results as JSON or generate transparency reports

## 🚀 Quick Start

### 1. Installation

```bash
git clone https://github.com/ysimokat/Crypto_RAG.git
cd Crypto_RAG
pip install -r requirements.txt
```

### 2. Configuration

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
# Edit .env with your API keys
```

Required API keys (optional but recommended):
- `OPENAI_API_KEY`: For GPT-based argument generation
- `REDDIT_CLIENT_ID` & `REDDIT_CLIENT_SECRET`: For Reddit content retrieval
- `NEWS_API_KEY`: For news article retrieval

### 3. Usage Options

#### Web Interface (Recommended)
```bash
streamlit run streamlit_app.py
```

#### Command Line Interface
```bash
python src/argumentrx.py "Bitcoin environmental impact"
python src/argumentrx.py "DeFi regulation" --save results.json --transparency
```

#### Python API
```python
from src.argumentrx import ArgumentRx

argumentrx = ArgumentRx()
results = argumentrx.generate_arguments("Proof of Work vs Proof of Stake")
print(results)
```

## 📁 Project Structure

```
Crypto_RAG/
├── src/
│   ├── argumentrx.py          # Main ArgumentRx class
│   ├── retrieval.py           # Data retrieval from various sources
│   ├── embeddings.py          # Text embedding and similarity search
│   ├── argument_generator.py  # LLM-based argument generation
│   └── evaluator.py          # Argument quality evaluation
├── streamlit_app.py           # Web interface
├── example_usage.py           # Usage examples
├── config.py                  # Configuration settings
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🛠️ Core Components

### 1. Data Retrieval (`retrieval.py`)
- **NewsRetriever**: Fetches articles from news APIs
- **RedditRetriever**: Searches relevant subreddits
- **CryptoBlogRetriever**: Gathers content from crypto news sites
- **UnifiedRetriever**: Coordinates all retrieval sources

### 2. Embedding Management (`embeddings.py`)
- Uses sentence transformers for text embedding
- FAISS-based similarity search for relevant source selection
- Persistent index storage and loading

### 3. Argument Generation (`argument_generator.py`)
- **ArgumentGenerator**: OpenAI GPT-based generation
- **LocalLLMGenerator**: Local model support (HuggingFace)
- Structured pro/con argument creation with citations

### 4. Evaluation System (`evaluator.py`)
- Rule-based scoring (clarity, logic, evidence, persuasiveness)
- Optional LLM-based evaluation for enhanced feedback
- Combined scoring methodology

## 📊 Evaluation Metrics

Arguments are scored on four dimensions:

- **Clarity (0.0-1.0)**: How clear and understandable the argument is
- **Logic (0.0-1.0)**: Logical structure and reasoning flow
- **Evidence (0.0-1.0)**: Use of citations and factual support
- **Persuasiveness (0.0-1.0)**: Convincing power and rhetorical effectiveness

## 🎯 Use Cases

- **Crypto Research**: Analyze pros/cons of tokens, protocols, or regulations
- **Debate Preparation**: Train students to see multiple perspectives
- **Policy Analysis**: Summarize opposing viewpoints on laws and governance
- **Research Assistant**: Demonstrate transparent reasoning systems

## 📋 Example Output

```json
{
  "topic": "Bitcoin environmental impact",
  "arguments": {
    "pro": {
      "content": "Bitcoin mining drives renewable energy adoption...",
      "evaluation": {
        "overall_score": 0.75,
        "clarity": 0.8,
        "logic": 0.7,
        "evidence": 0.8,
        "persuasiveness": 0.7
      },
      "citations": ["[1] Energy consumption study - coindesk.com"]
    },
    "con": {
      "content": "Bitcoin's energy consumption exceeds many countries...",
      "evaluation": {
        "overall_score": 0.82,
        "clarity": 0.85,
        "logic": 0.8,
        "evidence": 0.85,
        "persuasiveness": 0.78
      }
    }
  },
  "metadata": {
    "total_sources_retrieved": 25,
    "sources_used": 10,
    "model_used": "OpenAI"
  }
}
```

## 🔧 Configuration

Key settings in `config.py`:

- `EMBEDDING_MODEL`: Sentence transformer model for embeddings
- `LLM_MODEL`: Language model for argument generation
- `RETRIEVAL_TOP_K`: Number of sources to use for arguments
- `MAX_SOURCES_PER_ARGUMENT`: Maximum citations per argument
- `ARGUMENT_MAX_LENGTH`: Maximum argument length in words

## 🧪 Examples

Run the example script to see ArgumentRx in action:

```bash
python example_usage.py
```

This demonstrates:
- Basic argument generation
- File output and transparency reports
- Multiple topic analysis
- Evaluation breakdowns

## ⚡ GPU Support

The system automatically detects and uses GPU when available:
- Embedding models run on GPU for faster processing
- Local LLM generation utilizes GPU acceleration
- For optimal performance, install: `pip install faiss-gpu`

## 🚨 Limitations

- Requires internet connection for source retrieval
- API rate limits may affect performance
- Local LLM quality depends on model choice
- Source availability varies by topic

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built with HuggingFace Transformers, OpenAI API, and FAISS
- Inspired by retrieval-augmented generation research
- Uses public APIs for news, Reddit, and crypto content

---

**Note**: This system is designed for educational and research purposes. Always verify information from multiple sources and consider the limitations of AI-generated content.
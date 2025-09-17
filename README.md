# RestaurantLens (AI-Powered Customer Feedback Analyzer)

Analyze customer reviews at scale with an easy, interactive UI. This project focuses on **sentiment analysis** and **multilingual support**, and includes example data and setup scripts to help you get running quickly. The app supports batch analysis from CSV files and provides fast iteration for experiments and demos. :contentReference[oaicite:0]{index=0}

---

## ✨ Features

- **Multilingual analysis**: end-to-end flow tailored for non-English input (see `app_multilingual2.py` and setup scripts). :contentReference[oaicite:1]{index=1}  
- **Sentiment pipeline**: scripts to prepare and validate the sentiment model and resources. :contentReference[oaicite:2]{index=2}  
- **Batch input**: analyze multiple reviews from the included `reviews.csv`. :contentReference[oaicite:3]{index=3}  
- **Multi-page UI**: organized app pages for a cleaner experience (see `pages/`). :contentReference[oaicite:4]{index=4}

> **Tech stack:** Python (100%). The repository is primarily Python code. :contentReference[oaicite:5]{index=5}

---

## 🗂️ Repository Structure

| File/Folder             | Description                                        |
|--------------------------|----------------------------------------------------|
| `assets/`               | Static assets (images, icons, etc.)                |
| `data/`                 | (Optional) extra datasets or artifacts             |
| `pages/`                | Multi-page app subpages                            |
| `venv/`                 | Local virtual environment (not required)           |
| `app_multilingual2.py`  | Main application entry point                        |
| `requirements.txt`      | Python dependencies                                |
| `reviews.csv`           | Sample input data (customer reviews)               |
| `setup_multilingual.py` | Helper: download/setup multilingual resources      |
| `setup_sentiment.py`    | Helper: prepare sentiment resources/models         |
| `test_sentiment.py`     | Basic tests for sentiment pipeline                 |


(See the repo file listing for the current contents.)

---

## 🚀 Quickstart

### 1) Prerequisites
- Python 3.9+ recommended
- macOS, Linux, or Windows

### 2) Clone
```bash
git clone https://github.com/AsmiiGaurav/AI-Powered-Customer-Feedback-Analyzer.git
cd AI-Powered-Customer-Feedback-Analyzer
```

### 3) Setup Virtual Enviornment

python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate

### 4) Install Dependencies

pip install --upgrade pip
pip install -r requirements.txt

5) One-time resource setup (recommended)

Some analyses require language models/corpora.
# Multilingual resources (tokenizers, language data, etc.)
python setup_multilingual.py

# Sentiment resources/models

python setup_sentiment.py

### 6) Run the app
   
streamlit run app_multilingual2.py

###  Input Data

Use the included reviews.csv as a starting point to test the pipeline.
You can replace it with your own CSV containing a column of free-text reviews.

## Sentiment Analysis Score Explanation

The format you're seeing: **Overall Sentiment: Positive (0.93) [pos: 0.72, neg: 0.00, neu: 0.28]** represents two different types of scores from the sentiment analysis system:

### 1. Overall Sentiment Score (0.93)
- **What it is**: The final confidence score for the predicted sentiment label
- **How it's calculated**: This comes from the hybrid method that combines multiple sentiment analysis approaches:
  - VADER (40% weight)
  - TextBlob (30% weight) 
  - Transformer model (30% weight)
- **Range**: 0.0 to 1.0 (higher = more confident)
- **Purpose**: Indicates how confident the system is in its "Positive" prediction

### 2. Component Scores [pos: 0.72, neg: 0.00, neu: 0.28]
- **What they are**: Raw sentiment component scores from the underlying models (primarily VADER)
- **pos: 0.72**: Proportion of positive sentiment detected
- **neg: 0.00**: Proportion of negative sentiment detected  
- **neu: 0.28**: Proportion of neutral sentiment detected
- **Range**: Each component is 0.0 to 1.0, and they typically sum to 1.0

### Why the Difference?
The overall confidence (0.93) is **higher** than the positive component (0.72) because:

1. **Different Calculation Methods**: 
   - Overall confidence uses weighted voting across multiple models
   - Component scores come from individual model outputs (mainly VADER)

2. **Confidence Boosting**: 
   - When multiple models agree on "Positive", the system becomes more confident
   - The hybrid approach amplifies confidence when there's consensus

3. **Mathematical Transformation**:
   - The final confidence may be calculated using compound scores or weighted averages
   - This can result in higher confidence than individual components

### Example Breakdown:
- **Text Analysis**: "This restaurant is amazing!" 
- **VADER says**: 72% positive, 0% negative, 28% neutral
- **TextBlob agrees**: Positive sentiment
- **Transformer agrees**: Positive sentiment
- **Final Result**: 93% confident it's positive (because all methods agree)

This dual scoring system provides both granular component analysis and a robust overall prediction confidence.
### CSV Tips

Keep a header row (e.g., review).
Ensure your file is UTF-8 encoded for multilingual text.

### Testing

Run basic tests (if you’ve installed pytest):
pytest -k sentiment -q

### Acknowledgments

Thanks to the open-source Python ecosystem and NLP tooling that make rapid prototyping of multilingual sentiment analysis possible.





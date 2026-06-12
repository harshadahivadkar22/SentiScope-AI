# SentiScope AI — Advanced Sentiment Analytics Dashboard

SentiScope AI is a modern, responsive, and secure web application designed to perform high-fidelity sentiment analysis on user interactions. Built with Flask and powered by the TextBlob natural language processing engine, SentiScope AI classifies text data as Positive, Negative, or Neutral, and supplements this with advanced analytical insights, real-time interactive charts, and data export features.

Designed with a premium glassmorphic dark interface, the application is optimized for speed, accessibility (WCAG-compliant), and robust thread safety (especially under Windows environments).

---

## 🚀 Key Features

* **Real-Time Sentiment Classification**: Evaluates input text immediately, returning descriptive polarity (emotional direction) and subjectivity (factual vs. opinionated) scores.
* **Advanced NLP Insights**:
  * *Emotion Strength Indicator*: Computes sentiment intensity from polarity magnitudes and subjectivity.
  * *Confidence Scoring*: Assesses reliability based on grammatical length and word density rules.
  * *Sentiment Trend Tracking*: Dynamically compares submissions against a rolling average of past analyses.
  * *Context Recommendations*: Suggests customer service actions tailored to current sentiments.
* **Interactive Dashboard**:
  * Glassmorphic design variables with animated circular SVG score gauges.
  * Live-updating Matplotlib frequency distribution bar graphs and pie charts.
  * Accessible Sidebar Transaction Log: Keyboard-navigable logs with relative timestamp meters and instant metric reloading.
* **Report Exports**: Downloads records in CSV formats (for spreadsheet software) or TXT files (containing visual frequency statistics summaries).
* **Enterprise Concurrency & Security**:
  * Full thread synchronization via resource-specific locks to prevent file-locking conflicts (`WinError 32` on Windows).
  * Strict directory traversal protection and whitelists on file serving routes.
  * Safe exception handlers guarding against stack trace information disclosure.
  * Native HTTP security header configurations (Content-Security-Policy, X-Frame-Options, X-Content-Type-Options).

---

## 🛠️ Technology Stack

* **Backend**: Flask 3.0.3 (Python 3.10+)
* **Natural Language Processing**: TextBlob 0.18.0 (NLTK Tokenizers)
* **Data Visualization**: Matplotlib 3.10.9 (Non-interactive `Agg` Backend)
* **Frontend**: Vanilla HTML5, CSS3 Custom Properties (variables, responsive grids), and modern JavaScript (Asynchronous ES6 fetch API)
* **Database**: Local JSON-based flat file system with concurrent synchronization locks

---

## 📂 Folder Structure

```
SentiScope-AI/
├── .env                       # Local environment variables configuration
├── .gitignore                 # Files and folder exclusions for git commits
├── app.py                     # Central controller (Flask routes, Locks, Serves charts/exports)
├── config.py                  # Directory mapping and environment configs initializers
├── requirements.txt           # Unified python system dependencies
│
├── services/
│   └── sentiment_service.py   # TextBlob wrapper and NLP analysis algorithm
│
├── templates/
│   └── index.html             # High-fidelity dashboard structure (A11y/WCAG focus points)
│
├── static/
│   ├── css/
│   │   └── style.css          # Glassmorphic themes, responsive grids, and visual states
│   └── js/
│       └── script.js          # Unified controller (AJAX, gauges redraw, keyboard handlers)
│
├── memory/
│   └── analysis_history.json  # Synchronized JSON database
│
├── charts/                    # Matplotlib-generated output (Pie / Bar charts)
└── exports/                   # Downloadable TXT & CSV report buffers
```

---

## 📥 Installation Steps

Ensure you have Python 3.10+ installed on your system.

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/harshadahivadkar22/SentiScope-AI.git
   cd SentiScope-AI
   ```

2. **Set up a Virtual Environment**:
   ```bash
   # On Windows
   python -m venv .venv
   .venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install System Dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Verify Environment Configurations**:
   Create a `.env` file in the root directory (based on the default configuration):
   ```ini
   FLASK_ENV=development
   SECRET_KEY=your-secure-fallback-development-key-1234
   PORT=5000
   ```

5. **Run the Application**:
   ```bash
   python app.py
   ```
   Open your browser and navigate to `http://127.0.0.1:5000`.

---

## 💻 Usage Instructions

1. **Submit Text**: Type or paste customer support tickets, emails, or review text into the **Analysis Console** and click **Analyze Sentiment** (or press `Ctrl + Enter`).
2. **Review Metrics**: Inspect the circular score gauges showing Polarity/Subjectivity, the Advanced Insights panel, and the recommendation flags.
3. **Compare History**: Click on any past card in the **Recent Analyses** list. Keyboard-only users can navigate cards using the `Tab` key and load them by pressing `Enter` or `Space`.
4. **Export Reports**: Once records exist in history, click **Export CSV** to download raw tables or **Export TXT** to download visual summary charts summaries.
5. **Wipe Logs**: Click **Clear History** to purge all storage files and reset the dashboard.

---

## 📊 Screenshots Section

*Placeholder for SentiScope AI dashboard layouts:*

```
┌──────────────────────────────────────────────────────────────────┐
│  SentiScope AI   [Recent Analyses]        [Analysis Console]     │
│  ─────────────   ┌──────────────┐         ┌────────────────────┐ │
│  4 records       │ 2m ago       │         │ Great product!     │ │
│                  │ POSITIVE     │         └────────────────────┘ │
│                  ├──────────────┤         [ Analyze Sentiment ]  │
│                  │ Just now     │                                │
│                  │ NEUTRAL      │         [Sentiment Result]     │
│                  └──────────────┘         ┌────────────────────┐ │
│                                           │ POSITIVE           │ │
│                                           └────────────────────┘ │
│  [Export CSV] [Export TXT] [Clear Logs]   [Polarity]   [Subject] │
│                                           │  +0.75   │ │  0.80   │ │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔮 Future Enhancements

* **Multi-Language Support**: Integrate translation layers to analyze reviews in French, Spanish, German, and Chinese.
* **Batch Analytics Upload**: Allow users to drag and drop bulk spreadsheets (Excel/CSV) for automated batch processing.
* **Real-time API Webhook integrations**: Forward negative sentiment records directly to support desks (e.g., Zendesk, Jira).
* **Deep Learning Model Option**: Implement a toggle to switch between TextBlob (lexicon-based) and a fine-tuned Transformer model (e.g., RoBERTa) for nuanced classification.

---

## ✍️ Author Information

Developed with care by **Harsha Dahivadkar**

* **GitHub**: [@harshadahivadkar22](https://github.com/harshadahivadkar22)
* **Repository URL**: [https://github.com/harshadahivadkar22/SentiScope-AI](https://github.com/harshadahivadkar22/SentiScope-AI)

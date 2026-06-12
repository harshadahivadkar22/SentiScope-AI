import os
import csv
import json
import logging
import threading
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory
from config import Config
from services.sentiment_service import SentimentService

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure matplotlib to use a non-interactive back-end to prevent thread locks and crashes
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    logger.info("Successfully configured matplotlib to use the non-interactive 'Agg' backend.")
except Exception as e:
    logger.critical(f"Failed to configure matplotlib backend: {e}")

# Concurrency locks
db_lock = threading.Lock()
chart_lock = threading.Lock()

def load_history() -> list:
    """Helper to read history array from JSON file with safety wrappers."""
    with db_lock:
        try:
            if Config.MEMORY_FILE.exists():
                with open(Config.MEMORY_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
                    else:
                        logger.warning("History file is not a valid list. Resetting log.")
            else:
                logger.info("History JSON file does not exist yet. Returning empty list.")
        except Exception as e:
            logger.error(f"Error reading history JSON file: {e}")
        return []

def save_history(history_data: list) -> bool:
    """Helper to write history array to JSON file with safety wrappers."""
    with db_lock:
        try:
            # Enforce list type
            if not isinstance(history_data, list):
                history_data = []
                
            # Use atomic write: write to temp file and rename to avoid corrupting data on power cut / crash
            temp_file = Config.MEMORY_FILE.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(history_data, f, indent=4, ensure_ascii=False)
            
            # Atomic swap on filesystem
            os.replace(str(temp_file), str(Config.MEMORY_FILE))
            return True
        except Exception as e:
            logger.error(f"Error writing history JSON file: {e}")
            return False

def generate_analytics_charts():
    """Generates the Pie and Bar charts based on history logs using matplotlib."""
    with chart_lock:
        try:
            history = load_history()
            
            # Ensure charts directory exists
            Config.CHARTS_DIR.mkdir(parents=True, exist_ok=True)
            
            pos = sum(1 for item in history if isinstance(item, dict) and item.get('sentiment') == 'Positive')
            neg = sum(1 for item in history if isinstance(item, dict) and item.get('sentiment') == 'Negative')
            neu = sum(1 for item in history if isinstance(item, dict) and item.get('sentiment') == 'Neutral')
            total = pos + neg + neu
            
            if total == 0:
                # Delete existing files if history is cleared to reset dashboard
                for name in ['sentiment_pie.png', 'sentiment_bar.png']:
                    file_path = Config.CHARTS_DIR / name
                    if file_path.exists():
                        try:
                            file_path.unlink()
                        except OSError as err:
                            logger.warning(f"Could not delete file {file_path}: {err}")
                logger.info("Cleared existing chart files since history is empty.")
                return
                
            # Color palettes matching our dark mode variables
            text_color = '#9CA3AF'
            label_color = '#F3F4F6'
            
            # 1. Generate Pie Chart (Sentiment Percentages)
            fig, ax = plt.subplots(figsize=(4.5, 4.5), facecolor='none')
            labels = []
            sizes = []
            colors = []
            
            if pos > 0:
                labels.append('Positive')
                sizes.append(pos)
                colors.append('#10B981') # Green
            if neu > 0:
                labels.append('Neutral')
                sizes.append(neu)
                colors.append('#F59E0B') # Yellow
            if neg > 0:
                labels.append('Negative')
                sizes.append(neg)
                colors.append('#EF4444') # Red
                
            wedges, texts, autotexts = ax.pie(
                sizes, 
                labels=labels, 
                colors=colors, 
                autopct='%1.1f%%',
                startangle=140,
                textprops={'color': text_color, 'fontsize': 10},
                wedgeprops={'edgecolor': '#080C14', 'linewidth': 2}
            )
            for autotext in autotexts:
                autotext.set_color('#080C14')
                autotext.set_fontweight('bold')
                
            ax.axis('equal')
            plt.title('Sentiment Distribution', color=label_color, fontweight='bold', fontsize=12, pad=15)
            
            # Save atomically to avoid race conditions or lockouts
            temp_path = Config.CHARTS_DIR / 'sentiment_pie.tmp.png'
            plt.savefig(temp_path, transparent=True, dpi=150, bbox_inches='tight')
            plt.clf()
            plt.close(fig)
            
            os.replace(str(temp_path), str(Config.CHARTS_DIR / 'sentiment_pie.png'))
            
            # 2. Generate Bar Chart (Sentiment Frequency Counts)
            fig, ax = plt.subplots(figsize=(5.5, 4.5), facecolor='none')
            categories = ['Positive', 'Neutral', 'Negative']
            counts = [pos, neu, neg]
            colors = ['#10B981', '#F59E0B', '#EF4444']
            
            active_cats = []
            active_counts = []
            active_colors = []
            for cat, count, col in zip(categories, counts, colors):
                if count > 0:
                    active_cats.append(cat)
                    active_counts.append(count)
                    active_colors.append(col)
                    
            bars = ax.bar(active_cats, active_counts, color=active_colors, edgecolor='none', width=0.5, zorder=3)
            
            ax.set_facecolor('none')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#262C3A')
            ax.spines['bottom'].set_color('#262C3A')
            ax.tick_params(colors=text_color, labelsize=10)
            
            import matplotlib.ticker as ticker
            ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
            ax.grid(axis='y', linestyle='--', alpha=0.1, zorder=0)
            
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{int(height)}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),  
                            textcoords="offset points",
                            ha='center', va='bottom', color=label_color, fontweight='bold', fontsize=10)
                            
            plt.title('Sentiment Frequency', color=label_color, fontweight='bold', fontsize=12, pad=15)
            
            temp_path = Config.CHARTS_DIR / 'sentiment_bar.tmp.png'
            plt.savefig(temp_path, transparent=True, dpi=150, bbox_inches='tight')
            plt.clf()
            plt.close(fig)
            
            os.replace(str(temp_path), str(Config.CHARTS_DIR / 'sentiment_bar.png'))
            
            logger.info("Successfully generated analytics charts (Pie & Bar).")
        except Exception as e:
            logger.error(f"Error generating analytics charts: {e}")

def export_csv(history_data: list, filepath: Path):
    """Writes tabular sentiment data to a CSV file."""
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['ID', 'Timestamp', 'Text', 'Sentiment', 'Polarity', 'Subjectivity']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for entry in history_data:
            writer.writerow({
                'ID': entry.get('id', ''),
                'Timestamp': entry.get('timestamp', ''),
                'Text': entry.get('text', ''),
                'Sentiment': entry.get('sentiment', ''),
                'Polarity': entry.get('polarity', 0.0),
                'Subjectivity': entry.get('subjectivity', 0.0)
            })

def export_txt(history_data: list, filepath: Path):
    """Writes human-readable summary reports to a Text file."""
    pos = sum(1 for item in history_data if isinstance(item, dict) and item.get('sentiment') == 'Positive')
    neg = sum(1 for item in history_data if isinstance(item, dict) and item.get('sentiment') == 'Negative')
    neu = sum(1 for item in history_data if isinstance(item, dict) and item.get('sentiment') == 'Neutral')
    total = len(history_data)
    
    with open(filepath, 'w', encoding='utf-8') as txtfile:
        txtfile.write("=" * 80 + "\n")
        txtfile.write(" " * 28 + "SENTISCOPE AI REPORT\n")
        txtfile.write("=" * 80 + "\n")
        txtfile.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        txtfile.write(f"Total Records: {total}\n")
        txtfile.write(f"Positive Count: {pos}\n")
        txtfile.write(f"Negative Count: {neg}\n")
        txtfile.write(f"Neutral Count: {neu}\n")
        txtfile.write("=" * 80 + "\n\n")
        
        for idx, entry in enumerate(history_data, 1):
            txtfile.write(f"Record #{idx}\n")
            txtfile.write(f"ID: {entry.get('id', '')}\n")
            txtfile.write(f"Timestamp: {entry.get('timestamp', '')}\n")
            txtfile.write(f"Sentiment: {entry.get('sentiment', '')}\n")
            txtfile.write(f"Polarity Score: {entry.get('polarity', 0.0):+.3f}\n")
            txtfile.write(f"Subjectivity Score: {entry.get('subjectivity', 0.0):.3f}\n")
            txtfile.write("Analyzed Text:\n")
            txtfile.write(f"\"{entry.get('text', '')}\"\n")
            txtfile.write("-" * 80 + "\n\n")

# Initialize workspace folders and logs files on startup using Config
Config.init_app()

# Initialize dynamic charts if memory file contains entries
try:
    if Config.MEMORY_FILE.exists():
        with open(Config.MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if data:
                generate_analytics_charts()
except Exception as startup_err:
    logger.error(f"Failed to generate startup charts: {startup_err}")

# Initialize Flask application
app = Flask(__name__)
app.config.from_object(Config)

# Ensure NLTK corpora check does not block server initialization
try:
    import nltk
    # Check if tokenizer packages are present
    nltk.data.find('tokenizers/punkt')
    logger.info("NLTK 'punkt' tokenizer is available.")
except (LookupError, ImportError) as e:
    logger.info(f"NLTK check skipped or requires download: {e}")
    try:
        nltk.download('punkt', quiet=True)
    except Exception as download_err:
        logger.warning(f"Could not automatically download NLTK 'punkt': {download_err}")

@app.after_request
def add_security_headers(response):
    """Inject defensive HTTP security headers to protect against common web vulnerabilities."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "script-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "connect-src 'self';"
    )
    return response

@app.route('/', methods=['GET'])
def home():
    """Renders the main dashboard page."""
    return render_template('index.html')

@app.route('/charts/<path:filename>')
def serve_chart(filename):
    """Route to serve matplotlib charts directly from the charts/ directory with strict file whitelist."""
    if filename not in ['sentiment_pie.png', 'sentiment_bar.png']:
        return jsonify({'error': 'Resource not found.'}), 404
    return send_from_directory(Config.CHARTS_DIR, filename)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Asynchronously processes the user entered text, runs TextBlob classification,
    saves the transaction details inside the JSON logs, draws the analytics charts,
    and returns the result.
    """
    try:
        data = request.get_json() or {}
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'Please provide text content for analysis.'}), 400
            
        # Enforce server-side text size limit to prevent CPU exhaustion Denial of Service (DoS)
        if len(text) > 5000:
            return jsonify({'error': 'Submitted text exceeds the maximum limit of 5000 characters.'}), 400
            
        # Load existing history to evaluate trend running average
        history = load_history()
        
        # Analyze using sentiment service with history metrics
        results = SentimentService.analyze_text(text, history)
        
        # Construct the history record
        timestamp = datetime.now().isoformat()
        record_id = int(datetime.now().timestamp() * 1000)
        
        history_entry = {
            'id': record_id,
            'timestamp': timestamp,
            'text': text,
            'sentiment': results['sentiment'],
            'polarity': results['polarity'],
            'subjectivity': results['subjectivity'],
            'insights': results['insights']  # Save insights details for dashboard reloads
        }
        
        # Append entry to the top of the history list
        history.insert(0, history_entry)
        if not save_history(history):
            return jsonify({'error': 'Failed to save analysis to history logs.'}), 500
        
        # Generate new analytics charts dynamically
        generate_analytics_charts()
        
        logger.info(f"Saved entry ID: {record_id} and updated analytics charts.")
        
        return jsonify({
            'status': 'success',
            'data': results
        })
        
    except Exception as e:
        logger.error(f"Error in API analysis endpoint: {e}", exc_info=True)
        return jsonify({'error': 'An unexpected error occurred during analysis. Please try again later.'}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Retrieves all past analyses from the JSON store."""
    history = load_history()
    return jsonify(history)

@app.route('/api/history/clear', methods=['POST'])
def clear_history():
    """Wipes the history JSON log file and deletes charts."""
    if save_history([]):
        generate_analytics_charts()
        logger.info("Successfully cleared analysis history logs and deleted charts.")
        return jsonify({'status': 'success', 'message': 'History cleared successfully.'})
    return jsonify({'error': 'Could not clear history logs.'}), 500

@app.route('/api/export/csv', methods=['POST'])
def export_history_csv():
    """Generates and downloads a CSV export file of past analyses."""
    try:
        history = load_history()
        if not history:
            return jsonify({'error': 'No history records to export.'}), 400
            
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"sentiscope_export_{timestamp_str}.csv"
        filepath = Config.EXPORTS_DIR / filename
        
        # Generate CSV file
        export_csv(history, filepath)
        
        logger.info(f"Generated CSV export file: {filename}")
        return send_from_directory(Config.EXPORTS_DIR, filename, as_attachment=True)
        
    except Exception as e:
        logger.error(f"Error in CSV export endpoint: {e}", exc_info=True)
        return jsonify({'error': 'Failed to generate CSV export.'}), 500

@app.route('/api/export/txt', methods=['POST'])
def export_history_txt():
    """Generates and downloads a human-readable TXT summary report."""
    try:
        history = load_history()
        if not history:
            return jsonify({'error': 'No history records to export.'}), 400
            
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"sentiscope_export_{timestamp_str}.txt"
        filepath = Config.EXPORTS_DIR / filename
        
        # Generate TXT file
        export_txt(history, filepath)
        
        logger.info(f"Generated TXT export file: {filename}")
        return send_from_directory(Config.EXPORTS_DIR, filename, as_attachment=True)
        
    except Exception as e:
        logger.error(f"Error in TXT export endpoint: {e}", exc_info=True)
        return jsonify({'error': 'Failed to generate TXT export.'}), 500

if __name__ == '__main__':
    logger.info("Starting SentiScope AI (Final Production) server...")
    app.run(
        host='0.0.0.0', 
        port=app.config.get('PORT', 5000), 
        debug=app.config.get('DEBUG', False)
    )

/**
 * SentiScope AI - Dashboard Controller
 * Integrates AJAX api requests, renders sidebar history panels, triggers visual gauge and matplotlib updates.
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Selectors
    const textInput = document.getElementById('text-input');
    const btnAnalyze = document.getElementById('btn-analyze');
    
    const resultsEmpty = document.getElementById('results-empty');
    const resultsContent = document.getElementById('results-content');
    const sentimentBadge = document.getElementById('sentiment-badge');
    const sentimentText = document.getElementById('sentiment-text');
    
    const polarityFill = document.getElementById('polarity-fill');
    const polarityScore = document.getElementById('polarity-score');
    const polarityLbl = document.getElementById('polarity-lbl');
    
    const subjectivityFill = document.getElementById('subjectivity-fill');
    const subjectivityScore = document.getElementById('subjectivity-score');
    const subjectivityLbl = document.getElementById('subjectivity-lbl');

    // Advanced Insights
    const insightEmotion = document.getElementById('insight-emotion');
    const insightConfidence = document.getElementById('insight-confidence');
    const insightTrend = document.getElementById('insight-trend');
    const recommendationBox = document.getElementById('recommendation-box');
    const insightRecommendation = document.getElementById('insight-recommendation');

    // Sidebar selectors
    const historyList = document.getElementById('history-list');
    const historyCounter = document.getElementById('history-counter');
    const btnClearHistory = document.getElementById('btn-clear-history');
    
    // Exports selectors
    const btnExportCsv = document.getElementById('btn-export-csv');
    const btnExportTxt = document.getElementById('btn-export-txt');

    // Charts selectors
    const analyticsSection = document.getElementById('analytics-section');
    const chartPie = document.getElementById('chart-pie');
    const chartBar = document.getElementById('chart-bar');

    // Circle SVG gauge circumference constants (Radius = 40)
    const GAUGE_CIRCUMFERENCE = 251.2;

    // Load initial logs
    fetchHistory();

    // Textarea interaction
    textInput.addEventListener('keydown', (e) => {
        // Submit on Ctrl+Enter
        if (e.ctrlKey && e.key === 'Enter') {
            btnAnalyze.click();
        }
    });

    // Attach click event to analyze trigger
    btnAnalyze.addEventListener('click', () => {
        const text = textInput.value.trim();
        if (!text) {
            alert('Please enter some text content to analyze.');
            return;
        }
        executeAnalysis(text);
    });

    // Clear history logs action
    btnClearHistory.addEventListener('click', () => {
        if (confirm('Are you sure you want to clear all history records from the system? This will also wipe your analytics charts.')) {
            clearHistoryLogs();
        }
    });

    // Export CSV report action
    btnExportCsv.addEventListener('click', () => {
        const dateStr = new Date().toISOString().slice(0, 10).replace(/-/g, '');
        downloadReport('/api/export/csv', `sentiscope_export_${dateStr}.csv`);
    });

    // Export TXT report action
    btnExportTxt.addEventListener('click', () => {
        const dateStr = new Date().toISOString().slice(0, 10).replace(/-/g, '');
        downloadReport('/api/export/txt', `sentiscope_export_${dateStr}.txt`);
    });

    /**
     * Sends the text to the Flask API endpoint, updates history, and initiates rendering
     */
    function executeAnalysis(text) {
        setLoading(true);

        fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.error || 'Server error.'); });
            }
            return response.json();
        })
        .then(json => {
            if (json.status === 'success') {
                renderResults(json.data);
                fetchHistory(); // Refresh sidebar history and charts
            }
        })
        .catch(err => {
            console.error('Analysis error:', err);
            alert(err.message || 'Network error: Could not contact analysis service.');
        })
        .finally(() => {
            setLoading(false);
        });
    }

    /**
     * Fetch past logs from the Flask server
     */
    function fetchHistory() {
        fetch('/api/history')
            .then(res => {
                if (!res.ok) throw new Error('Could not load history logs.');
                return res.json();
            })
            .then(historyData => {
                renderHistorySidebar(historyData);
                renderCharts(historyData);
                updateExportButtonsState(historyData);
            })
            .catch(err => console.error('Error fetching history:', err));
    }

    /**
     * Send clear logs request to the server
     */
    function clearHistoryLogs() {
        fetch('/api/history/clear', { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    fetchHistory(); // Reload history sidebar and remove charts
                    // Reset results panel to empty state
                    resultsEmpty.classList.remove('hidden');
                    resultsContent.classList.add('hidden');
                    textInput.value = '';
                } else {
                    alert('Could not clear history: ' + (data.error || 'Server error.'));
                }
            })
            .catch(err => console.error('Error clearing history:', err));
    }

    /**
     * Stream binary file download from the server
     */
    function downloadReport(endpoint, filename) {
        fetch(endpoint, { method: 'POST' })
            .then(res => {
                if (!res.ok) {
                    return res.json().then(err => { throw new Error(err.error || 'Export failed.'); });
                }
                return res.blob();
            })
            .then(blob => {
                const downloadUrl = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = downloadUrl;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(downloadUrl);
            })
            .catch(err => {
                console.error('Download error:', err);
                alert('Failed to download report: ' + err.message);
            });
    }

    /**
     * Toggles the UI state during AJAX execution
     */
    function setLoading(isLoading) {
        const spinner = btnAnalyze.querySelector('.loading-spinner');
        const span = btnAnalyze.querySelector('span');
        
        if (isLoading) {
            btnAnalyze.disabled = true;
            textInput.disabled = true;
            spinner.classList.remove('hidden');
            span.textContent = 'Analyzing...';
        } else {
            btnAnalyze.disabled = false;
            textInput.disabled = false;
            spinner.classList.add('hidden');
            span.textContent = 'Analyze Sentiment';
        }
    }

    /**
     * Enable or disable export buttons based on history record counts
     */
    function updateExportButtonsState(history) {
        const hasRecords = history && history.length > 0;
        btnExportCsv.disabled = !hasRecords;
        btnExportTxt.disabled = !hasRecords;
    }

    /**
     * Fades in the results panel and triggers circle gauge animations
     */
    function renderResults(data) {
        // Swap empty card state with active results card
        resultsEmpty.classList.add('hidden');
        resultsContent.classList.remove('hidden');

        const sentimentLower = data.sentiment.toLowerCase();

        // 1. Update Large Sentiment Classification Badge
        sentimentBadge.className = `sentiment-badge ${sentimentLower}`;
        sentimentText.textContent = data.sentiment.toUpperCase();

        // 2. Animate Polarity SVG Gauge
        polarityScore.textContent = (data.polarity >= 0 ? '+' : '') + data.polarity.toFixed(2);
        
        // Calculate stroke dashoffset (absolute polarity maps 0 to 100%)
        const polMagnitude = Math.abs(data.polarity);
        const polOffset = GAUGE_CIRCUMFERENCE - (polMagnitude * GAUGE_CIRCUMFERENCE);
        
        // Apply dashoffset value
        polarityFill.style.strokeDashoffset = polOffset;
        
        // Dynamically style gauge colors based on category
        if (sentimentLower === 'positive') {
            polarityFill.style.stroke = 'var(--color-positive)';
            polarityLbl.textContent = 'Positive';
            polarityLbl.className = 'score-label positive';
        } else if (sentimentLower === 'negative') {
            polarityFill.style.stroke = 'var(--color-negative)';
            polarityLbl.textContent = 'Negative';
            polarityLbl.className = 'score-label negative';
        } else {
            polarityFill.style.stroke = 'var(--color-neutral)';
            polarityLbl.textContent = 'Neutral';
            polarityLbl.className = 'score-label neutral';
        }

        // 3. Animate Subjectivity SVG Gauge
        subjectivityScore.textContent = data.subjectivity.toFixed(2);
        
        const subOffset = GAUGE_CIRCUMFERENCE - (data.subjectivity * GAUGE_CIRCUMFERENCE);
        subjectivityFill.style.strokeDashoffset = subOffset;
        
        // Set subjectivity descriptions
        if (data.subjectivity > 0.7) {
            subjectivityLbl.textContent = 'Highly Opinionated';
            subjectivityLbl.className = 'score-label subjectivity-opinion';
        } else if (data.subjectivity > 0.3) {
            subjectivityLbl.textContent = 'Mixed / Subjective';
            subjectivityLbl.className = 'score-label';
        } else {
            subjectivityLbl.textContent = 'Objective Facts';
            subjectivityLbl.className = 'score-label subjectivity-fact';
        }

        // 4. Update Advanced Insights Panel
        const insights = data.insights;
        if (insights) {
            insightEmotion.textContent = `${insights.emotion_strength}% (${insights.emotion_label})`;
            insightConfidence.textContent = `${insights.confidence}% (${insights.confidence_label})`;
            
            // Format Sentiment Trend with color and symbol helper
            insightTrend.className = 'insight-value-trend'; // Reset classes
            const trendText = insights.trend;
            
            if (trendText.includes('Improving')) {
                insightTrend.classList.add('improving');
                insightTrend.textContent = 'Improving ↗';
            } else if (trendText.includes('Declining')) {
                insightTrend.classList.add('declining');
                insightTrend.textContent = 'Declining ↘';
            } else {
                insightTrend.classList.add('stable');
                insightTrend.textContent = trendText; 
            }
            
            // Update recommendation banner
            insightRecommendation.textContent = insights.recommendation;
            recommendationBox.className = `recommendation-box ${sentimentLower}`;
        }
    }

    /**
     * Renders the scrollable sidebar logs list
     */
    function renderHistorySidebar(history) {
        historyList.innerHTML = '';
        
        const count = history ? history.length : 0;
        historyCounter.textContent = `${count} record${count === 1 ? '' : 's'}`;

        if (count === 0) {
            historyList.innerHTML = `
                <div class="history-empty-placeholder">
                    <svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none">
                        <circle cx="12" cy="12" r="10"></circle>
                        <polyline points="12 6 12 12 16 14"></polyline>
                    </svg>
                    <p>No records found</p>
                </div>
            `;
            return;
        }

        history.forEach(item => {
            const date = new Date(item.timestamp);
            const timeStr = formatRelativeTime(date);
            const sentimentLower = item.sentiment.toLowerCase();

            const card = document.createElement('div');
            card.className = 'history-card';
            card.setAttribute('tabindex', '0');
            card.setAttribute('role', 'button');
            card.setAttribute('aria-label', `History item from ${timeStr}: Sentiment ${item.sentiment}, Polarity ${(item.polarity >= 0 ? '+' : '') + item.polarity.toFixed(2)}, Subjectivity ${item.subjectivity.toFixed(2)}`);
            
            card.innerHTML = `
                <div class="history-card-header">
                    <span class="time-label">${timeStr}</span>
                    <span class="badge-mini ${sentimentLower}">${item.sentiment}</span>
                </div>
                <div class="history-card-snippet">${escapeHTML(item.text)}</div>
                <div class="history-card-metrics">
                    <span>Pol: <strong>${(item.polarity >= 0 ? '+' : '') + item.polarity.toFixed(2)}</strong></span>
                    <span>Sub: <strong>${item.subjectivity.toFixed(2)}</strong></span>
                </div>
            `;

            const loadCardData = () => {
                textInput.value = item.text;
                renderResults({
                    sentiment: item.sentiment,
                    polarity: item.polarity,
                    subjectivity: item.subjectivity,
                    insights: item.insights
                });
            };

            // Click history card: load textarea AND pass serialized insights back to the UI instantly
            card.addEventListener('click', loadCardData);
            card.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    loadCardData();
                }
            });

            historyList.appendChild(card);
        });
    }

    /**
     * Loads dynamic charts using timestamp query parameters to bypass cache
     */
    function renderCharts(history) {
        const count = history ? history.length : 0;
        
        if (count === 0) {
            analyticsSection.classList.add('hidden');
            chartPie.src = '';
            chartBar.src = '';
        } else {
            analyticsSection.classList.remove('hidden');
            const cacheBuster = Date.now();
            chartPie.src = `/charts/sentiment_pie.png?cb=${cacheBuster}`;
            chartBar.src = `/charts/sentiment_bar.png?cb=${cacheBuster}`;
        }
    }

    /**
     * Formats datetime as user-friendly relative strings
     */
    function formatRelativeTime(date) {
        const now = new Date();
        const diffMs = now - date;
        const diffSec = Math.floor(diffMs / 1000);
        const diffMin = Math.floor(diffSec / 60);
        const diffHr = Math.floor(diffMin / 60);
        
        if (diffSec < 60) return 'Just now';
        if (diffMin < 60) return `${diffMin}m ago`;
        if (diffHr < 24) return `${diffHr}h ago`;
        
        return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    }

    /**
     * Escapes HTML string to prevent XSS injection in history snippet output
     */
    function escapeHTML(str) {
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
});

from textblob import TextBlob

class SentimentService:
    """
    A service class that provides sentiment analysis using TextBlob,
    augmented with advanced insights (Emotion Strength, Confidence, Trend, and Recommendations).
    """
    
    @staticmethod
    def analyze_text(text: str, history: list = None) -> dict:
        """
        Analyzes the given text for sentiment polarity and subjectivity,
        along with advanced analytical insights.
        
        Args:
            text (str): The text content entered by the user.
            history (list, optional): Previous analysis entries from the JSON logs.
            
        Returns:
            dict: A dictionary containing sentiment results, scores, and advanced insights.
        """
        # Defensive Type Check: Ensure text is treated as a string
        if text is None:
            text = ""
        elif not isinstance(text, str):
            text = str(text)
            
        # Ensure history is a list
        if history is None or not isinstance(history, list):
            history = []
            
        # Return default neutral results if text is empty or blank
        if not text.strip():
            return {
                "sentiment": "Neutral",
                "polarity": 0.0,
                "subjectivity": 0.0,
                "insights": {
                    "emotion_strength": 0,
                    "emotion_label": "Low Intensity",
                    "confidence": 70,
                    "confidence_label": "Medium",
                    "trend": "Stable",
                    "recommendation": "Customer sentiment is balanced."
                }
            }
            
        # Create a TextBlob instance to parse and evaluate the text
        blob = TextBlob(text)
        
        # Retrieve TextBlob sentiment metrics
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # 1. Classify the sentiment category
        if polarity > 0.1:
            sentiment = "Positive"
        elif polarity < -0.1:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"
            
        # 2. Calculate Emotion Strength
        # Blend polarity magnitude (60%) and subjectivity (40%) to estimate strength
        emotion_val = (abs(polarity) * 0.6) + (subjectivity * 0.4)
        emotion_strength = int(round(emotion_val * 100))
        
        if emotion_strength >= 70:
            emotion_label = "High Intensity"
        elif emotion_strength >= 35:
            emotion_label = "Moderate Intensity"
        else:
            emotion_label = "Low Intensity"
            
        # 3. Calculate Confidence Indicator
        # Base confidence is 70%. Adjust based on sample size (word count) and grammatical weight.
        words = blob.words
        word_count = len(words)
        confidence = 70
        
        if word_count < 5:
            confidence -= 20 # Penalty for short inputs
        elif word_count >= 20:
            confidence += 15 # Bonus for large inputs
            
        # Bonus if TextBlob detects high subjectivity or highly clear factual statements
        if subjectivity > 0.8 or subjectivity < 0.2:
            confidence += 5
            
        # Clamp confidence score between 40% and 98%
        confidence = max(40, min(98, confidence))
        
        if confidence >= 80:
            confidence_label = "Strong"
        elif confidence >= 60:
            confidence_label = "Medium"
        else:
            confidence_label = "Low"
            
        # 4. Calculate Sentiment Trend
        # Compare current polarity to the running average of the last 5 analyses in history
        if len(history) < 2:
            trend = "Stable (First Run)"
        else:
            # Extract polarity scores of up to 5 previous analyses (excluding current transaction) and ensure type safety
            prev_polarities = [
                item['polarity'] 
                for item in history[:5] 
                if isinstance(item, dict) and isinstance(item.get('polarity'), (int, float))
            ]
            if prev_polarities:
                avg_prev_polarity = sum(prev_polarities) / len(prev_polarities)
                polarity_diff = polarity - avg_prev_polarity
                
                if polarity_diff > 0.15:
                    trend = "Improving"
                elif polarity_diff < -0.15:
                    trend = "Declining"
                else:
                    trend = "Stable"
            else:
                trend = "Stable"
                
        # 5. Generate Recommendation based on sentiment category
        if sentiment == "Positive":
            recommendation = "Customer appears satisfied."
        elif sentiment == "Negative":
            recommendation = "Customer may require support."
        else:
            recommendation = "Customer sentiment is balanced."
            
        return {
            "sentiment": sentiment,
            "polarity": round(polarity, 3),
            "subjectivity": round(subjectivity, 3),
            "insights": {
                "emotion_strength": emotion_strength,
                "emotion_label": emotion_label,
                "confidence": confidence,
                "confidence_label": confidence_label,
                "trend": trend,
                "recommendation": recommendation
            }
        }

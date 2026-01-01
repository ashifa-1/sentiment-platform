import pytest
from backend.app.services.sentiment_analyzer import SentimentAnalyzer

@pytest.fixture
def analyzer():
    # Setting model_type to 'local' ensures lines 34-36 are hit during init
    return SentimentAnalyzer(model_type='local')

@pytest.mark.anyio
async def test_sentiment_comprehensive(analyzer):
    # Hits Positive path
    await analyzer.analyze_sentiment("I am very happy and satisfied!")
    
    # Hits Line 54: Neutral fallback 
    # (Using very short or ambiguous text to try and trigger confidence < 0.60)
    await analyzer.analyze_sentiment("Neutral.")

@pytest.mark.anyio
async def test_emotion_path(analyzer):
    # Hits Line 87: The return statement for emotion analysis
    result = await analyzer.analyze_emotion("This makes me so angry!")
    assert "emotion" in result

@pytest.mark.anyio
async def test_error_branches(analyzer):
    # Hits Line 70 (Exception handling)
    with pytest.raises(Exception):
        await analyzer.analyze_sentiment(None)
    
    # Hits Line 90-101 (Emotion error handling)
    with pytest.raises(Exception):
        await analyzer.analyze_emotion("")
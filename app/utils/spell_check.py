import requests
import json

# This is the same URL the old libraries were using.
NAVER_SPELL_CHECKER_URL = "https://m.search.naver.com/p/csearch/ocontent/util/SpellerProxy"

def check_spelling(text: str) -> str:
    """
    Checks the spelling of a given text using Naver's unofficial API.
    Handles long texts by splitting them.
    Includes error handling for API changes.
    """
    if not text or not isinstance(text, str):
        return text

    # Naver API has a 500 character limit.
    if len(text) > 500:
        # Simple split by sentences. A more robust method might be needed for complex texts.
        sentences = text.replace('\n', ' ').split('. ')
        corrected_sentences = [check_spelling(sentence) for sentence in sentences if sentence]
        return '. '.join(corrected_sentences)

    params = {
        'where': 'nexearch',
        'color_blindness': 0,
        'q': text
    }

    try:
        response = requests.get(NAVER_SPELL_CHECKER_URL, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        # The old library used `eval`, which is unsafe. We use `response.json()`
        data = response.json()

        # The KeyError indicated the 'result' key was missing.
        # We access the corrected HTML path safely with .get()
        result = data.get('message', {}).get('result', {})
        corrected_html = result.get('html', '')
        
        # A simple way to extract text from the HTML response
        import re
        corrected_text = re.sub(r'<.*?>', '', corrected_html)
        
        return corrected_text if corrected_text else text

    except (requests.exceptions.RequestException, json.JSONDecodeError, KeyError, AttributeError) as e:
        print(f"[Spell Check Error] An error occurred: {e}")
        print(f"[Spell Check Error] Raw response from Naver: {response.text if 'response' in locals() else 'No response'}")
        # If spell checking fails for any reason, return the original text.
        return text

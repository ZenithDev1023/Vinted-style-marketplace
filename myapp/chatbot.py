import os
import pandas as pd
import random
import re
import json
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from django.conf import settings

# Absolute path to the JSON script, resolved relative to Django's BASE_DIR
SCRIPT_PATH = os.path.join(settings.BASE_DIR, 'myapp', 'static', 'chatbot', 'chatbotscript.json')

# Load the tags dataframe once at module level so it isn't re-read on every request
_tags_df = None

# Helper function to load the tags dataframe (with caching)
def _get_tags_df():
    global _tags_df
    if _tags_df is None:
        _tags_df = load_file(SCRIPT_PATH)
    return _tags_df

# Function to load the JSON file and convert it to a DataFrame. 
def load_file(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    tags_df = pd.DataFrame(data['Tags'])
    return tags_df

# Function to save conversation turns to a text file for logging purposes
def save_conversation(user_sentence, bot_response):
    """Append a conversation turn to chatdata.txt inside BASE_DIR."""
    filepath = os.path.join(settings.BASE_DIR, 'chatdata.txt')
    with open(filepath, 'a') as f:
        f.write(f'Timestamp: {pd.Timestamp.now()}\n')
        f.write(f'User: {user_sentence}\n')
        f.write(f'Bot: {bot_response}\n')
        f.write('\n')

# Function to expand response templates with captured variables and memory
def expand_response_template(response, captured_groups, memory=None):
    # Find all placeholders in the response string in form {placeholder}
    placeholders = re.findall(r'\{(\w+)\}', response)
    
    # Create combined dictionary with current captures and memory
    all_vars = captured_groups.copy()
    
    # Add memory variables (last_name, last_stressor, etc.)
    if memory:
        for key, value in memory.items():
            all_vars[f'last_{key}'] = value
    
    # Replace placeholders with captured values
    for placeholder in placeholders:
        if placeholder in all_vars:
            response = response.replace(f'{{{placeholder}}}', all_vars[placeholder])
    
    return response



def pre_process(sentence):
    # Tokenize the sentence
    words = word_tokenize(sentence)

    # Define custom stopword set
    custom_keep = {'who', 'she', 'he', 'they', 'what'}
    stop_words = set(stopwords.words("english"))
    custom_stopwords = stop_words - custom_keep  # remove certain words from stopwords

    # Add punctuation to stopwords for filtering
    custom_stopwords.update({".", ",", "?", "!"})

    # Remove stopwords and punctuation
    filtered_words = [word for word in words if word.lower() not in custom_stopwords]

    # Join filtered words into a sentence
    filtered_sentence = " ".join(filtered_words)

    # Lemmatize the filtered sentence
    lemmatizer = WordNetLemmatizer()
    words = word_tokenize(filtered_sentence)
    lemmatized_words = [lemmatizer.lemmatize(word, "v") for word in words if word.lower()]

    # Return cleaned, lemmatized string
    return " ".join(lemmatized_words)

def pattern_matching(userinput, tags_df, memory=None):
    lamentized_input = pre_process(userinput)

    # Goes through each row in the dataframe, then tries to check for the pattern
    for index, row in tags_df.iterrows():
        pattern = row['patterns']
        match = re.search(pattern, lamentized_input, re.IGNORECASE)

        # if no match, try matching with original user input
        if not match:
            match = re.search(pattern, userinput, re.IGNORECASE)
        
        # If there is a match, choose a random response
        if match:
            response = random.choice(row['responses'])
            
            # Capture all named groups from the regex match
            captured_groups = {}
            for group_name, group_value in match.groupdict().items():
                if group_value is not None:
                    captured_groups[group_name] = group_value.strip()
            
            # Expand response template with captured groups
            response = expand_response_template(response, captured_groups, memory)
            
            return response, captured_groups    
    
    default_responses = [
        "Sorry, I didn't understand that. Can you rephrase?",
        "I'm not sure how to respond to that. Could you try asking in a different way?",
        "Hmm, I don't have a response for that. Can you say it differently?"
    ]
    return random.choice(default_responses), {}


def get_response(user_message, memory=None):
    """
    Main entry point for the Django view.
    Takes a user message string and an optional memory dict (from the session).
    Returns (response_text, updated_memory).
    """
    if memory is None:
        memory = {}

    tags_df = _get_tags_df()
    response, captured_vars = pattern_matching(user_message, tags_df, memory)

    # Persist the conversation log
    save_conversation(user_message, response)

    # Update memory with any newly captured variables
    memory.update(captured_vars)

    return response, memory

# DB-aware query handlers
# Patterns that indicate the user is asking about a specific listing
_DB_QUERY_PATTERNS = [
    # price / cost queries  e.g. "how much is the hammer", "price of drill"
    (re.compile(
        r'(?:price|cost|how much|worth|value)\s+(?:is|of|for)?\s*(?:the\s+)?(?P<item>.+)',
        re.IGNORECASE,
    ), 'price'),
    # availability / do you have  e.g. "do you have a ladder", "is there a saw"
    (re.compile(
        r'(?:do you have|is there|any|available)\s+(?:a\s+|an\s+)?(?P<item>.+)',
        re.IGNORECASE,
    ), 'availability'),
    # details / info  e.g. "tell me about the drill", "details on hammer"
    (re.compile(
        r'(?:tell me about|details|info|information)\s+(?:on\s+|about\s+)?(?:the\s+)?(?P<item>.+)',
        re.IGNORECASE,
    ), 'details'),
    (re.compile(
        r'(?:condition|category|seller|description)\s+(?:of|for)?\s*(?:the\s+)?(?P<item>.+)',
        re.IGNORECASE,
    ), 'details'),
]


def db_query_response(user_message):
    """
    It checks the user message against predefined patterns to detect if they're asking about a listing.
    if so, it queries the database for active listings, and returns a response string with the relevant info.
    If no DB match is found, it returns None to let the normal pattern-matching engine do it. 

    Import is done in the function to save on initial load time and to avoid circular imports at module load.
    """
    from .models import Listing, ListingStatus

    for pattern, query_type in _DB_QUERY_PATTERNS:
        match = pattern.search(user_message)
        if not match:
            continue

        item_query = match.group('item').strip().rstrip('?').strip()
        if not item_query:
            continue

        # Search active listings whose title contains the query term(s)
        listings = Listing.objects.filter(
            title__icontains=item_query,
            status=ListingStatus.ACTIVE,
        ).select_related('user', 'category', 'location')[:5]

        if not listings:
            return (
                f"I couldn't find any active listings matching \"{item_query}\" "
                f"right now. Try browsing the Products page or use the search bar."
            )

        if query_type == 'price':
            if listings.count() == 1:
                l = listings[0]
                return (
                    f"The listing \"{l.title}\" is priced at £{l.price:.2f} "
                    f"(condition: {l.get_condition_display()}, "
                    f"seller: {l.user.username})."
                )
            lines = "\n".join(
                f"• {l.title} — £{l.price:.2f} ({l.get_condition_display()})"
                for l in listings
            )
            return f"Here are the active listings I found for \"{item_query}\":\n{lines}"

        elif query_type == 'availability':
            lines = "\n".join(
                f"• {l.title} — £{l.price:.2f} ({l.get_condition_display()}, "
                f"posted by {l.user.username})"
                for l in listings
            )
            return (
                f"Yes! Here's what's currently available for \"{item_query}\":\n{lines}"
            )
        elif query_type == 'condition':
            lines = "\n".join(
                f"• {l.title} — Condition: {l.get_condition_display()}, "
                f"Category: {l.category.name}, Seller: {l.user.username}"
                for l in listings
            )
            return (
                f"Here are the details of active listings I found for \"{item_query}\":\n{lines}"
            )

        elif query_type == 'details':
            l = listings[0]
            return (
                f"\"{l.title}\" — £{l.price:.2f}\n"
                f"Condition: {l.get_condition_display()}\n"
                f"Category: {l.category.name}\n"
                f"Seller: {l.user.username}\n"
                f"Description: {l.description}"
            )

    return None  # no DB match — let normal chatbot handle it

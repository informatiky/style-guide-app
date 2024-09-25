import json
import logging
from flask import Flask, request, jsonify, render_template, send_from_directory
import spacy
from spacy.matcher import PhraseMatcher
from spacy.tokens import Span
import re
import os

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load spaCy model
nlp = spacy.load("en_core_web_md")
logger.info("Loaded spaCy model")

# Load rules from JSON file
try:
	with open('ruleset.json', 'r') as f:
		rules = json.load(f)['rules']
	logger.info(f"Loaded {len(rules)} rules from ruleset.json")
except Exception as e:
	logger.error(f"Error loading ruleset.json: {str(e)}")
	rules = []

# Create a PhraseMatcher
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

# Prepare patterns for matching
pattern_count = 0
for rule in rules:
	if 'word' in rule:
		words = rule['word'] if isinstance(rule['word'], list) else [rule['word']]
		for word in words:
			# Add the original word
			matcher.add(word, None, nlp(word))
			pattern_count += 1
			# Add a version with 'ing' if it's a verb
			if rule.get('partOfSpeech') == 'VERB':
				matcher.add(word, None, nlp(word + 'ing'))
				pattern_count += 1
			# Add a version without final 's' if it ends with 's'
			if word.endswith('s'):
				matcher.add(word, None, nlp(word[:-1]))
				pattern_count += 1
			# Add a version with final 's' if it doesn't end with 's'
			if not word.endswith('s'):
				matcher.add(word, None, nlp(word + 's'))
				pattern_count += 1
	else:
		logger.warning(f"Rule without 'word' key: {rule}")

logger.info(f"Added {pattern_count} patterns to the matcher")

@app.route('/favicon.ico')
def favicon():
	return send_from_directory(os.path.join(app.root_path, 'static'),
	                           'favicon.ico',mimetype='image/vnd.microsoft.icon')

@app.route('/ethnic-and-racial-groups')
def ethnicRacialGroups():
	return render_template('ethnicRacialGroups.html')

@app.route('/fewer-than-less-than')
def fewerLessThan():
	return render_template('fewerLessThan.html')

@app.route('/gender-and-sex')
def genderSex():
	return render_template('genderSex.html')

@app.route('/islam-islamism-jihadist-mujahideen')
def islam():
	return render_template('islam.html')

@app.route('/singular-or-plural')
def singularPlural():
	return render_template('singularPlural.html')

@app.route('/the')
def the():
	return render_template('the.html')

@app.route('/transitive-and-intransitive-verbs')
def verbs():
	return render_template('verbs.html')

@app.route('/')
def index():

	return render_template('index.html')

@app.route('/check', methods=['POST'])
def check_text():
	text = request.form['text']
	logger.info(f"Received text: {text}")
	doc = nlp(text)
	logger.info(f"Processed text with spaCy: {len(doc)} tokens")

	results = []

	# Use the PhraseMatcher to find matches
	matches = matcher(doc)
	logger.info(f"Found {len(matches)} initial matches")

	for match_id, start, end in matches:
		span = doc[start:end]
		matched_text = span.text
		logger.debug(f"Examining match: {matched_text}")

		# Find the corresponding rule
		for rule in rules:
			if 'word' not in rule:
				continue
			words = rule['word'] if isinstance(rule['word'], list) else [rule['word']]
			if any(re.match(f"^{re.escape(word)}(ing|s)?$", matched_text, re.IGNORECASE) for word in words):
				logger.debug(f"Found matching rule for: {matched_text}")
				pos_match = 'partOfSpeech' not in rule or span.root.pos_ == rule['partOfSpeech']

				if pos_match:
					logger.debug(f"POS match successful for: {matched_text}")
					result = {
						'word': matched_text,
						'start': span.start_char,
						'end': span.end_char,
						'suggestion': rule.get('replaceWith', ''),
						'message': rule.get('replaceMessage', rule.get('message', '')),
						'content': rule.get('content', '')
					}
					results.append(result)
					break
				else:
					logger.debug(f"POS mismatch for: {matched_text}. Expected {rule.get('partOfSpeech')}, got {span.root.pos_}")

	if not results:
		logger.info("No matches found, returning general advice")
		results.append({
			'word': text,
			'start': 0,
			'end': len(text),
			'message': "No specific style guide rules found for this text. However, always aim for clarity and conciseness in your writing."
		})

	logger.info(f"Returning {len(results)} results")
	return jsonify(results)

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=5001)
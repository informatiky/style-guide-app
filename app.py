import spacy


def is_passive(doc):
	for token in doc:
		if token.dep_ == "nsubjpass" or token.dep_ == "auxpass":
			return True
	return False


# Load the English language model
nlp = spacy.load("en_core_web_lg")

# Get input from the user
sentence = input("Enter a sentence: ")

# Process the sentence
doc = nlp(sentence)

# Check if the sentence is passive
if is_passive(doc):
	print("The sentence is in passive voice.")
else:
	print("The sentence is not in passive voice.")

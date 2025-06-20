from allosaurus.app import read_recognizer
import string
import ipaTransliteration as epi
from difflib import SequenceMatcher
# Load audio transcription model
model = read_recognizer()

# Python translator to remove punctuation & whitespace
translator = str.maketrans('', '', string.punctuation + string.whitespace + 'ː' + 'ˑ')
stress_translator = str.maketrans('', '', string.whitespace + 'ː' + 'ˑ' + "," + "ʼ")

# Take audio, return IPA transcription without whitespace or punctuation
def transcribe_audio(audio_path: str) -> str:
	ipa_transcription = model.recognize(audio_path)
	ipa_transcription = ipa_transcription.translate(translator)
	return ipa_transcription

# Transcribe audio, return IPA without whitespace but retain stress markings
def transcribe_audio_with_stress(audio_path: str) -> str:
	ipa_transcription = model.recognize(audio_path, 'spa')
	ipa_transcription = ipa_transcription.translate(stress_translator)
	return ipa_transcription	

# Compare user pronunciation to correct pronunciation,
# using difflib to find which symbols in correct pronunciation were pronounced incorrectly
# Convert index of symbols in correct pronunciation to index in sentence mapping with ipa_indices
# Opcodes are 5 tuples of form tag, i1, i2, j1, j2
# where the tag is replace/delete/insert/equal
# and user_ipa[i1:i2] should be replaced/deleted/inserted or equal (as tag says) with correct_ipa[j1:j2]
def compare_strings(sentence, user_ipa):
	sentence_mapping = epi.sentenceMapping(sentence)
	sentence_mapping.transliterate_latam()
	correct_ipa = sentence_mapping.get_ipa()
	sentence_mapping.set_indices()
	sequence_matcher = SequenceMatcher(None, user_ipa, correct_ipa)
	opcode_list = sequence_matcher.get_opcodes()
	for opcode in opcode_list:
		# opcode[3] is index of first char in correct_ipa that deletion/insertion/replacement starts at
		# indices[opcode[3]] is (ipa letter, index in sentence mapping)
		if opcode[0] == 'delete':
			delete_incorrect(sentence_mapping, user_ipa[opcode[1]], opcode[3])
		elif opcode[0] == 'insert' or opcode[0] == 'replace':
			insert_incorrect(sentence_mapping, opcode[3], opcode[4])

	output_str = ""

	for ipa in sentence_mapping.ipa_mapping:
		if ipa.pronounced_correctly == False:
			output_str += ">" + ipa.ortho_letter + "<"
		else:
			output_str += ipa.ortho_letter
	return output_str 
		
		
# if extra char between index -1 and index is vowel, mark prev IPA symbol as incorrect if it's a vowel,
# otherwise mark next IPA marking as incorrect, if no vowels, mark prev consonant as incorrect
# if consonant, mark prev consonant as incorrect, if no prev consonant, mark next consonant as incorrect, 
# otherwise mark prev vowel as incorrect 
def delete_incorrect(sentence_mapping, current_ipa, pos):
	# Convert IPA symbol index to sentence_mapping index
	index = sentence_mapping.ipa_indices[pos][1] if pos < len(sentence_mapping.ipa_indices) else sentence_mapping.ipa_indices[-1][1]
	prev_index = sentence_mapping.ipa_indices[pos - 1][1]
	next_index = index
	prev_mapping = sentence_mapping.ipa_mapping[prev_index]
	next_mapping = sentence_mapping.ipa_mapping[next_index]

	# edge case for 'h'
	h = {'h', "H"}
	if sentence_mapping.ipa_mapping[index - 1] in h and index > 0:
		sentence_mapping.ipa_mapping[index - 1].pronounced_correctly = False

	if is_vowel_ipa(current_ipa):
		if index == 0:
			next_mapping.pronounced_correctly = False
		elif index == len(sentence_mapping.ipa_mapping) - 1:
			prev_mapping.pronounced_correctly = False
		elif is_vowel_ipa(prev_mapping.ipa_letter):
			prev_mapping.pronounced_correctly = False
		elif is_vowel_ipa(next_mapping.ipa_letter):
			next_mapping.pronounced_correctly = False
		else:
			prev_mapping.pronounced_correctly = False
	else:
		if index == 0:
			next_mapping.pronounced_correctly = False
		elif index == len(sentence_mapping.ipa_mapping):
			prev_mapping.pronounced_correctly = False
		elif not is_vowel_ipa(prev_mapping.ipa_letter) and string.isalpha(prev_mapping.ortho_letter):
			prev_mapping.pronounced_correctly = False
		else:
			next_mapping.pronounced_correctly = False

# Since correct_ipa[start_index] to end_index must be inserted into user pronunciation,
# that means it was all incorrectly pronounced,
# so mark all ipa_mapping from start_index to end_index as incorrect
# replacement uses same logic
def insert_incorrect(sentence_mapping, start_pos, end_pos):
	prev_index = sentence_mapping.ipa_indices[start_pos][1] - 1
	prev_mapping = sentence_mapping.ipa_mapping[prev_index]

	# edge case for 'h'
	h = {'h', 'H'}
	if prev_mapping.ortho_letter in h and prev_index >= 0:
		prev_mapping.pronounced_correctly = False
	
	for i in range(start_pos, end_pos if end_pos < len(sentence_mapping.ipa_indices) else len(sentence_mapping.ipa_indices)):
		# Convert IPA symbol index to sentence_mapping_index
		index = sentence_mapping.ipa_indices[i][1]
		next_mapping = sentence_mapping.ipa_mapping[index]
		next_mapping.pronounced_correctly = False
		
# helper function to tell if an IPA character is a vowel sound		
def is_vowel_ipa(ipa_char):
	vowels = {"i", "y", "ɨ", "ʉ", "ɯ", "u", "ɪ", "ʏ", "ʊ", "e", "ø", "ɘ", "ɵ", "ɤ", "o", "e̞", "ø̞", "ə", "ɤ̞", "o̞", "ɛ", "œ", "ɜ", "ɞ", "ʌ", "ɔ", "æ", "ɐ", "a", "ɶ", "ä", "ɑ", "ɒ"}

	return ipa_char in vowels

# Since some sounds are similar enough that they can be considered correct,
# change chars in user_ipa to equivalent chars that transliterate() would generate
# so users are not penalized for essentially correct pronunciation
def preprocess_user_ipa(user_ipa):
	user_ipa.replace("ɣ", "g")
	user_ipa.replace("ð̞", "d")
	user_ipa.replace("β", "b")
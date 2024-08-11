# This file is part of the EstGEC punctuation error synthesizer
# Author: Christian-Enrique Hindremäe
# 2024

# file: error_generator.py
#
# Contains functions necessary for error synthesis
# Imported as a module in main file synthesizer.py

import string
import random

# Collect correct punctuations from input sentence


def collect_punctuations(sentence):
    correct_punctuations = []
    for char in sentence:
        if char in string.punctuation:
            correct_punctuations.append(char)
    return correct_punctuations

# Determine whether to synthesize an error


def determine_punct_error(percentage):
    introduce = percentage
    no_introduce = 100 - percentage
    choices = ["yes", "no"]
    choice = random.choices(choices, weights=[introduce, no_introduce], k=1)

    return choice[0]


def determine_error_type(u, m, r, u_error_is_possible):
    if u_error_is_possible == False:
        u = 0
    choices = ["u", "m", "r"]
    choice = random.choices(choices, weights=[u, m, r], k=1)

    return choice[0]


def determine_unnecessary_character(unnecessaryPunctuation, u_punctuation_options):
    # Map statistics based on available characters in the sentence
    options = {key: value for key, value in unnecessaryPunctuation.items(
    ) if key in u_punctuation_options}
    choices = list(options.keys())
    weights = list(options.values())
    choice = random.choices(choices, weights=weights, k=1)

    return choice[0]


def determine_missing_character(correct_punctuations, missingPunctuation, correct_end_punctuation, sentence, missingCombinations):
    top_combination_weights = {}
    print(f"Sentence: {sentence}")

    # Create a list of pairs (punctuation, word) from the sentence
    punct_word_pairs = []
    for punct in correct_punctuations:
        parts = sentence.split(punct)
        for i in range(1, len(parts)):
            word = parts[i].strip().split()[0] if parts[i].strip() else ""
            if word:
                punct_word_pairs.append((punct, word))

    print(f"Punctuation-word pairs: {punct_word_pairs}")

    # Check if any pairs exist in known top combinations
    for punct, word in punct_word_pairs:
        for combination in missingCombinations:
            comb_punct, comb_word, comb_weight = combination
            if word == comb_word and punct == comb_punct:
                top_combination_weights[(word, punct)] = comb_weight

    if top_combination_weights:
        print("Got combinations:")
        print(top_combination_weights)
        selected_word, selected_punct = max(
            top_combination_weights, key=top_combination_weights.get)
        print(f"Chose {selected_punct} and {selected_word}")
        return selected_punct, selected_word
    else:
        options = {key: value for key, value in missingPunctuation.items()
                   if key in correct_punctuations}
        if not options:
            return None, ""
        choices = list(options.keys())
        weights = list(options.values())
        choice = random.choices(choices, weights=weights, k=1)

        print(f"Chose {choice[0]}")
        return choice[0], ""


def determine_replacement_character(r_punctuation, total, correct_punctuations, total_fixes, middle_fixes, end_fixes):

    # Choose wrong character - options are all wrong characters which corrections sub-directory contains any from correct_punctuations
    wrong_options = {key: value for key, value in r_punctuation.items() if set(
        total_fixes[key]) & set(correct_punctuations)}
    wrong_choice = random.choices(
        list(wrong_options.keys()), weights=list(wrong_options.values()), k=1)[0]

    # Choose correct character
    correct_options = {key: value for key, value in total_fixes[wrong_choice].items(
    ) if key in correct_punctuations}
    correct_choice = random.choices(
        list(correct_options.keys()), weights=list(correct_options.values()), k=1)[0]

    # Choose position
    position_options = ["end", "middle"]
    middle_percentage = 0
    end_percentage = 0
    if wrong_choice in middle_fixes:
        middle_percentage = middle_fixes[wrong_choice].get(correct_choice, 0)
    if wrong_choice in end_fixes:
        end_percentage = end_fixes[wrong_choice].get(correct_choice, 0)
    position_choice = random.choices(position_options, weights=[
                                     end_percentage, middle_percentage], k=1)[0]

    return correct_choice, wrong_choice, position_choice


def generate_u_error(sentence, words, character, word):
    # Check if the chosen word is the first word in the sentence
    if word == words[0]:
        return sentence  # Do nothing if it's the first word

    # Find the index of the word in the list of words
    word_index = words.index(word)

    # Append the character to the preceding word
    preceding_word = words[word_index - 1]
    word_with_character = preceding_word + character

    # Replace the original word with the word containing the unnecessary character
    error_sentence = sentence.replace(preceding_word, word_with_character, 1)

    return error_sentence


def generate_m_error(sentence, character, word):
    if word:
        print(f"Got {character} and {word}")
        # Construct the combination string to be removed
        combination = character + " " + word
        # Find all occurrences of the combination
        start = 0
        positions = []
        while True:
            start = sentence.find(combination, start)
            if start == -1:
                break
            positions.append(start)
            start += len(combination)

        # Ensure we replace the specific occurrence
        if positions:
            pos = positions[0]
            error_sentence = sentence[:pos] + " " + \
                word + sentence[pos + len(combination):]
        else:
            error_sentence = sentence
    else:
        pos = -1
        for _ in range(sentence.count(character)):
            pos = sentence.find(character, pos + 1)
            if pos != -1 and sentence[pos:pos + len(character)] == character:
                break
        if pos != -1:
            error_sentence = sentence[:pos] + sentence[pos + len(character):]
        else:
            error_sentence = sentence

    return error_sentence


def generate_r_error(sentence, correct_end_punctuation, correct_character, wrong_character, position):
    if position == "middle":
        error_sentence = sentence.replace(correct_character, wrong_character)
    elif position == "end":
        error_sentence = sentence.replace(
            correct_end_punctuation, wrong_character)

    return error_sentence

# This file is part of the EstGEC punctuation error synthesis
# Author: Christian-Enrique Hindremäe
# 2024 v1.0

# file: synthesizer.py
# 
# Synthesizes errors into correct source sentences using generated statistics

# Usage: python synthesizer.py source_file
# Where
#   source_file - source text file used for synthesizing errors into

# Output:
#   joint parallel corpora files "all_correct" and "all_incorrect"
#   three data sets - train, valid, test; divided by ratio 8:1:1

import sys
from nltk import sent_tokenize
from nltk import word_tokenize
from datetime import datetime
import analyzer
import error_generator
import pickle
import string
import nltk
import math
nltk.download('punkt')

# Call analyzer to generate and provide statistics, and save it in binary using pickle
def receive_statistics():
    statistics = analyzer.generate_statistics()

    with open("statistics.pkl", "wb") as fp:
        pickle.dump(statistics, fp)

# Retrieve statistics from the binary file
def import_percentages_data():
    with open("statistics.pkl", "rb") as fp:
        statistics = pickle.load(fp)
    return statistics

# Tokenize the source text using nltk
def process_source_text(file_path):
    group = []  # Group of sentences

    with open(file_path, "r", encoding="utf8") as file:
        # As the necessary format for Fairseq is having one sentence per line, script defines a buffer 
        # to prevent splitting a sentence across multiple lines
        sentence_buffer = ""
        for line in file:
            sentence_buffer += (" " + line)
            buffer_sentences = sent_tokenize(sentence_buffer)

            if len(buffer_sentences) > 1:
                for sentence in buffer_sentences[:-1]:
                    group.append(sentence.strip())
                sentence_buffer = buffer_sentences[-1]
        return group

# Write correct and incorrect sentences in corresponding files
def output_set(file, incorrect_file, sentence, incorrect_sentence):
    tokenized_sentence = ' '.join(word_tokenize(sentence))
    tokenized_incorrect_sentence = ' '.join(word_tokenize(incorrect_sentence))
    file.write(f"{tokenized_sentence}\n")
    incorrect_file.write(f"{tokenized_incorrect_sentence}\n")
    
def split_set(filename):
    with open(filename, "r", encoding="utf8") as file:
        sentences = [line.strip() for line in file]
    
    max_sentences = len(sentences)
    max_train_set = math.floor(max_sentences * 0.8)
    max_test_set = math.floor(max_sentences * 0.1) + max_train_set

    with open("train_" + filename, "w", encoding="utf8") as train_file, \
        open("valid_" + filename, "w", encoding="utf8") as valid_file, \
        open("test_" + filename, "w", encoding="utf8") as test_file:

        for i in range(max_sentences):
            if i < max_train_set:
                output_file = train_file
            elif i < max_test_set:
                output_file = test_file
            else:
                output_file = valid_file

            output_file.write(sentences[i] + "\n")
            
    train_file.close()
    valid_file.close()
    test_file.close()

def main():
    if len(sys.argv) != 2:
        print_usage()
        sys.exit(-1)
    
    print(f"{datetime.now()}    Retrieving statistics...")
    receive_statistics()
    statistics = import_percentages_data()

    # Map statistics to variables
    punctuation_error = round(float(statistics["totalPunctErrors"]), 2)
    u_error = round(float(statistics["unnecessaryErrors"]), 2)
    m_error = round(float(statistics["missingErrors"]), 2)
    r_error = round(float(statistics["replacementErrors"]), 2)
    m_punctuation = statistics["missingPunctuation"]
    u_punctuation = statistics["unnecessaryPunctuation"]
    r_punctuation = statistics["replacementPunctuation"]
    r_punctuation_end = statistics["replacementEndPunctuation"]
    r_punctuation_middle = statistics["replacementMiddlePunctuation"]
    r_punctuation_total_fixes = statistics["fixesTotalPunctuation"]
    r_punctuation_end_fixes = statistics["fixesEndPunctuation"]
    r_punctuation_middle_fixes = statistics["fixesMiddlePunctuation"]
    r_punctuation_total_fix_percentages = statistics["totalFixPercentages"]
    r_punctuation_middle_fix_percentages = statistics["middleFixPercentages"]
    r_punctuation_end_fix_percentages = statistics["endFixPercentages"]
    u_combinations = statistics["unnecessaryCombinations"]
    m_combinations = statistics["missingCombinations"]
    
    print(m_combinations)

    # In case of replacing full stop at the end of the sentence, this variable indicates that next sentence should start lowercase
    connect_next_sentence = False

    with open("all_correct.txt", "w", encoding="utf8") as all_file_correct, \
        open("all_incorrect.txt", "w", encoding="utf8") as all_file_incorrect:
        
        file = sys.argv[1]
        print(f"{datetime.now()}    Processing source...")
        group = process_source_text(file)
        sentence_counter = 0
        print(f"Length of processed text: {len(group)}")     
        max_sentences = len(group)
        print(f"{datetime.now()}    Starting error synthesis")
        for sentence in group:
            print(f"Progress: {sentence_counter}/{max_sentences}", end="\r", flush=True)
            
            if connect_next_sentence:
                sentence = sentence[0].lower() + sentence[1:]
                connect_next_sentence = False
            correct_punctuations = error_generator.collect_punctuations(
                sentence)
            correct_end_punctuation = sentence[-1]
            words = sentence.split()
            u_error_is_possible = False
            u_words_options = []
            u_punctuation_options = []

            # Determine if the sentence contains words that are common for U_ERROR
            for nextWord in u_combinations.keys():
                if nextWord in words:
                    preceding_word_index = words.index(nextWord) - 1
                    if preceding_word_index >= 0 and words[preceding_word_index][-1] not in string.punctuation:
                        u_error_is_possible = True
                        u_words_options.append(nextWord)
                        u_punctuation_options.append(u_combinations[nextWord])
                
            introduce_error = error_generator.determine_punct_error(punctuation_error)
            error_type = "none"

            match introduce_error:
                case "yes":
                    error_type = error_generator.determine_error_type(u_error, m_error, r_error, u_error_is_possible)
                case "no":
                    continue

            match error_type:
                case "u":
                    character = error_generator.determine_unnecessary_character(
                        u_punctuation, u_punctuation_options)
                    word = u_words_options[u_punctuation_options.index(character)]
                    error_sentence = error_generator.generate_u_error(
                        sentence, words, character, word)
                    output_set(all_file_correct, all_file_incorrect, sentence, error_sentence)
                case "m":
                    pair = error_generator.determine_missing_character(
                        correct_punctuations, m_punctuation, correct_end_punctuation, sentence, m_combinations)
                    character = pair[0]
                    if character == None:
                        continue
                    word = pair[1]
                    error_sentence = error_generator.generate_m_error(
                        sentence, character, word)
                    output_set(all_file_correct, all_file_incorrect, sentence, error_sentence)
                case "r":
                    correct_character, wrong_character, position = error_generator.determine_replacement_character(
                        r_punctuation, r_punctuation_total_fix_percentages, correct_punctuations, r_punctuation_total_fixes, r_punctuation_middle_fixes, r_punctuation_end_fixes)
                    error_sentence = error_generator.generate_r_error(sentence, correct_end_punctuation, correct_character, wrong_character, position)
                    if position == "end" and wrong_character == "," or wrong_character == ":":
                        connect_next_sentence = True
                    output_set(all_file_correct, all_file_incorrect, sentence, error_sentence)
                case "none":
                    continue
            sentence_counter += 1
    all_file_correct.close()
    all_file_incorrect.close()
    print(f"{datetime.now()}    Error synthesis finished. Splitting data into train, valid, and test sets...")
    split_set("all_correct.txt")
    split_set("all_incorrect.txt")
    print(f"{datetime.now()}    Finished")
    
def print_usage():
    print("Usage: python synthesizer.py source_file")
    print("Where")
    print("     source_file - source text file for synthesizing errors into")
    
main()

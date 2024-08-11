# This file is part of the EstGEC punctuation error synthesizer
# Author: Christian-Enrique Hindremäe
# 2024

# file: analyzer.py
#
# Generates statistics from annotated text files
# When executed separately, outputs statistics only as a text file in the directory ./statistics_output
# Imported as a module in main file synthesizer.py

import os
import glob
from datetime import datetime

# Storing statistics in human-readable way
output_dir = "./statistics_output"
os.makedirs(output_dir, exist_ok=True)
time = datetime.now().strftime("%Y-%m-%d")


def save_to_file(data):
    filenametime = time + "_statistics_summary.txt"
    filename = (os.path.join(output_dir, filenametime))
    file = open(filename, "a", encoding="utf8")
    file.write(f"{data}\n")
    file.close


def generate_statistics():
    sentenceCount = 0
    sentenceCountByLevel = {"A2": 0, "B1": 0, "B2": 0, "C1": 0}
    punctErrorCounts = {"M:PUNCT": 0, "U:PUNCT": 0, "R:PUNCT": 0}
    punctErrorCountsByLevel = {"A2": 0, "B1": 0, "B2": 0, "C1": 0}
    errorSentenceCount = 0
    errorSentenceCountByLevel = {"A2": 0, "B1": 0, "B2": 0, "C1": 0}
    isErrorSentence = False
    missingPunctuation = {}  # Characters that have been missing
    replacementPunctuation = {}  # Characters that have been wrong
    middleReplacementPunctuation = {}  # Wrong characters in the middle of sentence
    endReplacementPunctuation = {}  # Wrong characters in the end of sentence
    unnecessaryPunctuation = {}  # Characters that have been unnecessary
    replacementMapping = {}
    # Corrections for each wrong character in the middle of sentence
    middleReplacementMapping = {}
    # Corrections for each wrong character in the end of sentence
    endReplacementMapping = {}
    parameters = []  # Container for M2 markup
    characterToReplace = ''  # Character in the sentence needing to be replaced
    characterToReplaceIndex = 0  # Index of the character
    nextWordsForUnnecessary = {}
    combinationsUnnecessary = {}  # Unnecessary characters paired with following words
    combinationsUnnecessaryNext = {}
    combinationsPrecedingUnnecessaryNext = {}
    combinationsMissing = {}
    totalFixes = {}  # Characters that have been used as corrections
    endFixes = {}
    middleFixes = {}

    # Percentages for error synthesis
    percentage_missing_punctuation = {}
    percentage_unnecessary_punctuation = {}
    percentage_replacement_punctuation = {}
    percentage_middle_replacement_punctuation = {}
    percentage_end_replacement_punctuation = {}
    percentage_replacement_mapping = {}
    percentage_end_replacement_mapping = {}
    percentage_middle_replacement_mapping = {}
    percentage_total_fixes = {}
    percentage_end_fixes = {}
    percentage_middle_fixes = {}

    combination_entries = []

    # Path to gold token files
    paths = glob.glob(r"./source_test/*/*.txt")

    for src in paths:
        with open(src, "r", encoding="utf-8") as f:
            language_level = os.path.basename(os.path.dirname(src))
            activeSentence = []

            for line in f:
                line = line.strip()

                if not line:
                    continue

                # Splitting the sentence using "|||"
                parts = line.split("|||")

                # Splitting the index part of the markup separated by whitespace, in case of source sentence ("S") this splits the whole sentence
                parameters = parts[0].split()

                if parameters[0] == "S":
                    isErrorSentence = False
                    sentenceCount += 1
                    sentenceCountByLevel[language_level] += 1
                    activeSentence = parameters  # Active sentence currently analyzed

                if parameters[0] == "A":
                    if parts[-1] == "0":
                        errorType = parts[1]

                        # Count error types
                        if errorType in punctErrorCounts:
                            if isErrorSentence == False:
                                errorSentenceCount += 1
                                errorSentenceCountByLevel[language_level] += 1
                                isErrorSentence = True
                            # Punctutation presented as correction, in case of multiple options separated by "||"
                            correction = parts[2].split("||")
                            correctionLength = len(correction)
                            punctErrorCounts[errorType] += 1
                            punctErrorCountsByLevel[language_level] += 1

                        # Replacement errors
                        if errorType == "R:PUNCT":
                            characterToReplaceIndex = int(parameters[1])
                            characterToReplace = activeSentence[characterToReplaceIndex+1]

                            position = "middle"
                            if characterToReplaceIndex == len(activeSentence) - 2:
                                position = "end"

                            if characterToReplace not in replacementPunctuation:
                                replacementPunctuation[characterToReplace] = 0
                            replacementPunctuation[characterToReplace] += 1

                            if position == "middle":
                                if characterToReplace not in middleReplacementPunctuation:
                                    middleReplacementPunctuation[characterToReplace] = 0
                                middleReplacementPunctuation[characterToReplace] += 1

                            elif position == "end":
                                if characterToReplace not in endReplacementPunctuation:
                                    endReplacementPunctuation[characterToReplace] = 0
                                endReplacementPunctuation[characterToReplace] += 1

                            for option in correction:
                                if characterToReplace not in replacementMapping:
                                    replacementMapping[characterToReplace] = {}
                                if option[0] not in replacementMapping[characterToReplace]:
                                    replacementMapping[characterToReplace][option[0]] = 0
                                if correctionLength == 1:
                                    replacementMapping[characterToReplace][option[0]] += 1
                                elif correctionLength > 1:
                                    replacementMapping[characterToReplace][option[0]] += 0.5

                                if position == "middle":
                                    if characterToReplace not in middleReplacementMapping:
                                        middleReplacementMapping[characterToReplace] = {
                                        }
                                    if option[0] not in middleReplacementMapping[characterToReplace]:
                                        middleReplacementMapping[characterToReplace][option[0]] = 0
                                    if correctionLength == 1:
                                        middleReplacementMapping[characterToReplace][option[0]] += 1
                                    elif correctionLength > 1:
                                        middleReplacementMapping[characterToReplace][option[0]] += 0.5

                                elif position == "end":
                                    if characterToReplace not in endReplacementMapping:
                                        endReplacementMapping[characterToReplace] = {
                                        }
                                    if option[0] not in endReplacementMapping[characterToReplace]:
                                        endReplacementMapping[characterToReplace][option[0]] = 0
                                    if correctionLength == 1:
                                        endReplacementMapping[characterToReplace][option[0]] += 1
                                    elif correctionLength > 1:
                                        endReplacementMapping[characterToReplace][option[0]] += 0.5

                        # Missing errors
                        if errorType == "M:PUNCT":
                            missingPunctuations = correction
                            missingPunctuationIndex = int(parameters[1])
                            nextWord = None
                            if missingPunctuationIndex < len(activeSentence) - 2:
                                nextWord = activeSentence[missingPunctuationIndex + 1]
                                if nextWord not in combinationsMissing:
                                    combinationsMissing[nextWord] = {}
                            for missingPunctuationMark in missingPunctuations:
                                if missingPunctuationMark not in missingPunctuation:
                                    missingPunctuation[missingPunctuationMark] = 0
                                if correctionLength == 1:
                                    missingPunctuation[missingPunctuationMark] += 1
                                elif correctionLength > 1:
                                    missingPunctuation[missingPunctuationMark] += 0.5
                                if nextWord:
                                    if missingPunctuationMark not in combinationsMissing[nextWord]:
                                        combinationsMissing[nextWord][missingPunctuationMark] = 0
                                    combinationsMissing[nextWord][missingPunctuationMark] += 1

                        # Unnecessary errors
                        if errorType == "U:PUNCT":
                            unnecessaryCharacterIndex = int(parameters[1])
                            unnecessaryCharacter = activeSentence[unnecessaryCharacterIndex + 1]
                            precedingWord = activeSentence[unnecessaryCharacterIndex]
                            nextWord = None

                            if unnecessaryCharacterIndex < len(activeSentence) - 2:
                                nextWord = activeSentence[unnecessaryCharacterIndex + 2]

                            if unnecessaryCharacter not in unnecessaryPunctuation:
                                unnecessaryPunctuation[unnecessaryCharacter] = 0
                            unnecessaryPunctuation[unnecessaryCharacter] += 1

                            # Handle combinations of "unnecessary character + nextWord"
                            if nextWord:
                                combination = f"{unnecessaryCharacter} + {nextWord}"
                                if combination not in combinationsUnnecessaryNext:
                                    combinationsUnnecessaryNext[combination] = 0
                                combinationsUnnecessaryNext[combination] += 1

                            # Handle combinations of "precedingWord + unnecessary character + nextWord"
                            if nextWord:
                                combination = f"{precedingWord} + {unnecessaryCharacter} + {nextWord}"
                                if combination not in combinationsPrecedingUnnecessaryNext:
                                    combinationsPrecedingUnnecessaryNext[combination] = 0
                                combinationsPrecedingUnnecessaryNext[combination] += 1

    # Percentages
    totalPunctErrors = sum(punctErrorCounts.values())
    totalPunctErrorsPercentage = (errorSentenceCount / sentenceCount * 100)
    errorPercentages = {errorType: (
        count / totalPunctErrors) * 100 for errorType, count in punctErrorCounts.items()}

    mErrCount = punctErrorCounts["M:PUNCT"]
    uErrCount = punctErrorCounts["U:PUNCT"]
    rErrCount = punctErrorCounts["R:PUNCT"]

    # Statistics output

    filenametime = time + "_statistics_summary.txt"
    filename = (os.path.join(output_dir, filenametime))
    file = open(filename, "w", encoding="utf8")
    file.close

    flattened_counts = []
    for word, punct_counts in combinationsMissing.items():
        for punct, count in punct_counts.items():
            flattened_counts.append((punct, word, count))

    # Sort the list of tuples by count in descending order
    sorted_counts = sorted(flattened_counts, key=lambda x: x[2], reverse=True)

    # Extract and print the top 5 combinations
    missingCombinations = sorted_counts[:10]
    for word, punct, count in missingCombinations:
        print(f"{punct} + {word}: {count} korda")

    save_to_file(f"Kõikide lausete arv: {sentenceCount}\n")

    save_to_file(f"Kirjavahemärgivigade koguarv: {totalPunctErrors} \n")

    save_to_file(
        f"Kirjavahemärgivigu sisaldavate lausete arv: {errorSentenceCount} ({totalPunctErrorsPercentage:.2f}%)")

    save_to_file(
        f"Lausete, vigu sisaldavate lausete ja vigade arv keeletaseme kaupa:")
    for level, count in sorted(sentenceCountByLevel.items(), key=lambda item: item[1], reverse=True):
        save_to_file(
            f"{level}: {count} ({errorSentenceCountByLevel[level]}) ({punctErrorCountsByLevel[level]})")

    save_to_file("Vigade arv vea tüübi kaupa:")
    for errorType, count in sorted(punctErrorCounts.items(), key=lambda item: item[1], reverse=True):
        save_to_file(
            f"{errorType}: {count} ({errorPercentages[errorType]:.2f}%)")

    save_to_file("\n Puuduv kirjavahemärk, osakaal kõigist M:PUNCT vigadest:")
    for mark, count in sorted(missingPunctuation.items(), key=lambda item: item[1], reverse=True):
        save_to_file(f"{mark}: {count} ({(count / mErrCount * 100):.2f}%)")
        percentage_missing_punctuation[mark] = round(
            (count / mErrCount * 100), 2)

    save_to_file(
        "\n Üleliigne kirjavahemärk, osakaal kõigist U:PUNCT vigadest:")
    for mark, precedingWords in sorted(unnecessaryPunctuation.items(), key=lambda item: item[1], reverse=True):
        save_to_file(
            f"{mark}: {unnecessaryPunctuation[mark]} korda ({(unnecessaryPunctuation[mark] / uErrCount * 100):.2f}%)")
        percentage_unnecessary_punctuation[mark] = round(
            (unnecessaryPunctuation[mark] / uErrCount * 100), 2)

   # Iterate through the sorted combinationsUnnecessaryNext and save the top 5 entries
    for index, (combination, count) in enumerate(sorted(combinationsUnnecessaryNext.items(), key=lambda item: item[1], reverse=True)):
        if index < 5:
            parts = combination.split(" + ")
            unnecessaryChar, nextWord = parts[0], parts[1]
            combinationsUnnecessary[nextWord] = unnecessaryChar
            entry = f"{unnecessaryChar} + {nextWord}: {count} korda"
            combination_entries.append(entry)

    save_to_file("\n Üleliigne kirjavahemärk koos järgneva sõnaga:")
    for entry in combination_entries:
        save_to_file(entry)

    for combination, count in sorted(combinationsPrecedingUnnecessaryNext.items(), key=lambda item: item[1], reverse=True):
        parts = combination.split(" + ")
        precedingWord, unnecessaryChar, nextWord = parts[0], parts[1], parts[2]

    save_to_file("\n Vale kirjavahemärk, osakaal kõigist R:PUNCT vigadest:")
    for mark, count in sorted(replacementPunctuation.items(), key=lambda item: item[1], reverse=True):
        save_to_file(f"{mark}: {count} ({(count / rErrCount * 100):.2f}%)")
        percentage_replacement_punctuation[mark] = round(
            (count / rErrCount * 100), 2)

    save_to_file("\n Vale märgi parandused:")
    for originalPunctuation, replacements in sorted(replacementMapping.items(), key=lambda item: sum(item[1].values()), reverse=True):
        save_to_file(f"Vale märk: {originalPunctuation}")
        if originalPunctuation not in percentage_replacement_mapping:
            percentage_replacement_mapping[originalPunctuation] = {}
        for replacement, count in replacements.items():
            save_to_file(
                f"    parandus: {replacement} ({count} korda) ({(count / replacementPunctuation[originalPunctuation] * 100):.2f}%)")
            percentage_replacement_mapping[originalPunctuation][replacement] = round(
                (count / replacementPunctuation[originalPunctuation] * 100), 2)

    save_to_file(
        "\n Vale kirjavahemärk lause keskel, osakaal antud märgi esinemisest kokku:")
    for mark, count in sorted(middleReplacementPunctuation.items(), key=lambda item: item[1], reverse=True):
        save_to_file(
            f"{mark}: {count} ({(count / replacementPunctuation[mark] * 100):.2f}%)")
        percentage_middle_replacement_punctuation[mark] = round(
            (count / replacementPunctuation[mark] * 100), 2)

    save_to_file("\n Vale märgi parandused lause keskel:")
    for originalPunctuation, replacements in sorted(middleReplacementMapping.items(), key=lambda item: sum(item[1].values()), reverse=True):
        save_to_file(f"Vale märk: {originalPunctuation}")
        if originalPunctuation not in percentage_middle_replacement_mapping:
            percentage_middle_replacement_mapping[originalPunctuation] = {}
        for replacement, count in replacements.items():
            save_to_file(
                f"    parandus: {replacement} ({count} korda) ({(count / middleReplacementPunctuation[originalPunctuation] * 100):.2f}%)")
            percentage_middle_replacement_mapping[originalPunctuation][replacement] = round(
                (count / middleReplacementPunctuation[originalPunctuation] * 100), 2)
            totalFixes.setdefault(replacement, 0)
            middleFixes.setdefault(replacement, 0)
            totalFixes[replacement] += count
            middleFixes[replacement] += count

    save_to_file(
        "\n Vale kirjavahemärk lause lõpus, osakaal antud märgi esinemisest kokku:")
    for mark, count in sorted(endReplacementPunctuation.items(), key=lambda item: item[1], reverse=True):
        save_to_file(
            f"{mark}: {count} ({(count / replacementPunctuation[mark] * 100):.2f}%)")
        percentage_end_replacement_punctuation[mark] = round(
            (count / replacementPunctuation[mark] * 100), 2)

    save_to_file("\n Vale märgi parandused lause lõpus:")
    for originalPunctuation, replacements in sorted(endReplacementMapping.items(), key=lambda item: sum(item[1].values()), reverse=True):
        save_to_file(f"Vale märk: {originalPunctuation}")
        if originalPunctuation not in percentage_end_replacement_mapping:
            percentage_end_replacement_mapping[originalPunctuation] = {}
        for replacement, count in replacements.items():
            save_to_file(
                f"    parandus: {replacement} ({count} korda) ({(count / endReplacementPunctuation[originalPunctuation] * 100):.2f}%)")
            percentage_end_replacement_mapping[originalPunctuation][replacement] = round(
                (count / endReplacementPunctuation[originalPunctuation] * 100), 2)
            totalFixes.setdefault(replacement, 0)
            endFixes.setdefault(replacement, 0)
            totalFixes[replacement] += count
            endFixes[replacement] += count

    for fix, count in totalFixes.items():
        percentage_total_fixes[fix] = round((count / rErrCount * 100), 2)

    for fix, count in endFixes.items():
        percentage_end_fixes[fix] = round((count / totalFixes[fix] * 100), 2)

    for fix, count in middleFixes.items():
        percentage_middle_fixes[fix] = round(
            (count / totalFixes[fix] * 100), 2)

    print(combinationsUnnecessary)

    return {
        # Total punctuation errors percentage
        "totalPunctErrors": totalPunctErrorsPercentage,
        "unnecessaryErrors": errorPercentages["U:PUNCT"],
        "missingErrors": errorPercentages["M:PUNCT"],
        "replacementErrors": errorPercentages["R:PUNCT"],
        # Characters that have been unnecessary
        "unnecessaryPunctuation": percentage_unnecessary_punctuation,
        # Characters that have been missing
        "missingPunctuation": percentage_missing_punctuation,
        # Characters that have been wrong
        "replacementPunctuation": percentage_replacement_punctuation,
        # Characters that have been wrong in the end
        "replacementEndPunctuation": percentage_end_replacement_punctuation,
        # Characters that have been wrong in the middle
        "replacementMiddlePunctuation": percentage_middle_replacement_punctuation,
        # Corrections for wrong characters in total
        "fixesTotalPunctuation": percentage_replacement_mapping,
        # Corrections for wrong characters in the end
        "fixesEndPunctuation": percentage_end_replacement_mapping,
        # Corrections for wrong characters in the middle
        "fixesMiddlePunctuation": percentage_middle_replacement_mapping,
        "totalFixPercentages": percentage_total_fixes,  # Characters used as corrections
        # Characters used as corrections in the end
        "endFixPercentages": percentage_end_fixes,
        # Characters used as corrections in the middle
        "middleFixPercentages": percentage_middle_fixes,
        # Pairs of unnecessary character and following word,
        "unnecessaryCombinations": combinationsUnnecessary,
        # Pairs of missing character and following word
        "missingCombinations": missingCombinations
    }


generate_statistics()

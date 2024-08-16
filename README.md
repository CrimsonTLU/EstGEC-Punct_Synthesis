# EstGEC-Punct_Synthesis
## Author: Christian Hindremäe

This repository contains scripts that were developed as part of the Bachelor Thesis titled <a href="https://www.etera.ee/zoom/201483/view?page=34&p=separate&tool=info&view=0,0,2550,3301">Synthesis of Punctuation Errors for Estonian Grammatical Error Correction</a>

It consists of following scripts:

* **analyzer.py** - Iterates over gold token edits and calculates statistics of punctuation errors
* **error_generator.py** - Determines a punctuation to be used and synthesizes the error
* **synthesizer.py** - Main script, retrieves statistics from analyzer.py, processes source text with correct sentences, determines error type, calls appropriate functions from error_generator.py and outputs a parallel corpora of correct and incorrect sentences.

## Statistics structure:
Statistics are output in two ways:
1. Text file, meant to be human readable
2. Binary file, meant to be consumed by the main script

In general, the logic chain of the statistics is as follows:

Total number of sentences > Number of punctuation errors in total > No. of punct errors by type > Frequency of every punctuation under specific error type > Context sensitive frequencies (punctuation and preceding/following word etc) 

## Output structure:
Parallel corpora consists of matching files with suffixes **.correct** and **.incorrect** accordingly. There are both joint sets and subsets:

* All - all the sentences
* Train - 8/10 of the sentences
* Valid - 1/10 of the sentences
* Test - 1/10 of the sentences

Correct and incorrect sentences are matched via line number of file pairs, i.e correct sentence at line 6 in file train.correct matches the incorrect sentence at line 6 in file train.incorrect

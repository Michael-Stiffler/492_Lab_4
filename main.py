import sys
import re
import requests
from bs4 import BeautifulSoup, Comment
import spacy


def main():
    stop_words = load_stop_words()

    dicts = [
        {},
        {},
        {},
        {},
        {},
        {}
    ]

    """

    urls = [
        "https://en.wikipedia.org/wiki/Machine_learning",
        "https://en.wikipedia.org/wiki/Engineering",
        "http://my.clevelandclinic.org/research",
        "https://en.wikipedia.org/wiki/Data_mining",
        "https://en.wikipedia.org/wiki/Data_mining#Data_mining",
        "http://cis.csuohio.edu/~sschung/"
    ]

    """

    urls = ["https://en.wikipedia.org/wiki/Data_mining"]

    index = 0

    for url in urls:

        soup = BeautifulSoup(requests.get(url).content, "html.parser")
        words = []

        for text in soup.find_all(string=True):
            if text.parent.name != 'script' and text.parent.name != 'style' and text.parent.name != 'img' and len(text) != 0 and text != "\n" and not isinstance(text, Comment):
                words.append(text)

        file = "test" + str(index + 1) + ".txt"
        with open(file,  "w", encoding="utf-8") as f:
            for word in words:
                f.write(str(word))

        f.close()

        dicts[index] = parse_words(words, stop_words)

        index += 1

    print_dicts(dicts, urls)


def print_dicts(dicts, urls):

    index = 0

    for dictionary in dicts:

        counter = 0

        for item in sorted(dictionary, key=dictionary.get, reverse=True):
            if counter > 15:
                break
            else:
                print("For url: " + urls[index] + " is: " +
                      str(item) + " , " + str(dictionary[item]))

            counter += 1

        index += 1


def load_stop_words():
    stop_words = []

    with open("stop_word_list.txt") as f:
        lines = f.readlines()

        for line in lines:
            stop_words.append(line.strip('\n'))

        f.close()

    return stop_words


def parse_words(list_of_words, stop_words):
    counter = 0
    sp = spacy.load('en_core_web_sm')

    word_dict = {}

    for words in list_of_words:

        sentence = sp(str(words))
        bi_gram = ""

        for word in sentence:
            lemma = word.lemma_

            lemma = ''.join(i for i in str(lemma) if i.isalnum())
            lemma = lemma.lower()
            # and word.pos_ != "PUNCT" and word.pos_ != "SYM" and word.pos_ != "NUM"
            if len(lemma) > 0 and lemma not in stop_words and not find_num(lemma):
                if len(bi_gram) == 0:
                    if lemma == "datum" or lemma == "data" or lemma == "deep" or lemma == "machine":
                        bi_gram = lemma
                    else:
                        if lemma in word_dict:
                            word_dict[lemma] += 1
                        else:
                            word_dict[lemma] = 1
                else:
                    if bi_gram == "datum":
                        bi_gram = "data"
                    combind_word = bi_gram + "_" + lemma
                    if combind_word == "data_mining" or combind_word == "deep_learning" or combind_word == "machine_learning":
                        if combind_word in word_dict:
                            word_dict[combind_word] += 1
                        else:
                            word_dict[combind_word] = 1
                    bi_gram = ""

        counter += 1
        # print(counter)

    return word_dict


def find_num(word):
    return any(i.isdigit() for i in word)


if __name__ == '__main__':
    main()

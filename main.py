import requests
from bs4 import BeautifulSoup, Comment
import spacy
import math


def main():
    stop_words = load_stop_words()

    term_dict = {}

    urls = [
        "https://en.wikipedia.org/wiki/Machine_learning",
        "https://en.wikipedia.org/wiki/Engineering",
        "http://my.clevelandclinic.org/research",
        "https://en.wikipedia.org/wiki/Data_mining",
        "https://en.wikipedia.org/wiki/Data_mining#Data_mining",
        "http://cis.csuohio.edu/~sschung/"
    ]

    document_word_lengths = []

    index = 0

    for url in urls:

        soup = BeautifulSoup(requests.get(url).content, "html.parser")
        words = []

        for text in soup.find_all(string=True):
            if text.parent.name != 'script' and text.parent.name != 'style' and text.parent.name != 'img' and len(text) != 0 and text != "\n" and not isinstance(text, Comment):
                words.append(text)

        document_word_lengths.append(len(words))
        term_dict = parse_words(words, stop_words, term_dict, index + 1)
        index += 1

    write_search_term_freq(term_dict)
    write_term_freq(term_dict)

    tfidf_calculation(term_dict, urls, document_word_lengths)


def tfidf_calculation(terms, urls, document_word_lengths):
    keywords = [
        "research",
        "data",
        "mining",
        "analytics",
        "data_mining",
        "machine_learning",
        "deep_learning"
    ]

    tfidf_for_keywords = {}

    for word in sorted(terms.keys()):
        if word in keywords:
            tf = 0
            df = 0
            parsed = False
            for i in range(len(urls)):
                doc = str(i + 1)
                if doc in terms[word]:
                    tf = terms[word][doc] / document_word_lengths[i]
                else:
                    tf = 0
                df = math.log(len(urls) / len(terms[word]))
                if parsed:
                    tfidf_for_keywords[word][doc] = (tf * df)
                else:
                    tfidf_for_keywords[word] = {doc: (tf * df)}
                    parsed = True

    highest_score = 0
    winner = 0

    for i in range(len(urls)):
        score = 0
        for word in keywords:
            score += tfidf_for_keywords[word][str(i + 1)]
        print("tf-idf score for doc " + str(i + 1) + " is: " + str(score))
        if score > highest_score:
            winner = i + 1
            highest_score = score

    print("Document that is most suited for the keywords is doc#: " +
          str(winner) + " which is url " + urls[winner - 1])


def write_term_freq(terms):

    with open("terms.txt",  "w", encoding="utf-8") as f:

        f.write("Term\t\t\tDoc#\t\t\tFreq\n")

        for word in sorted(terms.keys()):
            for key in terms[word].keys():
                f.write(word + "\t\t\t" + str(key) + "\t\t\t" +
                        str(terms[word][str(key)]) + "\n")

    f.close()


def write_search_term_freq(terms):
    keywords = [
        "research",
        "data",
        "mining",
        "analytics",
        "data_mining",
        "machine_learning",
        "deep_learning"
    ]

    with open("search_terms.txt",  "w", encoding="utf-8") as f:

        f.write("Term\t\t\tDoc#\t\t\tFreq\n")

        for word in sorted(terms.keys()):
            if word in keywords:
                for key in terms[word].keys():
                    f.write(word + "\t\t\t" + str(key) + "\t\t\t" +
                            str(terms[word][str(key)]) + "\n")

    f.close()


def load_stop_words():
    stop_words = []

    with open("stop_word_list.txt") as f:
        lines = f.readlines()

        for line in lines:
            stop_words.append(line.strip('\n'))

        f.close()

    return stop_words


def add_to_dict(word_dict, doc_num, word):
    if word in word_dict:
        if str(doc_num) not in word_dict[word]:
            word_dict[word][str(doc_num)] = 1
        else:
            word_dict[word][str(doc_num)] += 1
    else:
        word_dict[word] = {str(doc_num): 1}

    return word_dict


def parse_words(list_of_words, stop_words, word_dict, doc_num):
    sp = spacy.load('en_core_web_sm')

    for words in list_of_words:

        sentence = sp(str(words))
        bi_gram = ""

        for word in sentence:
            lemma = word.lemma_

            if lemma == "datum":
                lemma = "data"

            if lemma == "analytic":
                lemma = "analytics"

            lemma = ''.join(i for i in str(lemma) if i.isalnum())
            lemma = lemma.lower()
            if len(lemma) > 0 and lemma not in stop_words and not find_num(lemma) and word.pos_ != "PUNCT" and word.pos_ != "SYM" and word.pos_ != "NUM":
                if len(bi_gram) == 0:
                    if lemma == "data" or lemma == "deep" or lemma == "machine":
                        bi_gram = lemma
                    word_dict = add_to_dict(word_dict, doc_num, lemma)
                else:
                    word_dict = add_to_dict(word_dict, doc_num, lemma)

                    combind_word = bi_gram + "_" + lemma

                    if combind_word == "data_mining" or combind_word == "deep_learning" or combind_word == "machine_learning":
                        word_dict = add_to_dict(
                            word_dict, doc_num, combind_word)
                    bi_gram = ""

    return word_dict


def find_num(word):
    return any(i.isdigit() for i in word)


if __name__ == '__main__':
    main()

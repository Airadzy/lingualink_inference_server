import requests
import logging
import spacy
import json
from bs4 import BeautifulSoup

log_filename = 'LinguaLink.log'
config_filename = "config.json"

logging.basicConfig(filename=log_filename,
                    format='%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s',
                    level=logging.INFO)

def split_json_file_content_into_lines(json_file_path):
    with open(json_file_path, 'r') as json_file:
        json_data = json.load(json_file)
    content = json_data.get("content", "")
    lines = content.split('\n')
    lines = [line.strip() for line in lines]
    lines = list(filter(None, lines))
    return lines
json_file_path = 'content.json'
lines = split_json_file_content_into_lines(json_file_path)

def load_config(config_filename):
    """
    Function to read json configuration file
    :param config_filename: the respective configuration file with key variables
    :return: json_dict that contains key variables
    """
    with open(config_filename, "r") as json_file:
        json_dict = json.load(json_file)
        return json_dict


def scrape_cambridge(words):
    results = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    for word in words:
        url = f"https://dictionary.cambridge.org/dictionary/english/{word}"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            difficulty_level = "Difficulty level not found"
            difficulty_span = soup.select_one(
                '.epp-xref.dxref.A1, .epp-xref.dxref.A2, .epp-xref.dxref.B1, .epp-xref.dxref.B2, .epp-xref.dxref.C1, .epp-xref.dxref.C2')
            if difficulty_span:
                difficulty_level = difficulty_span.get_text(strip=True)
            else:
                # Attempt to find difficulty level using the .gb.dgc class as a fallback
                difficulty_span_fallback = soup.select_one('.gc.dgc')
                if difficulty_span_fallback:
                    difficulty_level = difficulty_span_fallback.get_text(strip=True)
                else:
                    difficulty_level = "B"

            definition_div = soup.find('div', class_='def ddef_d db')
            definition = definition_div.text if definition_div else "Definition not found"

            results.append({"word": word, "difficulty_level": difficulty_level[0], "definition": definition})
        else:
            pass
    return results


def process_words(sentence):
    """

    :param sentence: input phrase
    :return:
    """

    nlp = spacy.load("en_core_web_sm")

    lemmatized_words = []
    doc = nlp(sentence)
    for token in doc:
        lemmatized_words.append(token.lemma_)
    words_list = list(set(lemmatized_words))
    return words_list


def filter_difficulty_level(word_dictionaries):
    list_A = []
    list_B = []
    list_C = []
    for dict in word_dictionaries:
        if dict["difficulty_level"] == "A":
            list_A.append(dict)
        if dict["difficulty_level"] == "B":
            list_B.append(dict)
        if dict["difficulty_level"] == "C":
            list_C.append(dict)
    return list_A, list_B, list_C


def final_list(level, list_A, list_B, list_C):
    if level == "A" and len(list_A) >= 10:
        return list_A
    elif level == "A" and len(list_A) < 10:
        return list_A + list_B
    elif level == "B" and len(list_B) >= 10:
        return list_B
    else:
        return list_B + list_C


def main():
    """
    main function running script
    :return:
    """
    config = load_config(config_filename)
    example = "eating eats eat ate adjustable rafting ability meeting better hello film movie radio"
    words_list = process_words(example)
    word_dictionary_list = scrape_cambridge(words_list)
    list_A, list_B, list_C = filter_difficulty_level(word_dictionary_list)
    processed_list = final_list("B", list_A, list_B, list_C)


if __name__ == "__main__":
    main()

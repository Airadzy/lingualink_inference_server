import requests
import logging
import spacy
import json
from bs4 import BeautifulSoup
import re
import multiprocessing
import pandas as pd
import random

log_filename = 'LinguaLink.log'
config_filename = "config.json"

logging.basicConfig(filename=log_filename,
                    format='%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s',
                    level=logging.INFO)


def load_config(config_filename):
    """
    Function to read json configuration file
    :param config_filename: the respective configuration file with key variables
    :return: json_dict that contains key variables
    """
    with open(config_filename, "r") as json_file:
        json_dict = json.load(json_file)
        return json_dict


def get_difficulty_level(json_file_path):
    with open(json_file_path, 'r') as json_file:
        json_content = json.load(json_file)
        difficulty_level = json_content.get("difficulty", "")
    return difficulty_level


def split_json_file_content_into_lines(json_file_path):
    with open(json_file_path, 'r') as json_file:
        json_data = json.load(json_file)
        json_article = json_data.get("article", "")
        json_article = re.sub(r'[^\w\s-]', '', json_article).lower()
        words = re.findall(r'\b\w+\b', json_article)
        unique_words = list(set(words))
    return unique_words


def scrape_word(word):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    url = f"https://dictionary.cambridge.org/dictionary/english/{word}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:

        soup = BeautifulSoup(response.content, 'html.parser')
        definition_div = soup.find('div', class_='def ddef_d db')
        if definition_div:
            definition = definition_div.text

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
                    return {"word": word, "difficulty_level": difficulty_level, "definition": definition}


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def process_words(words):
    """

    :param sentence: input phrase
    :return:
    """

    nlp = spacy.load("en_core_web_sm")

    lemmatized_words = []
    for batch_words in chunks(words, 100):
        doc = nlp(" ".join(batch_words))
        lemmatized_words.extend([token.lemma_ for token in doc if not token.is_stop and len(token.lemma_)>2])
    unique_words_list = list(set(lemmatized_words))
    return unique_words_list


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


def find_ten_most_frequent_words(list_dict_words_from_api):
    # 'count' is the frequency
    kaggle_df = pd.read_csv('unigram_freq.csv')
    dict_df = pd.DataFrame(list_dict_words_from_api)

    # to match to the Kaggle's dataset
    dict_df["word"] = dict_df["word"].str.lower()

    matched_df = pd.merge(dict_df, kaggle_df, on="word", how="left")

    matched_df["count"] = matched_df["count"].fillna(0)

    sorted_df = matched_df.sort_values(by='count', ascending=False)
    sorted_filtered_df = sorted_df.drop('count', axis=1)

    # Save the top 10 words to a variable
    top_10_words_df = sorted_filtered_df.head(10)

    # Return back to a list of dictionaries
    dict_10_frequent_words = top_10_words_df.to_dict(orient="records")
    return dict_10_frequent_words

def generate_quiz_json(short_list,long_list,filename):
    quiz=[]
    long_definitions = [d['definition'] for d in long_list]

    for item in short_list:
        word = item["word"]
        correct_definition = item["definition"]

        options = random.sample([d for d in long_definitions if d != correct_definition], 3)
        options.append(correct_definition)
        random.shuffle(options)

        quiz.append({
            'word': word,
            'options': options,
            'correct': correct_definition
        })

    return quiz


def model(json_file_path):
    """
    main function running script
    :return:
    """

    unique_words = split_json_file_content_into_lines(json_file_path)
    difficulty_level = get_difficulty_level(json_file_path)
    # config = load_config(config_filename)
    words = process_words(unique_words)
    # print("words", words)
    with multiprocessing.Pool() as pool:
        word_dictionary_list = pool.map(scrape_word, words)
        word_dictionary_list = [word_dict for word_dict in word_dictionary_list if word_dict is not None]

    # print("word dictionary list", word_dictionary_list)
    list_A, list_B, list_C = filter_difficulty_level(word_dictionary_list)
    processed_list = final_list(difficulty_level, list_A, list_B, list_C)
    # print(processed_list)
    dict_10_frequent_words = find_ten_most_frequent_words(processed_list)
    json_file = generate_quiz_json(dict_10_frequent_words, processed_list, "quiz.json")
    return json_file
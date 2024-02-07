import pandas as pd

kaggle_df = pd.read_csv('unigram_freq.csv')


def find_10_most_frequent_words(list_dict_words_from_api):
    # 'count' is the frequency
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
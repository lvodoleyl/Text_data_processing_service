from random import random


def run_fcm(texts: dict, count_clusters: int) -> dict:
    res = {}
    for id, text in texts.items():
        # compute clustering
        res[id] = {'clusters': {}, 'text': text}
        for cluster in range(count_clusters):
            res[id]['clusters'][cluster] = random()
    return res


def get_importance_word(texts_and_clusters: dict) -> str:
    # compute
    return 'word1 word2 word3'


def get_importance_word_topic_modeling(texts: list) -> str:
    # compute
    return 'word1 word2 word3'

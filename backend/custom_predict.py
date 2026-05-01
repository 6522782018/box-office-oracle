import pandas as pd

DEFAULT_SENTIMENT = 52.76

FEATURE_COLS = [
    "TargetSequelNo", "HistoryLen",
    "prev_gross", "prev_budget", "prev_sentiment", "prev_imdb",
    "avg_gross", "avg_budget", "avg_sentiment", "avg_imdb",
    "trend_gross", "trend_budget", "trend_sentiment", "trend_imdb"
]


def build_custom_features(movies):
    """
    Build the same feature format used by the trained model,
    but use default sentiment because users do not know sentiment score.
    """

    if not movies or len(movies) < 2:
        raise ValueError("Please enter at least 2 previous movies.")

    gross = [float(m["gross"]) for m in movies]
    budget = [float(m["budget"]) for m in movies]
    imdb = [float(m["imdb"]) for m in movies]

    sentiment = [DEFAULT_SENTIMENT for _ in movies]

    history_len = len(movies)
    target_sequel_no = history_len + 1

    row = pd.DataFrame([{
        "TargetSequelNo": target_sequel_no,
        "HistoryLen": history_len,

        "prev_gross": gross[-1],
        "prev_budget": budget[-1],
        "prev_sentiment": sentiment[-1],
        "prev_imdb": imdb[-1],

        "avg_gross": sum(gross) / len(gross),
        "avg_budget": sum(budget) / len(budget),
        "avg_sentiment": sum(sentiment) / len(sentiment),
        "avg_imdb": sum(imdb) / len(imdb),

        "trend_gross": gross[-1] - gross[0],
        "trend_budget": budget[-1] - budget[0],
        "trend_sentiment": sentiment[-1] - sentiment[0],
        "trend_imdb": imdb[-1] - imdb[0],
    }])

    return row[FEATURE_COLS]
from tcgbot.keywords import next_keyword

KEYWORDS = ["Pokemon TCG", "Pokemon booster box", "Pokemon ETB"]


def test_all_keywords_appear_before_any_repeats(tmp_path):
    state_path = tmp_path / "keywords_state.json"
    seen = [next_keyword(KEYWORDS, state_path) for _ in range(len(KEYWORDS))]
    assert sorted(seen) == sorted(KEYWORDS)


def test_reshuffles_after_exhausting_the_list(tmp_path):
    state_path = tmp_path / "keywords_state.json"
    first_round = [next_keyword(KEYWORDS, state_path) for _ in range(len(KEYWORDS))]
    second_round = [next_keyword(KEYWORDS, state_path) for _ in range(len(KEYWORDS))]
    assert sorted(first_round) == sorted(second_round) == sorted(KEYWORDS)
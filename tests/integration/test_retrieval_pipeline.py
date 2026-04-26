from src.retrieval.ranking import Ranking


def test_ranking_and_deduplication():
    results = [
        {"id": "a", "score": 0.5},
        {"id": "b", "score": 0.9},
        {"id": "a", "score": 0.6},
    ]

    ranked = Ranking.rank_results(results)
    assert ranked[0]["id"] == "b"

    deduped = Ranking.deduplicate_results(ranked)
    assert len(deduped) == 2
    assert deduped[0]["id"] == "b"

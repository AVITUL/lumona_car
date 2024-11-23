# this file is to only evaluate the retrieval quality of our technique. no prod implications.

from typing import List


class EvalRetrieval:
    def __init__(self, model: str, dataset: str, split: str):
        # choose a few random paragraphs as inputs.
        # fetch questions that can be answered exclusively from the retrieved paragraphs.
        # fetch questions that may contain information from other paragraphs.
        # do the retrieval
        # match paragraphs.
        pass

    def _choose_random_paragraphs(
        self, dataset: str, split: str, num_paragraphs: int
    ) -> List[str]:
        pass

    def _fetch_questions(self, paragraphs: List[str]) -> List[str]:
        pass

    def _do_retrieval(self, questions: List[str], model: str) -> List[str]:
        pass

    def _match_paragraphs(
        self, retrieved_paragraphs: List[str], paragraphs: List[str]
    ) -> List[str]:
        pass

    def _evaluate_retrieval(
        self, matched_paragraphs: List[str], paragraphs: List[str]
    ) -> float:
        pass

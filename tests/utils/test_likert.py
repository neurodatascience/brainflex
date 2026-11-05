import pytest

from brainflex.utils.likert import label_likert_answer

LABELS = ("a", "b", "c", "d", "e")


class TestLabelLikertAnswer:
    @pytest.mark.parametrize(
        ("answer", "expected"), [("1", "1 (a)"), (3, "3 (c)"), ("5", "5 (e)")]
    )
    def test_label(self, answer: str | int, expected: str):
        assert label_likert_answer(answer, LABELS) == expected

    @pytest.mark.parametrize("answer", ["0", "6", 6, "", "a"])
    def test_invalid_answer(self, answer: str | int):
        with pytest.raises(ValueError, match="must be one of"):
            label_likert_answer(answer, LABELS)

    @pytest.mark.parametrize("labels", [LABELS[:4], (*LABELS, "f")])
    def test_wrong_number_of_labels(self, labels: tuple[str, ...]):
        with pytest.raises(ValueError, match="Expected 5 labels"):
            label_likert_answer("1", labels)

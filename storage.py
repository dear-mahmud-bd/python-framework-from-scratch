from models import Question

class QuestionStorage:
    _id = 0

    def __init__(self):
        self._questions = []

    def all(self):
        return [question._asdict() for question in self._questions]

    def get(self, id: int):
        for question in self._questions:
            if question.id == id:
                return question
        return None

    def create(self, **kwargs):
        self._id += 1
        kwargs["id"] = self._id
        question = Question(**kwargs)
        self._questions.append(question)
        return question

    def delete(self, id: int):
        for ind, question in enumerate(self._questions):
            if question.id == id:
                del self._questions[ind]
                return True
        return False
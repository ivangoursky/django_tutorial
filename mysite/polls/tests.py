from django.test import TestCase

import datetime
from django.utils import timezone
from .models import Question, Choice
from django.urls import reverse

def create_question(question_text, dt, choices):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + dt
    q = Question(question_text=question_text, pub_date=time)
    q.save()
    for ch_text in choices:
        c = Choice(question = q, choice_text=ch_text,votes=0)
        c.save()
    print(q.choice_set.all())
    return q

class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        create_question(question_text="Past question.", dt=datetime.timedelta(days=-30),
                        choices=["Choice 1", "Choice 2"])
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", dt=datetime.timedelta(days=30),
                        choices=["Choice 1", "Choice 2"])
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        create_question(question_text="Past question.", dt=datetime.timedelta(days=-30),
                        choices=["Choice 1", "Choice 2"])
        create_question(question_text="Future question.", dt=datetime.timedelta(days=30),
                        choices=["Choice 1", "Choice 2"])
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        create_question(question_text="Past question 1.", dt=datetime.timedelta(days=-30),
                        choices=["Choice 1", "Choice 2"])
        create_question(question_text="Past question 2.", dt=datetime.timedelta(days=-5), choices=["Choice 1", "Choice 2"])
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )

    def test_question_with_no_choices(self):
        """
        Questions with no choices aren't displayed on
        the index page.
        """
        create_question(question_text="Question with no choices", dt=datetime.timedelta(days=-1), choices=[])
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text='Future question.', dt=datetime.timedelta(days=5),
                                          choices=["Choice 1", "Choice 2"])
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past Question.', dt=datetime.timedelta(days=-5),
                                        choices=["Choice 1", "Choice 2"])
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_question_with_no_choices(self):
        """
        The detail view of a question with no choices
        returns a 404 not found.
        """
        question = create_question(question_text="Question with no choices", dt=datetime.timedelta(days=-1), choices=[])
        url = reverse('polls:detail', args=(question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

class QuestionResultsViewTests(TestCase):
    def test_future_question(self):
        """
        The results view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text='Future question.', dt=datetime.timedelta(days=5),
                                          choices=["Choice 1", "Choice 2"])
        url = reverse('polls:results', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The results view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past Question.', dt=datetime.timedelta(days=-5),
                                        choices=["Choice 1", "Choice 2"])
        url = reverse('polls:results', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_question_with_no_choices(self):
        """
        The results view of a question with no choices
        returns a 404 not found.
        """
        question = create_question(question_text="Question with no choices", dt=datetime.timedelta(days=-1), choices=[])
        url = reverse('polls:results', args=(question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date is in the future.
        """
        future_question = create_question(question_text="Test question from the future.",
                                    dt=datetime.timedelta(days=30),
                                    choices=["Choice 1", "Choice 2"])
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions older than 1 day.
        """
        old_question = create_question(question_text="Test question older than 1 day.",
                                    dt = -datetime.timedelta(days=1,seconds=1),
                                    choices=["Choice 1", "Choice 2"])
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions, whose pub_date is within a day.
        """
        recent_question = create_question(question_text="Test question published within 1 day.",
                                    dt= -datetime.timedelta(hours=23,minutes=59,seconds=59),
                                    choices=["Choice 1", "Choice 2"])
        self.assertIs(recent_question.was_published_recently(), True)

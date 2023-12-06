from flex_prompt import Flex, Cat, target
from test_helpers import infinite

def test_flex():
  render = target('test-len-str')
  assert render(Flex([
    infinite('A'),
    infinite('B'),
    infinite('C'),
  ]), max_tokens=12).output == 'AAAABBBBCCCC'  

  assert render(Flex([
    infinite('A'),
    Cat(infinite('B'), flex_weight=2),
    infinite('C'),
  ]), max_tokens=12).output == 'AAABBBBBBCCC'


def test_flex_separator():
  render = target('test-len-str')
  assert render(Flex([
    infinite('A'),
    Cat(infinite('B'), flex_weight=2),
    infinite('C'),
  ], join='--'), max_tokens=12).output == 'AA--BBBB--CC'

from dataclasses import dataclass
from flex_prompt import Flexed, Expect

def test_flexed(snapshot):
  @dataclass
  class Ask(Flexed):
    """Given a text, answer a question."""
    text: str
    question: str
    answer: str | Expect = Expect(str)

    flex_join = '\n'
    def content(self, _ctx):
      yield 'Given the text, answer the question.'
      yield ''
      yield 'Text:'
      yield self.text
      yield 'Question: ', self.question
      yield 'Answer: ', self.answer
  render = target('test-len-str')
  rendering = render(Ask(infinite('tk'), 'What is to come?'), token_limit=200)
  assert rendering.output == '''Given the text, answer the question.

Text:
tktktktktktktktktktktktktktktktktktktktktktktktktktktktktktktktk
Question: What is to come?
Answer: '''
  assert rendering.max_response_tokens == 56

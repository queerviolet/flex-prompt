from flexprompt import Flex, Cat
from .test_helpers import render, infinite

def test_flex():
  assert render(Flex([
    infinite('A'),
    infinite('B'),
    infinite('C'),
  ]), max_tokens=6).output == 'AABBCC'

  assert render(Flex([
    infinite('A'),
    Cat(infinite('B'), flex_weight=2),
    infinite('C'),
  ]), max_tokens=8).output == 'AABBBBCC'


def test_flex_separator():
  assert render(Flex([
    infinite('A'),
    Cat(infinite('B'), flex_weight=2),
    infinite('C'),
  ], separator='--'), max_tokens=12).output == 'AA--BBBB--CC'

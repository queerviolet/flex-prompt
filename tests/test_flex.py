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

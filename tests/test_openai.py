from flex_prompt import render
from test_helpers import infinite

def test_gpt_35():
  output = render(infinite('A'), model='gpt-3.5-turbo')
  assert len(output.tokens) == 4097

def test_gpt_4():
  output = render(infinite('A'), model='gpt-4')
  assert len(output.tokens) == 8192
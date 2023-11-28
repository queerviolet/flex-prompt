from flex_prompt import render
from test_helpers import infinite
from langchain.llms import OpenAI

def test_lc_gpt35():
  out = render(infinite('A'), model=OpenAI(model='gpt-3.5-turbo', openai_api_key='XXXX'))
  assert len(out.tokens) == 4097
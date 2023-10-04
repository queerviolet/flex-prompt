from renderer.renderer import Renderer
from renderable import Flex, Cat
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI

def infinite(s):
  while True:
    yield s

flexed = Renderer.for_model(OpenAI()).with_max_tokens(100).render(Flex([
  Cat(infinite('A')),
  Cat(infinite('B'), flex_weight=2),
  Cat(infinite('C')),
]))
print(flexed.output, flexed.token_count)

chat = Renderer.for_model(ChatOpenAI()).with_max_tokens(100).render(Flex([
  {'role': 'system', 'content': Cat(['A']*100000)},
  Cat(['B']*100000, flex_weight=4),
  Cat(['C']*100000),
]))
print(chat.output)
print(chat._history)



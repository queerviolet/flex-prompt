from renderer.renderer import Renderer
from renderable import Flex, Cat
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI


flexed = Renderer.for_model(OpenAI()).with_max_tokens(100).render(Flex([
  Cat(['A']*100000),
  Cat(['B']*100000, flex_weight=4),
  Cat(['C']*100000),
]))
print(flexed.output)

chat = Renderer.for_model(ChatOpenAI()).with_max_tokens(100).render(Flex([
  Cat(['A']*100000),
  Cat(['B']*100000, flex_weight=4),
  Cat(['C']*100000),
]))
print(chat.output)



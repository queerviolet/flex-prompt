from .renderer import Renderer, StrRenderer

try:
  from langchain.llms import OpenAI
  import tiktoken

  @Renderer.register
  class OpenAIRenderer(StrRenderer):
    model_class = OpenAI

    MAX_TOKENS = {
      'gpt-4': 8192,
      'gpt-4-0613': 8192,
      'gpt-4-32k': 32768,
      'gpt-4-32k-0613': 32768,
      'gpt-4-0314': 8192,
      'gpt-4-32k-0314': 32768,
      'gpt-3.5-turbo': 4097,
      'gpt-3.5-turbo-16k': 16385,
      'gpt-3.5-turbo-instruct': 4097,
      'gpt-3.5-turbo-0613': 4097,
      'gpt-3.5-turbo-16k-0613': 16385,
      'gpt-3.5-turbo-0301': 4097,
      'text-davinci-003': 4097,
      'text-davinci-002': 4097,
      'code-davinci-002': 8001,
      'babbage-002': 16384,
      'davinci-002': 16384,
      'text-curie-001': 2049,
      'text-babbage-001': 2049,
      'text-ada-001': 2049,
      'davinci': 2049,
      'curie': 2049,
      'babbage': 2049,
      'ada': 2049
    }

    @classmethod
    def for_model(Self, llm):
      return Self.for_model_name(llm.model_name)

    @classmethod
    def for_model_name(Self, model_name):
      return Self(model_name=model_name,
        tokenizer=tiktoken.encoding_for_model(model_name),
        max_tokens=Self.MAX_TOKENS[model_name])

  # from langchain.schema import ChatMessage
  # from langchain.chat_models import ChatOpenAI

  # @Renderer.register
  # class ChatOpenAIRenderer(ChatRenderer):
  #   model_class = ChatOpenAI
  #   str_renderer_class = OpenAIRenderer
  #   output_type = list[ChatMessage]

  #   @classmethod
  #   def for_model(Self, llm):
  #     return Self.for_model_name(llm.model_name)

  #   @classmethod
  #   def for_model_name(Self, model_name):
  #     return Self(model_name=model_name,
  #       tokenizer=tiktoken.encoding_for_model(model_name),
  #       max_tokens=OpenAIRenderer.MAX_TOKENS[model_name])  
except ImportError: pass
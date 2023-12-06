from .. import register_target_finder, Target
from ..rendering import Str

@register_target_finder
def openai_models(model):
  if isinstance(model, str) and model in MAX_TOKENS:
    import tiktoken
    return Target(tokenizer=tiktoken.encoding_for_model(model),
      max_tokens=MAX_TOKENS[model],
      rendering_type=Str)
  model_name = getattr(model, 'model_name', None)
  if not model_name: model_name = getattr(model, 'model_name_or_path', None)
  if model_name: return openai_models(model_name)
  return None

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

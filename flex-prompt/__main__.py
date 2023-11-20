from renderer.renderer import Renderer
from flexprompt.cat import Cat, Flex

from langchain.llms import OpenAI

renderer = Renderer.for_model(OpenAI(model='gpt-3.5-turbo'))
#print(renderer.render('hello world'))

#print(renderer.render(['hello', 'world']))

smol = renderer.with_max_tokens(100)
print(smol.render(Flex([
  ['x'*1000],
  ['y'*1000],
  ['z'*1000],
  ['hello world', 'my only friend', 'we meet again', 'for yet more time', 'but we all dine', 'in the end'],
  ['hello world', 'my only friend', 'we meet again', 'for yet more time', 'but we all dine', 'in the end'],
  ['hello world', 'my only friend', 'we meet again', 'for yet more time', 'but we all dine', 'in the end'],
])))
#print(smol.render('hello world my only friend we meet again'))

from langchain.chat_models import ChatOpenAI
from langchain.schema import ChatMessage
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

template = ChatPromptTemplate.from_messages([  
  ChatMessage(role='system', content='Reply with one message containing all the things the-red-baron has said in this conversation (and only those things).'),
  ChatMessage(role='user', name='the-red-baron', content='When did the dodgers last win the world series?'),
  ChatMessage(role='user', content='Why is the ground brown?'),
  ChatMessage(role='user', name='the-red-baron', content='Why is the sky blue?'),
  ChatMessage(role='user', content='When did Beyonce?')
])

chain = LLMChain(llm=ChatOpenAI(model='gpt-3.5-turbo-0613'), prompt=template)
print(chain.generate([template]))

from json import dumps

print('nt=', ChatOpenAI(model='gpt-3.5-turbo-0613').get_num_tokens_from_messages([  
  ChatMessage(role='system', content='You are a friendly, helpful assistant.'),
  ChatMessage(role='user', content='When did the dodgers last win the world series?')  
]))

import tiktoken
cl100k_base = tiktoken.get_encoding('cl100k_base')
enc = tiktoken.Encoding(
    # If you're changing the set of special tokens, make sure to use a different name
    # It should be clear from the name what behaviour to expect.
    name="cl100k_im",
    pat_str=cl100k_base._pat_str,
    mergeable_ranks=cl100k_base._mergeable_ranks,
    special_tokens={
        **cl100k_base._special_tokens,
        "<|im_start|>": 100264,
        "<|im_end|>": 100265,
    },
)

print('tiktoken token encoding=', len(enc.encode('''<|im_start|>system
You are a friendly, helpful assistant.<|im_end|>
<|im_start|>name=the-red-baron
When did the dodgers last win the world series?<|im_end|>\n<|im_start|>''', allowed_special=set(['<|im_start|>', '<|im_end|>']))))

import openai

msgs = [
    {"role": "system", "content": "the_red_baron: When did the dodgers last win the world series?"},
    {"role": "user", "content": "Why is the sky blue?"},
    {"role": "system", "content": "the_red_baron: Why is the sky green?"},
    {"role": "user", "content": "Why did Beyonce?"},
    {"role": "system", "content": "Reply with one message containing all the things the_red_barron has said in this conversation (and only those things)."},
  ]
completion = openai.ChatCompletion.create(model="gpt-3.5-turbo-0613", messages=msgs)
print(completion)
print(ChatOpenAI(model="gpt-3.5-turbo-0613").get_num_tokens_from_messages([
  ChatMessage(**m) for m in msgs
]))

def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613"):
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
        return num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens

print(num_tokens_from_messages(msgs))
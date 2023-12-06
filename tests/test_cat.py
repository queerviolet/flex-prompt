from flex_prompt import Cat, render
one = """
and lo betide, the red sky opened upon us as though the crinkled
hand of the heavens itself was reaching down.
"""
two = """
we were witness to dark and terrible portents, whose nameless
features we could not grasp with our mortal minds
"""
three = """
it was only then, in the moment when cruel stars had long since
wrung us dry, that the chinchillas arrived.
"""

def test_cat_block():
  assert render(Cat([one, two, three]),
                model='test-len-str',
                token_limit=200).output == one

def test_cat_clip():
  rendering = render(Cat([one, two, three], mode='clip'),
                     model='test-len-str',
                     token_limit=200)
  assert rendering.output == (one + two)[:200]
  assert rendering.overflow_token_count == len(one) + len(two) - 200

def test_cat_join_clip():
  rendering = render(Cat([one, two, three], mode='clip', join='---'),
                     model='test-len-str',
                     token_limit=200)
  assert rendering.output == (one + '---' + two)[:200]  

def test_cat_join_block():
  rendering = render(Cat([one, two, three], mode='block', join='---'),
                     model='test-len-str',
                     token_limit=len(one) + len(two) + int(0.5 * len(three)))                     
  assert rendering.output == (one + '---' + two)

def test_cat_clip_if_big():
  """
  Cat mode='block' should fall back to clipping if it
  encounters an item too large to ever be rendered.
  """
  rendering = render(Cat('a', ['x' * 1000], mode='block'),
                     model='test-len-str',
                     token_limit=10)
  assert rendering.output == 'axxxxxxxxx'
  rendering = render(Cat('a', ['0123456789'], mode='block'),
                    model='test-len-str',
                    token_limit=10)
  assert rendering.output == 'a'
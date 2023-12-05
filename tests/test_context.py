from flex_prompt import render, Render

def test_ctx_tokens_remaining():
  def test_item(render: Render):
    yield render.tokens_remaining
    yield render.tokens_remaining
    assert render.tokens_remaining == 193
  assert render(test_item, model='test-len-str', max_tokens=199).output == '199196'

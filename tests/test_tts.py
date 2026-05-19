from bot.services.tts import clean_text_for_tts


class TestCleanTextForTts:
    def test_removes_code_blocks(self):
        text = "Here is code:\n```python\nprint('hello')\n```\nDone."
        result = clean_text_for_tts(text)
        assert "```" not in result
        assert "print" not in result
        assert "Done." in result

    def test_removes_inline_code(self):
        text = "Use `variable_name` here."
        result = clean_text_for_tts(text)
        assert "`" not in result
        assert "variable_name" in result

    def test_removes_links(self):
        text = "Visit [OpenCode](https://opencode.ai) for docs."
        result = clean_text_for_tts(text)
        assert "[" not in result
        assert "](" not in result
        assert "OpenCode" in result

    def test_removes_images(self):
        text = "See ![logo](https://example.com/logo.png) above."
        result = clean_text_for_tts(text)
        assert "![" not in result
        assert "logo" in result

    def test_removes_headers(self):
        text = "## Section Title\nSome content here."
        result = clean_text_for_tts(text)
        assert "##" not in result
        assert "Section Title" in result

    def test_removes_bold(self):
        text = "This is **important** text."
        result = clean_text_for_tts(text)
        assert "**" not in result
        assert "important" in result

    def test_removes_italic(self):
        text = "This is *emphasized* text."
        result = clean_text_for_tts(text)
        assert "*" not in result
        assert "emphasized" in result

    def test_removes_blockquotes(self):
        text = "> This is a quote.\nNormal text."
        result = clean_text_for_tts(text)
        assert ">" not in result
        assert "This is a quote." in result

    def test_removes_list_items(self):
        text = "- Item one\n- Item two\nNormal text."
        result = clean_text_for_tts(text)
        assert "Item one" in result
        assert "- " not in result.split("Normal")[0]

    def test_preserves_punctuation(self):
        text = "Hello, world! How are you? I'm fine."
        result = clean_text_for_tts(text)
        assert "," in result
        assert "!" in result
        assert "?" in result
        assert "'" in result

    def test_strips_whitespace(self):
        text = "  Hello  world  "
        result = clean_text_for_tts(text)
        assert result == "Hello world"

    def test_complex_markdown(self):
        text = """# Title

This is **bold** and *italic* text.

```python
def hello():
    pass
```

- [Link](https://example.com)
- List item

> A quote

Done!
"""
        result = clean_text_for_tts(text)
        assert "#" not in result
        assert "**" not in result
        assert "```" not in result
        assert "](" not in result
        assert "Done!" in result

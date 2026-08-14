import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


def _load_guardian_module():
    dotenv_mock = types.ModuleType("dotenv")
    dotenv_mock.load_dotenv = lambda: None
    module_path = Path(__file__).resolve().parents[1] / "guardian_v1.py"
    spec = importlib.util.spec_from_file_location("guardian_v1_under_test", module_path)
    module = importlib.util.module_from_spec(spec)

    with patch.dict(sys.modules, {"dotenv": dotenv_mock}):
        spec.loader.exec_module(module)

    return module


guardian = _load_guardian_module()


class DomSanitizationTests(unittest.TestCase):
    def test_removes_form_values_and_preserves_selector_metadata(self):
        html = """
        <form>
          <input id="email" class="field primary" name="email" role="textbox"
                 aria-label="Email address" data-testid="email-input" type="email"
                 value="person@example.test">
          <input id="csrf" name="csrf_token" type="hidden" value="csrf-secret-value">
          <textarea id="notes" name="notes">Private notes</textarea>
          <option value="private-option" selected>Visible option</option>
          <button id="save" class="action" data-testid="save-button" value="save-action">Save changes</button>
          <output>Private output</output>
          <div contenteditable="true">Private editable text</div>
        </form>
        """

        sanitized = guardian._sanitize_dom_for_prompt(html)

        self.assertNotIn("person@example.test", sanitized)
        self.assertNotIn("csrf-secret-value", sanitized)
        self.assertNotIn("Private notes", sanitized)
        self.assertNotIn("Private output", sanitized)
        self.assertNotIn("Private editable text", sanitized)
        self.assertIn('id="email"', sanitized)
        self.assertIn('class="field primary"', sanitized)
        self.assertIn('name="email"', sanitized)
        self.assertIn('role="textbox"', sanitized)
        self.assertIn('aria-label="Email address"', sanitized)
        self.assertIn('data-testid="email-input"', sanitized)
        self.assertIn('type="email"', sanitized)
        self.assertIn("Visible option", sanitized)
        self.assertIn("Save changes", sanitized)
        self.assertIn('value="save-action"', sanitized)
        self.assertNotIn('value="private-option"', sanitized)
        self.assertNotIn("selected", sanitized)

    def test_removes_script_and_style_and_masks_sensitive_data(self):
        html = """
        <script>const access_token = 'script-secret';</script>
        <style>.private { color: red; }</style>
        <div data-token="attribute-secret">Authorization: Bearer bearer-secret</div>
        <a href="/account?token=url-secret&amp;view=profile">Account</a>
        """

        sanitized = guardian._sanitize_dom_for_prompt(html)

        self.assertNotIn("script-secret", sanitized)
        self.assertNotIn(".private", sanitized)
        self.assertNotIn("attribute-secret", sanitized)
        self.assertNotIn("bearer-secret", sanitized)
        self.assertNotIn("url-secret", sanitized)
        self.assertNotIn("<script", sanitized)
        self.assertNotIn("<style", sanitized)
        self.assertIn("[REDACTED]", sanitized)

    def test_redacts_quoted_json_style_sensitive_keys(self):
        html = """
        <div data-context='{"token":"synthetic-json-token","api_key": "synthetic-json-key"}'></div>
        <div>{'authorization': 'Bearer synthetic-json-authorization'}</div>
        """

        sanitized = guardian._sanitize_dom_for_prompt(html)

        self.assertNotIn("synthetic-json-token", sanitized)
        self.assertNotIn("synthetic-json-key", sanitized)
        self.assertNotIn("synthetic-json-authorization", sanitized)
        self.assertIn("[REDACTED]", sanitized)

    def test_redacts_escaped_quoted_json_style_sensitive_values(self):
        html = r'''
        <div>{"token":"synthetic-quote-abc\"def"}</div>
        <div>{"token":"synthetic-backslash-abc\\def"}</div>
        <div>{'token':'synthetic-single-abc\'def'}</div>
        <div data-context='{"token":"synthetic-attribute-abc\"def"}'></div>
        '''

        sanitized = guardian._sanitize_dom_for_prompt(html)

        for fragment in (
            "synthetic-quote-abc",
            "synthetic-backslash-abc",
            "synthetic-single-abc",
            "synthetic-attribute-abc",
            "def",
        ):
            self.assertNotIn(fragment, sanitized)
        self.assertIn("[REDACTED]", sanitized)

    def test_enforces_dom_size_limit_and_marks_truncation(self):
        html = "<div data-testid=\"large-dom\">" + ("x" * (guardian.MAX_DOM_PROMPT_CHARS + 100)) + "</div>"

        sanitized = guardian._sanitize_dom_for_prompt(html)

        self.assertLessEqual(len(sanitized), guardian.MAX_DOM_PROMPT_CHARS)
        self.assertTrue(sanitized.endswith("<!-- DOM truncated before AI submission -->"))


if __name__ == "__main__":
    unittest.main()

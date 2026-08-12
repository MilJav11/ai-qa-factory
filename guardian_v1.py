import os
import json
import requests
import re
from html import escape
from html.parser import HTMLParser
from dotenv import load_dotenv

load_dotenv()

MAX_DOM_PROMPT_CHARS = 100_000
_TRUNCATION_MARKER = "\n<!-- DOM truncated before AI submission -->"
_FORM_VALUE_TAGS = ("input", "textarea", "select", "option", "output")
_SENSITIVE_ATTRIBUTE_RE = re.compile(
    r"(?:password|passwd|pwd|token|secret|cookie|authorization|auth|"
    r"api[_-]?key|session|csrf)",
    re.IGNORECASE,
)
_SENSITIVE_ASSIGNMENT_RE = re.compile(
    r"(?i)\b(?P<name>password|passwd|pwd|token|access[_-]?token|"
    r"id[_-]?token|refresh[_-]?token|api[_-]?key|secret|cookie|"
    r"set-cookie|authorization|session(?:id)?|csrf)\b\s*[:=]\s*"
    r"(?P<value>\"[^\"]*\"|'[^']*'|[^\s<]+)"
)
_AUTH_SCHEME_RE = re.compile(
    r"(?i)\b(?P<scheme>bearer|basic)\s+[A-Za-z0-9._~+/=-]+"
)
_SENSITIVE_QUERY_PARAM_RE = re.compile(
    r"(?i)([?&](?:token|access_token|id_token|api_key|key|"
    r"session|password|authorization)=)[^&#\s\"']+"
)
_VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


def _redact_sensitive_text(value: str) -> str:
    value = _AUTH_SCHEME_RE.sub(
        lambda match: f"{match.group('scheme')} [REDACTED]", value
    )
    value = _SENSITIVE_ASSIGNMENT_RE.sub(
        lambda match: f"{match.group('name')}=[REDACTED]", value
    )
    return _SENSITIVE_QUERY_PARAM_RE.sub(r"\1[REDACTED]", value)


class _DomPromptSanitizer(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.output = []
        self.skip_depth = 0
        self.clear_content_depth = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if self.skip_depth:
            if tag not in _VOID_TAGS:
                self.skip_depth += 1
            return
        if tag in ("script", "style"):
            self.skip_depth = 1
            return

        sanitized_attrs = []
        clears_content = False
        already_clearing_content = self.clear_content_depth > 0
        if already_clearing_content and tag not in _VOID_TAGS:
            self.clear_content_depth += 1
        for attribute_name, attribute_value in attrs:
            attribute_name = attribute_name.lower()
            if attribute_name == "style":
                continue
            if tag in _FORM_VALUE_TAGS and attribute_name in ("value", "selected"):
                continue
            if _SENSITIVE_ATTRIBUTE_RE.search(attribute_name):
                attribute_value = "[REDACTED]"
            elif attribute_value is not None:
                attribute_value = _redact_sensitive_text(attribute_value)
            if attribute_name == "contenteditable":
                clears_content = True
            sanitized_attrs.append((attribute_name, attribute_value))

        attributes = "".join(
            f' {name}' if value is None else f' {name}="{escape(value, quote=True)}"'
            for name, value in sanitized_attrs
        )
        self.output.append(f"<{tag}{attributes}>")

        if (
            (tag in ("textarea", "output") or clears_content)
            and not already_clearing_content
            and tag not in _VOID_TAGS
        ):
            self.clear_content_depth = 1

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag.lower() not in _VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if self.skip_depth:
            self.skip_depth -= 1
            return
        if tag not in _VOID_TAGS:
            self.output.append(f"</{tag}>")
        if self.clear_content_depth:
            self.clear_content_depth -= 1

    def handle_data(self, data):
        if not self.skip_depth and not self.clear_content_depth:
            self.output.append(_redact_sensitive_text(data))

    def handle_entityref(self, name):
        if not self.skip_depth and not self.clear_content_depth:
            self.output.append(f"&{name};")

    def handle_charref(self, name):
        if not self.skip_depth and not self.clear_content_depth:
            self.output.append(f"&#{name};")


def _sanitize_dom_for_prompt(dom_content: str) -> str:
    """Return a redacted, size-bounded DOM copy for the external AI request."""
    sanitizer = _DomPromptSanitizer()
    sanitizer.feed(dom_content)
    sanitizer.close()
    sanitized_dom = "".join(sanitizer.output)
    if len(sanitized_dom) > MAX_DOM_PROMPT_CHARS:
        return (
            sanitized_dom[:MAX_DOM_PROMPT_CHARS - len(_TRUNCATION_MARKER)]
            + _TRUNCATION_MARKER
        )
    return sanitized_dom


def run_guardian(stderr_log: str, dom_dump_path: str = "dom_dump.txt") -> dict:
    # 1. Selector extraction from log
    match = re.search(r"locator\(['\"](.*?)['\"]\)", stderr_log)
    if not match:
        return {"status": "error", "message": "Original selector not found in error log."}
    original_selector = match.group(1)
    
    # 2. Loading DOM dump & QA Standards
    try:
        with open(dom_dump_path, "r", encoding="utf-8") as f:
            dom_content = f.read()
    except FileNotFoundError:
        return {"status": "error", "message": f"File {dom_dump_path} does not exist."}

    # DYNAMIC LOADING OF QA STANDARDS
    try:
        with open("qa_standards.txt", "r", encoding="utf-8") as f:
            qa_rules = f.read()
    except FileNotFoundError:
        qa_rules = "No specific rules provided."

    # 3. AI Call (DeepSeek)
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return {"status": "error", "message": "Missing OPENROUTER_API_KEY in .env file."}

    url = "https://openrouter.ai/api/v1/chat/completions"

    try:
        sanitized_dom_content = _sanitize_dom_for_prompt(dom_content)
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to sanitize DOM before AI request: {str(e)}"
        }

    prompt = f"""A Playwright test failed because the locator '{original_selector}' is broken or missing.

DOM Dump:
{sanitized_dom_content}

YOUR TASK:
1. Analyze the original selector ('{original_selector}') to understand its intent.
2. Search the DOM Dump for the correct, updated element that matches this intent.
3. STRICTLY follow these project QA Standards when suggesting the new locator:
{qa_rules}

Return ONLY a clean JSON object with these keys (no markdown text, no ```json at the start):
{{
  "confidence": "HIGH",
  "reasoning": "Explain why the old one failed and why the new one is correct based on QA standards...",
  "locator": "page.locator('...')"
}}

IMPORTANT: Your response must be a valid JSON. Never use unescaped double quotes inside the reasoning field. Use single quotes for HTML attributes."""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek/deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        ai_text = data['choices'][0]['message']['content'].strip()
        
        # DEBUG: Printing raw response to terminal
        print(f"\n[DEBUG RAW AI RESPONSE]:\n{ai_text}\n")
        
        # AGGRESSIVE MARKDOWN CLEANING & REGEX EXTRACTION
        json_match = re.search(r'\{.*\}', ai_text, re.DOTALL)
        if json_match:
            ai_text = json_match.group(0)
        else:
            ai_text = ai_text.strip()
        
        # JSON Parsing with Defensive logic
        try:
            ai_json = json.loads(ai_text)
        except json.JSONDecodeError:
            try:
                clean_text = ai_text.replace('\n', '\\n')
                ai_json = json.loads(clean_text)
            except Exception:
                ai_json = {
                    "confidence": "LOW",
                    "reasoning": "WARNING: AI returned invalid JSON. Using fallback.",
                    "locator": f"page.locator('{original_selector}')"
                }
        
        return {
            "status": "success",
            "original_selector": original_selector,
            "ai_suggestion": ai_json
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to process AI response: {str(e)}\n\nRaw AI text was:\n{ai_text if 'ai_text' in locals() else 'No text'}"
        }

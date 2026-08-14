import io
import importlib.util
import os
import sys
import types
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import mock_open, patch


def _load_guardian_module():
    dotenv_stub = types.ModuleType("dotenv")
    dotenv_stub.load_dotenv = lambda: None
    module_path = Path(__file__).resolve().parents[1] / "guardian_v1.py"
    spec = importlib.util.spec_from_file_location(
        "guardian_v1_ai_errors_under_test", module_path
    )
    module = importlib.util.module_from_spec(spec)

    with patch.dict(sys.modules, {"dotenv": dotenv_stub}):
        spec.loader.exec_module(module)

    return module


guardian = _load_guardian_module()


class FakeResponse:
    def __init__(self, status_code=200, payload=None, headers=None, text=""):
        self.status_code = status_code
        self.payload = payload
        self.headers = headers or {}
        self.text = text

    def json(self):
        if isinstance(self.payload, Exception):
            raise self.payload
        return self.payload


SUCCESS_PAYLOAD = {
    "choices": [{"message": {"content": '{"confidence": "HIGH", "reasoning": "Synthetic", "locator": "page.locator(\'.new\')"}'}}]
}


class GuardianAiErrorTests(unittest.TestCase):
    def run_guardian(self, post_side_effect):
        output = io.StringIO()
        errors = io.StringIO()
        post_mock_arguments = (
            {"side_effect": post_side_effect}
            if isinstance(post_side_effect, (BaseException, list, tuple))
            else {"return_value": post_side_effect}
        )
        with (
            patch.dict(os.environ, {"OPENROUTER_API_KEY": "SYNTHETIC_TEST_KEY"}, clear=True),
            patch("builtins.open", mock_open(read_data="<button>Safe</button>")),
            patch.object(guardian.requests, "post", **post_mock_arguments) as post,
            patch.object(guardian.time, "sleep") as sleep,
            redirect_stdout(output),
            redirect_stderr(errors),
        ):
            result = guardian.run_guardian("Error: locator('.old')")
        return result, post, sleep, output.getvalue(), errors.getvalue()

    def assert_error(self, side_effect, expected_message):
        result, post, sleep, stdout, stderr = self.run_guardian(side_effect)
        self.assertEqual({"status": "error", "message": expected_message}, result)
        self.assertEqual("", stdout)
        self.assertEqual("", stderr)
        return post, sleep

    def test_successful_response_uses_configured_timeouts_without_retry(self):
        result, post, sleep, stdout, stderr = self.run_guardian(FakeResponse(payload=SUCCESS_PAYLOAD))

        self.assertEqual("success", result["status"])
        self.assertEqual(".old", result["original_selector"])
        self.assertEqual("page.locator('.new')", result["ai_suggestion"]["locator"])
        self.assertEqual(1, post.call_count)
        self.assertEqual((10, 60), post.call_args.kwargs["timeout"])
        sleep.assert_not_called()
        self.assertEqual("", stdout)
        self.assertEqual("", stderr)

    def test_http_client_errors(self):
        messages = {
            400: "The AI provider rejected the request. Check the request and model configuration.",
            401: "AI provider authentication failed. Check the configured API key.",
            402: "The AI provider account has insufficient credits.",
            403: "The AI provider denied access. Check the API key permissions and model access.",
            404: "The configured AI endpoint or model was not found.",
        }
        for status, message in messages.items():
            with self.subTest(status=status):
                post, sleep = self.assert_error(FakeResponse(status_code=status), message)
                self.assertEqual(1, post.call_count)
                sleep.assert_not_called()

    def test_http_429_without_safe_retry(self):
        post, sleep = self.assert_error(
            FakeResponse(status_code=429),
            "The AI provider rate limit was reached. Wait and try again later.",
        )
        self.assertEqual(1, post.call_count)
        sleep.assert_not_called()

    def test_http_500(self):
        post, sleep = self.assert_error(
            FakeResponse(status_code=500),
            "The AI provider is temporarily unavailable. Try again later.",
        )
        self.assertEqual(1, post.call_count)
        sleep.assert_not_called()

    def test_retries_once_after_429_with_safe_retry_after(self):
        result, post, sleep, _, _ = self.run_guardian([
            FakeResponse(status_code=429, headers={"Retry-After": "1"}),
            FakeResponse(payload=SUCCESS_PAYLOAD),
        ])

        self.assertEqual("success", result["status"])
        self.assertEqual(2, post.call_count)
        sleep.assert_called_once_with(1)

    def test_stops_after_second_429(self):
        post, sleep = self.assert_error(
            [
                FakeResponse(status_code=429, headers={"Retry-After": "1"}),
                FakeResponse(status_code=429, headers={"Retry-After": "1"}),
            ],
            "The AI provider rate limit was reached. Wait and try again later.",
        )
        self.assertEqual(2, post.call_count)
        sleep.assert_called_once_with(1)

    def test_429_does_not_retry_with_unsafe_retry_after(self):
        for retry_after in (None, "invalid", "0", "-1", "11"):
            with self.subTest(retry_after=retry_after):
                headers = {} if retry_after is None else {"Retry-After": retry_after}
                post, sleep = self.assert_error(
                    FakeResponse(status_code=429, headers=headers),
                    "The AI provider rate limit was reached. Wait and try again later.",
                )
                self.assertEqual(1, post.call_count)
                sleep.assert_not_called()

    def test_request_exceptions(self):
        cases = (
            (
                guardian.requests.Timeout("SYNTHETIC_TIMEOUT_SECRET"),
                "The AI provider did not respond within the allowed time.",
            ),
            (
                guardian.requests.ConnectionError("SYNTHETIC_CONNECTION_SECRET"),
                "Could not connect to the AI provider. Check the network connection and provider availability.",
            ),
            (
                guardian.requests.RequestException("SYNTHETIC_REQUEST_SECRET"),
                "The AI provider request failed.",
            ),
        )
        for exception, message in cases:
            with self.subTest(exception=type(exception).__name__):
                post, sleep = self.assert_error(exception, message)
                self.assertEqual(1, post.call_count)
                sleep.assert_not_called()

    def test_invalid_non_json_response(self):
        post, sleep = self.assert_error(
            FakeResponse(payload=ValueError("SYNTHETIC_RESPONSE_SECRET")),
            "The AI provider returned an invalid response.",
        )
        self.assertEqual(1, post.call_count)
        sleep.assert_not_called()

    def test_json_without_completion_content(self):
        post, sleep = self.assert_error(
            FakeResponse(payload={"choices": [{"message": {}}]}),
            "The AI provider response did not contain the expected content.",
        )
        self.assertEqual(1, post.call_count)
        sleep.assert_not_called()

    def test_raw_response_text_and_synthetic_secrets_are_not_exposed(self):
        secret = "SYNTHETIC_RESPONSE_BODY_SECRET"
        result, _, _, stdout, stderr = self.run_guardian(
            FakeResponse(status_code=400, text=secret)
        )
        combined = f"{result.get('message', '')}{stdout}{stderr}"
        self.assertNotIn(secret, combined)
        self.assertNotIn("SYNTHETIC_TEST_KEY", combined)


if __name__ == "__main__":
    unittest.main()

import importlib.util
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch


def _load_app_module():
    streamlit_stub = types.ModuleType("streamlit")
    streamlit_stub.set_page_config = lambda **kwargs: None
    streamlit_stub.sidebar = types.SimpleNamespace(
        title=lambda *args, **kwargs: None,
        radio=lambda *args, **kwargs: "test",
    )
    guardian_stub = types.ModuleType("guardian_v1")
    guardian_stub.run_guardian = lambda *args, **kwargs: None
    generator_stub = types.ModuleType("generator_v1")

    module_path = Path(__file__).resolve().parents[1] / "app.py"
    spec = importlib.util.spec_from_file_location(
        "app_guardian_apply_safety_under_test", module_path
    )
    module = importlib.util.module_from_spec(spec)

    with patch.dict(
        sys.modules,
        {
            "streamlit": streamlit_stub,
            "guardian_v1": guardian_stub,
            "generator_v1": generator_stub,
        },
    ):
        spec.loader.exec_module(module)

    assert sys.modules.get("streamlit") is not streamlit_stub
    assert sys.modules.get("guardian_v1") is not guardian_stub
    assert sys.modules.get("generator_v1") is not generator_stub
    return module


app = _load_app_module()


class GuardianApplySafetyTests(unittest.TestCase):
    def test_accepts_supported_locator_expressions(self):
        supported = (
            "page.locator('[data-test=\"checkout\"]')",
            'page.locator("[data-test=\'checkout\']")',
            "page.locator('.todo-list li').filter({ hasText: 'Buy milk' })",
            "page.locator('.item').first()",
            "page.locator('.item').last()",
            "page.locator('.item').nth(0)",
            "page.locator('.item').nth(12)",
            "page.locator('.item').filter({ hasText: 'Buy' }).nth(0).first()",
        )

        for locator in supported:
            with self.subTest(locator=locator):
                self.assertTrue(app._is_safe_guardian_locator(locator))

    def test_rejects_unsafe_or_unsupported_locator_expressions(self):
        rejected = (
            "",
            None,
            42,
            "page.locator('.item')\npage.locator('.other')",
            "page.locator('.item'); process.exit(1)",
            "page.locator(`.item`)",
            "page.locator('.item') // comment",
            "page.locator('.item') /* comment */",
            "page.getByRole('button')",
            "page.locator('.item').click()",
            "page.locator('.item').nth(-1)",
            "page.locator('.item').nth(1.5)",
            "page.locator('.item').filter({ has: page.locator('.child') })",
        )

        for locator in rejected:
            with self.subTest(locator=locator):
                self.assertFalse(app._is_safe_guardian_locator(locator))

    def test_replaces_single_quoted_base_locator(self):
        content = "await page.locator('[data-test=old]').click();\n"
        replacement, message = app._prepare_guardian_locator_replacement(
            content,
            "[data-test=old]",
            "page.locator('[data-test=new]')",
        )

        self.assertIsNone(message)
        self.assertEqual("await page.locator('[data-test=new]').click();\n", replacement)

    def test_replaces_double_quoted_base_locator(self):
        content = 'await page.locator("[data-test=old]").click();\n'
        replacement, message = app._prepare_guardian_locator_replacement(
            content,
            "[data-test=old]",
            'page.locator("[data-test=new]")',
        )

        self.assertIsNone(message)
        self.assertEqual('await page.locator("[data-test=new]").click();\n', replacement)

    def test_replaces_entire_existing_chain(self):
        content = "await page.locator('.old').last().click();\n"
        replacement, message = app._prepare_guardian_locator_replacement(
            content,
            ".old",
            "page.locator('.new').filter({ hasText: 'Updated' }).nth(0)",
        )

        self.assertIsNone(message)
        self.assertEqual(
            "await page.locator('.new').filter({ hasText: 'Updated' }).nth(0).click();\n",
            replacement,
        )
        self.assertNotIn(".last()", replacement)

    def test_replaces_existing_filter_without_chain_duplication(self):
        content = "await page.locator('.old').filter({ hasText: 'Old' }).first().click();\n"
        replacement, message = app._prepare_guardian_locator_replacement(
            content,
            ".old",
            "page.locator('.new').filter({ hasText: 'New' }).nth(0)",
        )

        self.assertIsNone(message)
        self.assertEqual(
            "await page.locator('.new').filter({ hasText: 'New' }).nth(0).click();\n",
            replacement,
        )
        self.assertNotIn("hasText: 'Old'", replacement)
        self.assertNotIn(".first()", replacement)

    def test_blocks_unsupported_locator_returning_continuations(self):
        continuations = (
            ".locator('.child').click()",
            ".getByRole('button').click()",
            ".getByCustom('button').click()",
            ".and(page.locator('.other')).click()",
            ".or(page.locator('.other')).click()",
            ".filter({ has: page.locator('.child') }).click()",
            ".first( ).click()",
            ".last( ).click()",
            ".nth(-1).click()",
            ".nth(variable).click()",
        )

        for continuation in continuations:
            with self.subTest(continuation=continuation):
                content = f"await page.locator('.old'){continuation};\n"
                replacement, message = app._prepare_guardian_locator_replacement(
                    content,
                    ".old",
                    "page.locator('.new')",
                )

                self.assertIsNone(replacement)
                self.assertEqual(
                    "The existing locator continues with an unsupported locator chain. No file was changed.",
                    message,
                )

    def test_preserves_supported_actions_after_replacement(self):
        actions = ("click()", "fill('new value')", "press('Enter')")

        for action in actions:
            with self.subTest(action=action):
                content = f"await page.locator('.old').{action};\n"
                replacement, message = app._prepare_guardian_locator_replacement(
                    content,
                    ".old",
                    "page.locator('.new')",
                )

                self.assertIsNone(message)
                self.assertEqual(f"await page.locator('.new').{action};\n", replacement)

    def test_refuses_zero_and_multiple_base_locator_matches(self):
        no_match, no_match_message = app._prepare_guardian_locator_replacement(
            "await page.locator('.other').click();\n",
            ".old",
            "page.locator('.new')",
        )
        multiple_matches, multiple_match_message = app._prepare_guardian_locator_replacement(
            "await page.locator('.old').click();\nawait page.locator('.old').fill('x');\n",
            ".old",
            "page.locator('.new')",
        )

        self.assertIsNone(no_match)
        self.assertEqual("Could not find the original locator. No file was changed.", no_match_message)
        self.assertIsNone(multiple_matches)
        self.assertEqual(
            "The original locator occurs more than once. No file was changed.",
            multiple_match_message,
        )

    def test_invalid_suggestion_does_not_prepare_a_change(self):
        content = "await page.locator('.old').click();\n"
        replacement, message = app._prepare_guardian_locator_replacement(
            content,
            ".old",
            "page.locator('.new'); process.exit(1)",
        )

        self.assertIsNone(replacement)
        self.assertEqual(
            "The AI suggestion is not a supported Playwright locator. No file was changed.",
            message,
        )

    def test_replacement_backslashes_are_not_treated_as_regex_references(self):
        content = "await page.locator('.old').click();\n"
        new_locator = r"page.locator('.new\\path')"

        replacement, message = app._prepare_guardian_locator_replacement(
            content,
            ".old",
            new_locator,
        )

        self.assertIsNone(message)
        self.assertIn(new_locator, replacement)

    def test_resolves_only_existing_spec_files_inside_project_tests(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_root = Path(temporary_directory)
            tests_directory = project_root / "tests"
            nested_tests_directory = tests_directory / "nested"
            tests_directory.mkdir()
            nested_tests_directory.mkdir()

            allowed_file = tests_directory / "example.spec.ts"
            nested_allowed_file = nested_tests_directory / "nested.spec.ts"
            directory_instead_of_file = tests_directory / "directory.spec.ts"
            wrong_extension_file = tests_directory / "example.ts"
            outside_file = project_root / "outside.spec.ts"
            for file_path in (allowed_file, nested_allowed_file, wrong_extension_file, outside_file):
                file_path.touch()
            directory_instead_of_file.mkdir()

            with patch.object(app, "__file__", str(project_root / "app.py")):
                self.assertEqual(
                    allowed_file.resolve(),
                    app._resolve_guardian_test_file("tests/example.spec.ts"),
                )
                self.assertEqual(
                    allowed_file.resolve(),
                    app._resolve_guardian_test_file(str(allowed_file.resolve())),
                )
                self.assertEqual(
                    nested_allowed_file.resolve(),
                    app._resolve_guardian_test_file("tests/nested/nested.spec.ts"),
                )

                rejected_paths = (
                    "outside.spec.ts",
                    str(outside_file.resolve()),
                    "tests/../tests/example.spec.ts",
                    "tests/missing.spec.ts",
                    "tests/directory.spec.ts",
                    "tests/example.ts",
                )
                for rejected_path in rejected_paths:
                    with self.subTest(rejected_path=rejected_path):
                        with self.assertRaises(ValueError):
                            app._resolve_guardian_test_file(rejected_path)

    def test_rejects_symlinked_file_outside_tests_when_supported(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_root = Path(temporary_directory)
            tests_directory = project_root / "tests"
            tests_directory.mkdir()
            outside_file = project_root / "outside.spec.ts"
            outside_file.touch()
            symlinked_file = tests_directory / "linked.spec.ts"

            try:
                symlinked_file.symlink_to(outside_file)
            except (NotImplementedError, OSError) as error:
                self.skipTest(f"Symlinks are unavailable in this environment: {error}")

            with patch.object(app, "__file__", str(project_root / "app.py")):
                with self.assertRaises(ValueError):
                    app._resolve_guardian_test_file("tests/linked.spec.ts")

    def test_rejects_symlinked_tests_directory_when_supported(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_root = Path(temporary_directory)
            real_tests_directory = project_root / "real_tests"
            real_tests_directory.mkdir()
            (real_tests_directory / "example.spec.ts").touch()
            symlinked_tests_directory = project_root / "tests"

            try:
                symlinked_tests_directory.symlink_to(real_tests_directory, target_is_directory=True)
            except (NotImplementedError, OSError) as error:
                self.skipTest(f"Symlinks are unavailable in this environment: {error}")

            with patch.object(app, "__file__", str(project_root / "app.py")):
                with self.assertRaises(ValueError):
                    app._resolve_guardian_test_file("tests/example.spec.ts")

    def test_preserves_crlf_when_reading_replacing_and_writing(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            target_file = Path(temporary_directory) / "sample.spec.ts"
            original = b"await page.locator('.old').click();\r\n"
            target_file.write_bytes(original)

            content = app._read_text_preserving_newlines(target_file)
            replacement, message = app._prepare_guardian_locator_replacement(
                content,
                ".old",
                "page.locator('.new')",
            )
            self.assertIsNone(message)
            app._write_text_atomically(target_file, replacement)

            self.assertEqual(
                b"await page.locator('.new').click();\r\n",
                target_file.read_bytes(),
            )

    def test_fdopen_error_closes_descriptor_and_removes_temp_file(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            target_file = Path(temporary_directory) / "sample.spec.ts"
            original = b"await page.locator('.old').click();\r\n"
            target_file.write_bytes(original)
            closed_descriptors = []
            real_close = app.os.close

            def close_descriptor(descriptor):
                closed_descriptors.append(descriptor)
                real_close(descriptor)

            with (
                patch.object(app.os, "fdopen", side_effect=OSError("simulated fdopen error")),
                patch.object(app.os, "close", side_effect=close_descriptor),
            ):
                with self.assertRaises(OSError):
                    app._write_text_atomically(target_file, "updated\r\n")

            self.assertEqual(1, len(closed_descriptors))
            self.assertEqual(original, target_file.read_bytes())
            self.assertEqual([], list(target_file.parent.glob(f".{target_file.name}.*.tmp")))

    def test_write_error_preserves_original_file_and_removes_temp_file(self):
        class FailingFile:
            def __init__(self, wrapped_file):
                self.wrapped_file = wrapped_file

            def __enter__(self):
                return self

            def write(self, content):
                raise OSError("simulated write error")

            def __exit__(self, *args):
                self.wrapped_file.close()

        with tempfile.TemporaryDirectory() as temporary_directory:
            target_file = Path(temporary_directory) / "sample.spec.ts"
            original = b"await page.locator('.old').click();\r\n"
            target_file.write_bytes(original)
            real_fdopen = app.os.fdopen

            with patch.object(
                app.os,
                "fdopen",
                side_effect=lambda *args, **kwargs: FailingFile(real_fdopen(*args, **kwargs)),
            ):
                with self.assertRaises(OSError):
                    app._write_text_atomically(target_file, "updated\r\n")

            self.assertEqual(original, target_file.read_bytes())
            self.assertEqual([], list(target_file.parent.glob(f".{target_file.name}.*.tmp")))

    def test_replace_error_preserves_original_file_and_removes_temp_file(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            target_file = Path(temporary_directory) / "sample.spec.ts"
            original = b"await page.locator('.old').click();\r\n"
            target_file.write_bytes(original)

            with patch.object(app.os, "replace", side_effect=OSError("simulated write error")):
                with self.assertRaises(OSError):
                    app._write_text_atomically(target_file, "updated\r\n")

            self.assertEqual(original, target_file.read_bytes())
            self.assertEqual([], list(target_file.parent.glob(f".{target_file.name}.*.tmp")))


if __name__ == "__main__":
    unittest.main()

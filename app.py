import streamlit as st
import re
import traceback
import os
import tempfile
from pathlib import Path
from guardian_v1 import run_guardian
import generator_v1


_TS_STRING_LITERAL = r'''(?:"(?:\\.|[^"\\\r\n])*"|'(?:\\.|[^'\\\r\n])*')'''
_FILTER_CHAIN = rf'''\.filter\(\s*\{{\s*hasText\s*:\s*{_TS_STRING_LITERAL}\s*,?\s*\}}\s*\)'''
_LOCATOR_CHAIN = rf'''(?:{_FILTER_CHAIN}|\.first\(\)|\.last\(\)|\.nth\(\s*(?:0|[1-9][0-9]*)\s*\))*'''
_SAFE_GUARDIAN_LOCATOR_RE = re.compile(
    rf'''page\.locator\(\s*{_TS_STRING_LITERAL}\s*\){_LOCATOR_CHAIN}''',
    re.VERBOSE,
)
_UNSUPPORTED_LOCATOR_CONTINUATION_RE = re.compile(
    r'''\s*\.\s*(?:locator|getBy[A-Za-z_$][A-Za-z0-9_$]*|filter|and|or|
        first|last|nth)\s*\(''',
    re.VERBOSE,
)


def _is_safe_guardian_locator(value: object) -> bool:
    """Allow one restricted, single-line Playwright locator expression."""
    if not isinstance(value, str):
        return False
    if not value or any(token in value for token in ("\r", "\n", ";", "`", "//", "/*", "*/")):
        return False
    return _SAFE_GUARDIAN_LOCATOR_RE.fullmatch(value) is not None


def _existing_locator_expression_pattern(original_selector: str) -> re.Pattern:
    escaped_selector = re.escape(original_selector)
    return re.compile(
        rf'''page\.locator\(\s*(?:'{escaped_selector}'|"{escaped_selector}")\s*\){_LOCATOR_CHAIN}''',
        re.VERBOSE,
    )


def _prepare_guardian_locator_replacement(
    content: str,
    original_selector: str,
    new_locator: object,
) -> tuple[str | None, str | None]:
    """Return one safe locator-expression replacement without modifying a file."""
    if not _is_safe_guardian_locator(new_locator):
        return None, "The AI suggestion is not a supported Playwright locator. No file was changed."

    pattern = _existing_locator_expression_pattern(original_selector)
    matches = list(pattern.finditer(content))
    match_count = len(matches)
    if match_count == 0:
        return None, "Could not find the original locator. No file was changed."
    if match_count > 1:
        return None, "The original locator occurs more than once. No file was changed."
    if _UNSUPPORTED_LOCATOR_CONTINUATION_RE.match(content, matches[0].end()):
        return None, "The existing locator continues with an unsupported locator chain. No file was changed."

    new_content, replacement_count = pattern.subn(lambda _: new_locator, content, count=1)
    if replacement_count != 1:
        return None, "The locator replacement could not be applied. No file was changed."
    return new_content, None


def _read_text_preserving_newlines(path: Path) -> str:
    with open(path, "r", encoding="utf-8", newline="") as file:
        return file.read()


def _write_text_atomically(path: Path, content: str) -> None:
    """Replace a file only after its full contents were written beside it."""
    file_descriptor = None
    temporary_name = None
    try:
        file_descriptor, temporary_name = tempfile.mkstemp(
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            text=True,
        )
        temporary_file = os.fdopen(
            file_descriptor,
            "w",
            encoding="utf-8",
            newline="",
        )
        file_descriptor = None
        with temporary_file as file:
            file.write(content)
        os.replace(temporary_name, path)
    except Exception:
        if file_descriptor is not None:
            try:
                os.close(file_descriptor)
            except OSError:
                pass
        if temporary_name is not None:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass
        raise


def _resolve_guardian_test_file(target_file: str) -> Path:
    """Return a safe, existing Playwright spec file inside project tests/."""
    candidate = Path(target_file)
    if ".." in candidate.parts:
        raise ValueError("Cesta nesmie obsahovať '..'.")

    project_root = Path(__file__).resolve().parent
    tests_dir = project_root / "tests"

    try:
        resolved_tests_dir = tests_dir.resolve(strict=True)
        resolved_target = (
            candidate if candidate.is_absolute() else project_root / candidate
        ).resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise ValueError("Cieľový súbor alebo adresár tests/ neexistuje.") from exc

    if tests_dir.is_symlink() or not resolved_tests_dir.is_dir():
        raise ValueError("Projektový adresár tests/ nie je platný bežný adresár.")

    try:
        resolved_tests_dir.relative_to(project_root)
        resolved_target.relative_to(resolved_tests_dir)
    except ValueError as exc:
        raise ValueError(
            "Cieľ musí byť v adresári tests/ alebo jeho podpriečinku."
        ) from exc

    if not resolved_target.is_file():
        raise ValueError("Cieľ musí byť existujúci bežný súbor.")
    if not resolved_target.name.endswith(".spec.ts"):
        raise ValueError("Cieľový súbor musí mať príponu .spec.ts.")

    return resolved_target

st.set_page_config(page_title="Playwright AI Guardian", page_icon="🛡️", layout="wide")

st.sidebar.title("🏭 AI QA Factory")
menu = st.sidebar.radio("Navigation", ["🚑 Guardian (Auto-Healer)", "✨ Test Generator"])

if menu == "🚑 Guardian (Auto-Healer)":
    st.title("🛡️ Playwright AI Guardian")

    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None

    # Scanning queue directory
    queue_dir = "guardian_queue"
    error_files = []
    if os.path.exists(queue_dir):
        error_files = [f for f in os.listdir(queue_dir) if f.startswith("error_log_")]

    if not error_files:
        st.success("🎉 Queue is empty! No failed tests.")
        default_file_path = "tests/guardian_test.spec.ts" # Fallback value
        st.subheader("Input (Manual Fallback)")
        stderr_input = st.text_area("Playwright error log:", value="", height=150)

        # BUTTON 1: ANALYSIS
        if st.button("🚀 Find cause and suggest fix"):
            if stderr_input:
                with st.spinner("AI is analyzing DOM tree and looking for a fix..."):
                    try:
                        st.session_state.analysis_result = run_guardian(stderr_input, dom_dump_path="dom_dump.txt")
                    except Exception as e:
                         st.error(f"Critical error: {e}")
            else:
                st.warning("Please insert an error log first.")
    else:
        st.info("📦 Enterprise Mode: Processing Failed Tests Queue")
        selected_error_file = st.selectbox("Select a failed test to analyze:", error_files)
        
        safe_title = selected_error_file.replace("error_log_", "").replace(".txt", "")
        error_log_path = os.path.join(queue_dir, selected_error_file)
        dom_dump_path = os.path.join(queue_dir, f"dom_dump_{safe_title}.txt")
        
        st.session_state.current_error_log_path = error_log_path
        st.session_state.current_dom_dump_path = dom_dump_path

        default_error = ""
        default_file_path = "tests/guardian_test.spec.ts" # Fallback value

        if os.path.exists(error_log_path):
            with open(error_log_path, "r", encoding="utf-8") as f:
                default_error = f.read()
            
            # Search for a string that starts with "tests" and ends with ".spec.ts"
            match = re.search(r'(tests[\\/][\w.-]+\.spec\.ts)', default_error)
            if match:
                default_file_path = match.group(1).replace('\\', '/') # Normalize slashes for Python

        stderr_input = default_error

        # BUTTON 1: ANALYSIS
        if st.button("🚀 Find cause and suggest fix"):
            if stderr_input:
                with st.spinner("AI is analyzing DOM tree and looking for a fix..."):
                    try:
                        st.session_state.analysis_result = run_guardian(stderr_input, dom_dump_path=st.session_state.current_dom_dump_path)
                    except Exception as e:
                         st.error(f"Critical error: {e}")
            else:
                st.warning("Selected error log is empty.")

    st.markdown("---")

    # DISPLAYING RESULT FROM MEMORY
    if st.session_state.analysis_result:
        res = st.session_state.analysis_result
        
        # 🚨 FIXED LOGIC: First check if backend crashed!
        if res.get("status") == "error":
            st.error(f"🚨 BACKGROUND ERROR (FINALLY VISIBLE):")
            st.code(res.get("message", "Unknown error"), language="text")
            
        # If success, show UI
        elif res.get("status") == "success" or "ai_suggestion" in res:
            st.success("✅ AI successfully analyzed the problem.")
            
            ai_data = res.get("ai_suggestion", res) 
            conf = ai_data.get("confidence", "UNKNOWN").upper()
            
            if conf == "HIGH":
                st.metric("Confidence Score", "HIGH 🟢")
            elif conf == "MEDIUM":
                st.metric("Confidence Score", "MEDIUM 🟠")
            else:
                st.metric("Confidence Score", "LOW 🔴")
                
            st.info(f"**Reasoning:** {ai_data.get('reasoning', 'No reasoning provided')}")
            
            new_locator = ai_data.get("locator", "")
            st.code(new_locator, language="typescript")
            
            st.markdown("### 🛠️ Apply Fix")
            original_selector = res.get("original_selector", ".btn-submit")
            
            target_file = st.text_input("Path to broken test:", value=default_file_path)
            
            # BUTTON 2: WRITE TO FILE
            if st.button("💾 Overwrite code in file"):
                st.write(f"🔍 **DEBUG:** Searching in file: `{original_selector}`")

                try:
                    validated_target_file = _resolve_guardian_test_file(target_file)
                except ValueError as e:
                    st.error(f"❌ Neplatná cesta k testu: {e}")
                else:
                    try:
                        content = _read_text_preserving_newlines(validated_target_file)
                        new_content, replacement_error = _prepare_guardian_locator_replacement(
                            content,
                            original_selector,
                            new_locator,
                        )
                        if replacement_error:
                            st.error(replacement_error)
                        else:
                            _write_text_atomically(validated_target_file, new_content)

                            # CLEANUP LOGIC
                            err_path = st.session_state.get('current_error_log_path')
                            dom_path = st.session_state.get('current_dom_dump_path')
                            if err_path and os.path.exists(err_path):
                                os.remove(err_path)
                            if dom_path and os.path.exists(dom_path):
                                os.remove(dom_path)

                            st.session_state.analysis_result = None
                            st.balloons()
                            st.success(f"🎉 Great! File {target_file} was successfully overwritten. Queue cleared.")
                            st.rerun()

                    except Exception as e:
                        st.error(f"❌ An error occurred during writing: {e}")

elif menu == "✨ Test Generator":
    st.header("✨ AI Test Generator (Factory)")
    
    url_input = st.text_input("Enter the website URL to test:")
    description_input = st.text_area("Describe the steps (e.g., login with user 'admin' and password '123'):")
    
    if "generated_code" not in st.session_state:
        st.session_state.generated_code = None

    generate_btn = st.button("Generate Test Code 🚀")
    
    if generate_btn:
        if url_input and description_input:
            api_key = os.environ.get("OPENROUTER_API_KEY")
            if not api_key:
                st.error("Missing OPENROUTER_API_KEY environment variable.")
            else:
                with st.spinner("AI is writing Playwright test..."):
                    code = generator_v1.generate_new_test(api_key, url_input, description_input)
                    st.session_state.generated_code = code
        else:
            st.warning("Please fill in both URL and description.")
            
    if st.session_state.generated_code:
        st.code(st.session_state.generated_code, language='typescript')
        
        st.markdown("---")
        new_file_name = st.text_input("Enter the name of the new file (e.g., `login_test.spec.ts`):")
        
        if st.button("Save and Create File 💾"):
            if new_file_name:
                try:
                    os.makedirs("tests", exist_ok=True)
                    clean_filename = os.path.basename(new_file_name)
                    filepath = os.path.join("tests", clean_filename).replace("\\", "/")
                    
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(st.session_state.generated_code)
                        
                    st.balloons()
                    st.success(f"🎉 File `{filepath}` was successfully created!")
                except Exception as e:
                    st.error(f"❌ Error saving file: {e}")
            else:
                st.warning("Please enter a valid file name.")

import streamlit as st
import re
import traceback
import os
from guardian_v1 import run_guardian
import generator_v1

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
                
                if not os.path.exists(target_file):
                     st.error(f"❌ File '{target_file}' does not exist!")
                else:
                    try:
                        with open(target_file, "r", encoding="utf-8") as f:
                            content = f.read()
                        
                        escaped_selector = re.escape(original_selector)
                        pattern = rf'page\.locator\([\'"]{escaped_selector}[\'"]\)'
                        
                        matches = re.findall(pattern, content)
                        st.write(f"🔍 **DEBUG:** Found occurrences in file: {len(matches)}")
                        
                        if len(matches) == 0:
                            st.error(f"❌ Could not find `{original_selector}` in file.")
                        else:
                            if not new_locator.strip():
                                st.error("🛑 Safety trigger: AI did not generate any new locator. File write blocked!")
                            else:
                                new_content = re.sub(pattern, new_locator, content)
                                with open(target_file, "w", encoding="utf-8") as f:
                                    f.write(new_content)
                                    
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
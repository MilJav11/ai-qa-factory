import streamlit as st
import re
import traceback
import os
from guardian_v1 import run_guardian 

st.set_page_config(page_title="Playwright AI Guardian", page_icon="🛡️", layout="wide")

st.title("🛡️ Playwright AI Guardian")

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

# Automatic loading of error log
default_error = ""
if os.path.exists("error_log.txt"):
    with open("error_log.txt", "r", encoding="utf-8") as f:
        default_error = f.read()

st.subheader("Input")
stderr_input = st.text_area("Playwright error log:", value=default_error, height=150)


# BUTTON 1: ANALYSIS
if st.button("🚀 Find cause and suggest fix"):
    if stderr_input:
        with st.spinner("AI is analyzing DOM tree and looking for a fix..."):
            try:
                st.session_state.analysis_result = run_guardian(stderr_input)
            except Exception as e:
                 st.error(f"Critical error: {e}")
    else:
        st.warning("Please insert an error log first.")

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
        
        target_file = st.text_input("Path to broken test:", value="tests/guardian_test.spec.ts")
        
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
                                
                            st.balloons()
                            st.success(f"🎉 Great! File {target_file} was successfully overwritten.")
                except Exception as e:
                    st.error(f"❌ An error occurred during writing: {e}")
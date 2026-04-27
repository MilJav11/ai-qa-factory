import streamlit as st
import re
import traceback
import os
from guardian_v1 import run_guardian 

st.set_page_config(page_title="Playwright AI Guardian", page_icon="🛡️", layout="wide")

st.title("🛡️ Playwright AI Guardian")

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

# Automatické načítanie chybového logu
default_error = ""
if os.path.exists("error_log.txt"):
    with open("error_log.txt", "r", encoding="utf-8") as f:
        default_error = f.read()

st.subheader("Vstup")
stderr_input = st.text_area("Chybový log z Playwrightu:", value=default_error, height=150)


# TLAČIDLO 1: ANALÝZA
if st.button("🚀 Zistiť príčinu a navrhnúť opravu"):
    if stderr_input:
        with st.spinner("AI analyzuje DOM strom a hľadá opravu..."):
            try:
                st.session_state.analysis_result = run_guardian(stderr_input)
            except Exception as e:
                 st.error(f"Kritická chyba: {e}")
    else:
        st.warning("Najprv vlož chybový log.")

st.markdown("---")

# ZOBRAZENIE VÝSLEDKU Z PAMÄTE
if st.session_state.analysis_result:
    res = st.session_state.analysis_result
    
    # 🚨 OPRAVENÁ LOGIKA: Najprv zistíme, či backend nepadol!
    if res.get("status") == "error":
        st.error(f"🚨 CHYBA V POZADÍ (KONEČNE VIDITEĽNÁ):")
        st.code(res.get("message", "Neznáma chyba"), language="text")
        
    # Ak je to naozaj úspech, až potom ukážeme UI
    elif res.get("status") == "success" or "ai_suggestion" in res:
        st.success("✅ AI úspešne analyzovala problém.")
        
        ai_data = res.get("ai_suggestion", res) 
        conf = ai_data.get("confidence", "UNKNOWN").upper()
        
        if conf == "HIGH":
            st.metric("Confidence Score", "VYSOKÁ (HIGH) 🟢")
        elif conf == "MEDIUM":
            st.metric("Confidence Score", "STREDNÁ (MEDIUM) 🟠")
        else:
            st.metric("Confidence Score", "NÍZKA (LOW) 🔴")
            
        st.info(f"**Zdôvodnenie:** {ai_data.get('reasoning', 'Bez zdôvodnenia')}")
        
        new_locator = ai_data.get("locator", "")
        st.code(new_locator, language="typescript")
        
        st.markdown("### 🛠️ Aplikovať opravu")
        original_selector = res.get("original_selector", ".btn-submit")
        
        target_file = st.text_input("Cesta k pokazenému testu:", value="tests/guardian_test.spec.ts")
        
        # TLAČIDLO 2: ZÁPIS DO SÚBORU
        if st.button("💾 Prepísať kód v súbore"):
            st.write(f"🔍 **DEBUG:** Hľadám v súbore: `{original_selector}`")
            
            if not os.path.exists(target_file):
                 st.error(f"❌ Súbor '{target_file}' neexistuje!")
            else:
                try:
                    with open(target_file, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    escaped_selector = re.escape(original_selector)
                    pattern = rf'page\.locator\([\'"]{escaped_selector}[\'"]\)'
                    
                    matches = re.findall(pattern, content)
                    st.write(f"🔍 **DEBUG:** Nájdené výskyty v súbore: {len(matches)}")
                    
                    if len(matches) == 0:
                        st.error(f"❌ Nenašiel som `{original_selector}` v súbore.")
                    else:
                        if not new_locator.strip():
                            st.error("🛑 Ochranná poistka: AI nevygenerovala žiadny nový lokátor. Zápis do súboru bol zablokovaný!")
                        else:
                            new_content = re.sub(pattern, new_locator, content)
                            with open(target_file, "w", encoding="utf-8") as f:
                                f.write(new_content)
                                
                            st.balloons()
                            st.success(f"🎉 Paráda! Súbor {target_file} bol úspešne prepísaný.")
                except Exception as e:
                    st.error(f"❌ Nastala chyba pri zápise: {e}")
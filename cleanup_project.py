import os
import shutil

def archive_old_files():
    """
    Archivuje staré prototypové .py, .ts a .spec.ts súbory do samostatnej zložky,
    aby zostal v koreni iba systém QA Guardian.
    """
    archive_dir = "_archive_old_prototypes"
    
    # Kritické súbory, ktoré MUSIA zostať v koreňovom adresári
    whitelist = [
        "app.py",
        "guardian_v1.py",
        "error_parser.py",
        "cleanup_project.py",
        "playwright.config.ts",
        "guardian-hook.ts"
    ]
    
    # Prípony súborov, ktoré chceme archivovať
    extensions_to_archive = (".py", ".ts", ".spec.ts")
    
    # Vytvorenie archívu, ak neexistuje
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)
        print(f"✅ Archívny priečinok pripravený: {archive_dir}")

    files_moved = 0
    
    # Prechádzanie súborov v koreňovom adresári
    for filename in os.listdir("."):
        # Zaujímajú nás iba súbory (nie priečinky) so zvolenými príponami
        if os.path.isfile(filename) and filename.endswith(extensions_to_archive):
            # Ak súbor nie je vo whiteliste, presunieme ho
            if filename not in whitelist:
                src = filename
                dst = os.path.join(archive_dir, filename)
                
                try:
                    shutil.move(src, dst)
                    print(f"📦 Archivované: {filename} -> {archive_dir}/")
                    files_moved += 1
                except Exception as e:
                    print(f"❌ Chyba pri presune {filename}: {e}")

    if files_moved == 0:
        print("ℹ️ Žiadne ďalšie staré súbory na archiváciu neboli nájdené.")
    else:
        print(f"\n✨ Operácia dokončená. Celkovo archivovaných súborov v tomto behu: {files_moved}")

if __name__ == "__main__":
    archive_old_files()

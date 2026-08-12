import os
import shutil

def archive_old_files():
    """
    Archives old prototype .py, .ts and .spec.ts files into a separate folder
    to keep only the QA Guardian system in the root.
    """
    archive_dir = "_archive_old_prototypes"
    
    # Critical files that MUST stay in the root directory
    whitelist = [
        "app.py",
        "guardian_v1.py",
        "error_parser.py",
        "cleanup_project.py",
    "playwright.config.ts",
    "generator_v1.py",
    "guardian_reporter.ts",
        "guardian-hook.ts"
    ]
    
    # File extensions to archive
    extensions_to_archive = (".py", ".ts", ".spec.ts")
    
    # Create archive directory if it doesn't exist
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)
        print(f"✅ Archive folder ready: {archive_dir}")

    files_moved = 0
    
    # Iterate through files in the root directory
    for filename in os.listdir("."):
        # Focus on files (not directories) with selected extensions
        if os.path.isfile(filename) and filename.endswith(extensions_to_archive):
            # If the file is not in the whitelist, move it
            if filename not in whitelist:
                src = filename
                dst = os.path.join(archive_dir, filename)
                
                try:
                    shutil.move(src, dst)
                    print(f"📦 Archived: {filename} -> {archive_dir}/")
                    files_moved += 1
                except Exception as e:
                    print(f"❌ Error moving {filename}: {e}")

    if files_moved == 0:
        print("ℹ️ No more old files found for archiving.")
    else:
        print(f"\n✨ Operation completed. Total files archived in this run: {files_moved}")

if __name__ == "__main__":
    archive_old_files()

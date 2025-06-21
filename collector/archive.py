#!/usr/bin/env python3
import zipfile
from pathlib import Path
from datetime import datetime, timedelta

def archive_old_logs(data_dir="data", archive_dir="archive", days_old=7):
    data_path = Path(data_dir)
    archive_path = Path(archive_dir)
    archive_path.mkdir(exist_ok=True)

    cutoff = datetime.now() - timedelta(days=days_old)
    files_to_archive = []

    for json_file in data_path.glob("log_*.json"):
        file_time = datetime.fromtimestamp(json_file.stat().st_mtime)
        if file_time < cutoff:
            files_to_archive.append(json_file)

    if not files_to_archive:
        print("📦 No files to archive.")
        return

    zip_name = archive_path / f"{datetime.now().strftime('%Y-%m-%d')}.zip"
    with zipfile.ZipFile(zip_name, 'a', zipfile.ZIP_DEFLATED) as zipf:
        for f in files_to_archive:
            zipf.write(f, arcname=f.name)
            f.unlink()
    print(f"📦 Archived {len(files_to_archive)} files into {zip_name}")

if __name__ == "__main__":
    archive_old_logs()

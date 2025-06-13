import subprocess

# 1. Scrape VNG-publicaties
subprocess.run(["python", "scrape_vng.py"])

# 2. Merge alles in publicaties.json
subprocess.run(["python", "merge_publicaties.py"])

import subprocess
hashlabel = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip().decode("utf-8") 

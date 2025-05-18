import subprocess
from code.analyze import analyze
from code.crawl import executePredefinedSearch
from code.export import merge
from code.extract import executePredefinedCrawl

subprocess.run(['..\\.venv\\Scripts\\activate.bat'], shell=True, check=True)

# 1
executePredefinedSearch()

# 2
executePredefinedCrawl()


# 3
analyze()

# 4
emptyColCount = 2
merge(emptyColCount, "Main")
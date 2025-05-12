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


emptyColCount = 2
# 3
analyze(emptyColCount)

# 4


merge(emptyColCount, "Main")
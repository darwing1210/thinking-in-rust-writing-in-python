"""ingest() returns Result[Article, IngestError], not Article."""

from ingest.after.ingest import ingest
from ingest.catalog import OK_URL

result = ingest(OK_URL)
print(result.title)

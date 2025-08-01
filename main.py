from firecrawl import JsonConfig, FirecrawlApp
from pydantic import BaseModel
from typing import List

app = FirecrawlApp(api_key="fc-745b0d56f5d04dc3aa8b16e3399bd580")

class ExtractSchema(BaseModel):
    company_name: str
    job_postings: List[str]

json_config = JsonConfig(
    schema=ExtractSchema
)

llm_extraction_result = app.scrape_url(
    'https://munichre-jobs.com/de/MunichRe',
    formats=["json"],
    json_options=json_config,
    only_main_content=False,
    timeout=120000
)

print(llm_extraction_result.json)
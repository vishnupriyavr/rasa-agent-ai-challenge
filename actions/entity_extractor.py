import os

from dotenv import load_dotenv
from rasa.nlu.extractors.duckling_entity_extractor import DucklingEntityExtractor

load_dotenv("/Users/vishnupriyavr/Documents/rasa-agent-ai-challenge/.env")
duckling_url = os.environ.get("RASA_DUCKLING_HTTP_URL")

duckling_config = {
    **DucklingEntityExtractor.get_default_config(),
    "url": duckling_url,
    "dimensions": ["time"]
}

duckling_entity_extractor = DucklingEntityExtractor(duckling_config)
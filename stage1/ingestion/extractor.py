import os
import json
import time
import requests
from typing import Optional

from models.schema import ExtractionResult


# -----------------------------
# Configuration
# -----------------------------

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "mistralai/mistral-7b-instruct:free"

MAX_RETRIES = 2
REQUEST_TIMEOUT = 30


# -----------------------------
# Extraction Prompt
# -----------------------------

SYSTEM_PROMPT = """
You are an information extraction engine.

Your task is to extract structured knowledge from text.
You must follow the schema and rules exactly.
Do not explain your reasoning.
Do not include any text outside valid JSON.
If information is uncertain or implicit, omit it.
"""

USER_PROMPT_TEMPLATE = """
Extract structured knowledge from the following text.

ALLOWED ENTITY TYPES:
- Entity (real-world objects: people, organizations, products, places)
- Event (things that happened or occurred)
- Concept (abstract ideas, domains, phenomena)
- Metric (dates, numbers, quantities, measurements)

ALLOWED RELATIONSHIP TYPES:
- MENTIONS
- RELATED_TO
- ASSOCIATED_WITH
- CAUSES
- PRECEDES
- PART_OF
- MEASURED_BY
- EXTRACTED_FROM

NAMING GUIDELINES:
- The `name` field MUST be a human-readable phrase copied or lightly normalized from the text.
- Do NOT use IDs or placeholders as names.
- Use the most specific surface form available in the text.
- If unsure, choose the shortest meaningful phrase from the text.

SUBTYPE RULES:
- If the entity clearly belongs to a common category (e.g., Organization, Product, Year, Industry),
  put that in `subtype`.
- Otherwise, leave `subtype` as null.

GENERAL RULES:
- Use only the allowed types.
- Do not infer or guess information not present in the text.
- Every entity and relationship must reference the given chunk ID.
- If nothing is extractable, return empty arrays.

CHUNK ID: {chunk_id}

TEXT:
{chunk_text}

Return only valid JSON in the following format:
{{
  "entities": [],
  "relationships": []
}}
"""



# -----------------------------
# Core Extraction Function
# -----------------------------

def normalize_extraction(parsed_output: dict, chunk_id: str) -> dict:
    entities = parsed_output.get("entities", [])
    entity_ids = {e["id"] for e in entities if "id" in e}

    # Normalize entities
    for entity in entities:
        entity.setdefault("source_chunk_id", chunk_id)
        entity.setdefault("confidence", 0.8)

    # Normalize relationships
    normalized_relationships = []

    for rel in parsed_output.get("relationships", []):
        source_id = rel.get("source_id") or rel.get("source")
        target_id = rel.get("target_id") or rel.get("target")

        # 🔥 DROP invalid relationships
        if source_id not in entity_ids or target_id not in entity_ids:
            continue

        normalized_relationships.append({
            "source_id": source_id,
            "target_id": target_id,
            "type": rel.get("type"),
            "source_chunk_id": rel.get("source_chunk_id") or rel.get("chunk_id") or chunk_id,
            "confidence": rel.get("confidence", 0.8)
        })

    parsed_output["entities"] = entities
    parsed_output["relationships"] = normalized_relationships

    return parsed_output


def extract_json_from_text(text: str) -> dict:
    """
    Safely extract the first JSON object from a text string.
    Handles markdown fences and stray text.
    """
    text = text.strip()

    # Remove markdown code fences if present
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()

    # Find first JSON object
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("No JSON object found in LLM response")

    json_str = text[start:end + 1]
    return json.loads(json_str)


def extract_knowledge_from_chunk(
    chunk_id: str,
    chunk_text: str
) -> Optional[ExtractionResult]:
    """
    Sends a single document chunk to the LLM and returns a validated ExtractionResult.
    Returns None if extraction fails after retries.
    """

    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    user_prompt = USER_PROMPT_TEMPLATE.format(
        chunk_id=chunk_id,
        chunk_text=chunk_text
    )

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.0,
        "response_format": { "type": "json_object" }
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(
                OPENROUTER_API_URL,
                headers=headers,
                json=payload,
                timeout=REQUEST_TIMEOUT
            )

            response.raise_for_status()

            raw_content = response.json()["choices"][0]["message"]["content"]

            # Parse JSON strictly
            parsed_output = extract_json_from_text(raw_content)
            parsed_output = normalize_extraction(parsed_output, chunk_id)


            # Validate against Pydantic schema
            extraction_result = ExtractionResult.model_validate(parsed_output)

            return extraction_result

        except Exception as e:
            print(f"[Extractor] Attempt {attempt} failed: {e}")
            print("----- RAW MODEL OUTPUT -----")
            print(raw_content)
            print("----------------------------")
            if attempt < MAX_RETRIES:
                time.sleep(1)
            else:
                print("[Extractor] Extraction failed after max retries.")
                return None
        

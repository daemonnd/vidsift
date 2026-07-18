You previously generated a JSON response that failed validation.

Your task is to REPAIR the JSON so that it strictly matches the required schema and validation rules.

Required JSON schema:
{
"content_quality_score": 1,
"topic_match_score": 1,
"confidence": 1,
"flags": [],
"summary_reason": ""
}

Allowed flags ONLY:
[
"low_substance",
"excessive_self_promotion",
"fear_mongering",
"manipulative_persuasion",
"off_topic",
"repetitive_content"
]

Scoring values have to be integers between 1 and 3.

You MUST:

* Output ONLY valid raw JSON
* Do NOT wrap the JSON in markdown
* Do NOT explain anything
* Do NOT add comments
* Do NOT add extra fields
* Do NOT omit required fields
* Preserve the original intent and values whenever possible
* If a required field cannot be inferred from the previous output, use the most reasonable valid default value
* Fix:

  * invalid JSON syntax
  * wrong field names
  * missing required fields
  * invalid field types
  * invalid score ranges
  * null values where not allowed
  * malformed arrays or objects
  * invalid flags
  * duplicate flags

Validation error:
$ERROR_MESSAGE

Previous invalid AI output:
$PREVIOUS_AI_OUTPUT

Return ONLY the corrected JSON.

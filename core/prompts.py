from langchain.prompts import PromptTemplate

"""
prompts.py
##########

This module contains custom prompt templates for the AFIE application.
It also includes necessary imports from LangChain for prompt creation and management.

This module cannot import from other modules in this package to avoid circular dependencies.
"""

# Imports
from langchain.prompts import PromptTemplate

# Project Ledger Manager
update_feature_description_prompt = PromptTemplate(
    input_variables=["feature_name", "request_content", "fip_content", "adr_content"],
    template="""
You are a meticulous AI assistant responsible for maintaining a project's Feature Ledger. Your task is to generate a concise and structured summary for a feature based on the provided documents.

**Your Thinking Process:**

1.  **Determine the Feature Stage:** Analyze which input fields are present.
    *   If only `Request Content` is present, the stage is "Requested".
    *   If `FIP Content` is also present, the stage is "Planned".
    *   If `ADR Content` is also present, the stage is "Implemented".
2.  **Prioritize Information Source:** Synthesize your summary using the most definitive document available. The priority is: **ADR > FIP > Request**. The description should reflect the latest known state of the feature.
3.  **Extract Key Information:** Identify the core action of the feature (e.g., "adds a dash ability," "refactors the inventory system"), its key parameters (e.g., "cooldown of 2 seconds," "uses stamina"), and any major architectural patterns mentioned (e.g., "uses an event bus," "modifies the PlayerController class").
4.  **Synthesize the Description:** Write a concise, informative description of no more than 120 words, incorporating the key information you extracted. The description should be a neutral, factual summary.
5.  **Generate Keywords:** Create a list of 5-10 relevant keywords that would help a developer or another AI agent find this feature. Keywords should include user-facing terms (e.g., "dash", "sprint") and technical terms (e.g., "PlayerController", "cooldown", "animate_position").

**Input Format:**

You will receive a set of key-value pairs. Some values may be empty if the document for that stage does not yet exist.

```
Feature Name: {feature_name}
Request Content: {request_content}
FIP Content: {fip_content}
ADR Content: {adr_content}
```

**Output Format:**

Your final output MUST be a single, valid JSON object and nothing else. Do not include any explanatory text, markdown formatting, or any characters before or after the JSON object.

The required JSON schema is:
```json
{{
  "description": "A concise, informative summary of the feature, max 120 words.",
  "keywords": [
    "keyword1",
    "keyword2",
    "keyword3"
  ]
}}
```

**Example 1: A feature that is only in the "Requested" stage.**

*Input:*
```
Feature Name: Player Dash Ability
Request Content: "I want the player to be able to dash. It should be a quick burst of speed in the direction they are looking and use up some stamina. It should have a 2-second cooldown."
FIP Content: 
ADR Content: 
```

*Expected Output:*
```json
{{
  "description": "Defines a requested player ability for a short-duration dash in the forward direction. The feature is intended to consume stamina and be governed by a 2-second cooldown period. This feature would grant the player enhanced mobility for evasive maneuvers or quick repositioning.",
  "keywords": [
    "dash",
    "sprint",
    "player ability",
    "movement",
    "stamina",
    "cooldown"
  ]
}}
```

**Example 2: A feature that has been fully "Implemented".**

*Input:*
```
Feature Name: Player Dash Ability
Request Content: "I want the player to be able to dash..."
FIP Content: "The FIP describes implementing the dash by modifying the PlayerController..."
ADR Content: "Implemented the dash ability by adding a 'perform_dash' method to the PlayerController. This method uses the Ursina engine's animate_position function for smooth movement. A global cooldown timer in the UIManager was used to enforce the 2s cooldown. The final stamina cost was set to 15."
```

*Expected Output:*
```json
{{
  "description": "Implements a player dash ability via a 'perform_dash' method in the PlayerController, using the Ursina engine's animate_position function for smooth movement. This ability consumes 15 stamina and is managed by a 2-second global cooldown timer located in the UIManager. This provides a core mobility mechanic for the player.",
  "keywords": [
    "dash",
    "sprint",
    "player ability",
    "movement",
    "stamina",
    "cooldown",
    "PlayerController",
    "animate_position",
    "UIManager"
  ]
}}
```
""")

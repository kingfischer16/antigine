"""
chains.py
#########

This module contains predefined LCEL (Language Chain Expression Language) chains for use in other functions.
These chains are designed to facilitate common workflows and can be imported and utilized throughout the codebase.

"""
# Imports
from langchain_core.output_parsers import JsonOutputParser

from prompts import update_feature_description_prompt
from models import chat_model

# Chains
# ======

# Chain for updating feature descriptions
# ---------------------------------------
# Input: feature name, request_content, fip_content, adr_content
# Output: JSON object with "description" and "keywords" fields
feature_description_update_chain = update_feature_description_prompt | chat_model | JsonOutputParser()


PROMPT = """You are tasked with generating a structured query based on a question about a car. Your goal is to create a JSON object containing three key elements: "type", "tags", and "keywords". These elements will be used to construct a WHERE clause for a database query.

Here is the question about a car: {question}

Analyze the question and generate a JSON object with the following structure:
- "type": Determines where the information comes from. It can be "page", "table", or "image".
- "tags": An array of relevant tags from the following options: "RECOMMENDATION", "COMPONENT", "FEATURE", "OPERATIONAL_GUIDE", "OTHER".
- "keywords": An array of general keywords that help narrow down the query.

To determine the "type":
- Use "page" if the question seems to require general textual information.
- Use "table" if the question is about specific data or comparisons.
- Use "image" if the question is about visual aspects of the car.

To generate "tags":
- Include "RECOMMENDATION" if the question asks for advice or suggestions.
- Include "COMPONENT" if the question is about specific car parts.
- Include "FEATURE" if the question is about car capabilities or characteristics.
- Include "OPERATIONAL_GUIDE" if the question is about how to use or operate the car.
- Include "OTHER" if the question doesn't fit into the above categories.

To create "keywords":
- Identify the main subjects and actions in the question.
- Include synonyms or related terms that could be relevant to the query.
- Focus on words that are specific to cars and the particular aspect being asked about.

Only include fields that have non-empty values. If a field would be empty based on the question, omit it from the JSON output.

make sure your output is in JSON format and it contains the three keys: type, tags, and keywords.
"""

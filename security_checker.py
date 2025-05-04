import os
import argparse
from openai import OpenAI
import json

def check_code_security(code_content: str, api_key: str):
    """
    Sends code content to OpenAI for security analysis,
    and returns the structured output.
    
    Args:
        code_content (str): The string containing the code to analyze.
        api_key (str): The OpenAI API key.

    Returns:
        list | str: A list of issue dictionaries or an error string.
    """
    # Removed file reading logic - content is now passed directly
    if not isinstance(code_content, str):
         return "Error: Invalid code content provided (must be a string)."
    if not code_content:
        return "Error: Code content is empty."

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o", # Or whichever model you prefer
            messages=[
                {"role": "system", "content": "You are a security analysis assistant. Analyze the provided code for potential errors and security vulnerabilities. Respond ONLY with a JSON list of unique findings. Each object in the list should represent a distinct issue and have 'line' (the approximate line number, or null if general), 'severity' (e.g., 'High', 'Medium', 'Low', 'Info'), and 'issue' (a concise description of the error or concern). Do not repeat the same finding for the same line."},
                {"role": "user", "content": f"Analyze this code:\n\n```\n{code_content}\n```"}
            ],
            temperature=0.2, # Lower temperature for more deterministic output
        )
        
        # Extract the JSON response content
        analysis_result = response.choices[0].message.content
        
        # Clean the response: Remove potential markdown fences and surrounding whitespace
        cleaned_result = analysis_result.strip()
        if cleaned_result.startswith("```json"):
            cleaned_result = cleaned_result[7:] # Remove ```json
        if cleaned_result.startswith("```"):
             cleaned_result = cleaned_result[3:] # Remove ```
        if cleaned_result.endswith("```"):
            cleaned_result = cleaned_result[:-3] # Remove ```
        cleaned_result = cleaned_result.strip()

        # Attempt to parse the cleaned JSON string
        try:
            structured_output = json.loads(cleaned_result)
            return structured_output
        except json.JSONDecodeError as json_err:
             # Include the cleaned string and the specific JSON error in the message
             return f"Error: Could not parse the response from the AI as JSON.\\nParsing error: {json_err}\\nCleaned response attempt:\\n{cleaned_result}"
        
    except Exception as e:
        return f"Error interacting with OpenAI API: {e}"

def main():
    parser = argparse.ArgumentParser(description="Analyze a code file for security issues using OpenAI (CLI mode).")
    parser.add_argument("file_path", help="Path to the code file to analyze.")
    parser.add_argument("--api-key", required=True, help="Your OpenAI API key.") 

    args = parser.parse_args()
    
    # Read file content for CLI mode
    try:
        with open(args.file_path, 'r') as f:
            code_content_for_cli = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {args.file_path}")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # Use the core function with the read content
    result = check_code_security(code_content_for_cli, args.api_key)

    # --- Output formatting for CLI mode ---
    if isinstance(result, str) and result.startswith("Error:"):
        print(result)
    elif isinstance(result, list):
        print("Security Analysis Results:")
        if not result:
            print("No issues found.")
        else:
            reported_lines = set()
            unique_issues_count = 0
            for item in result:
                 line = item.get('line')
                 # Try converting line to int if possible
                 report_key = None
                 if line is not None:
                     try:
                         report_key = int(line)
                     except (ValueError, TypeError):
                         report_key = line # Keep original if not convertible
                 else:
                     report_key = None # Keep None as None
                 
                 # Only print if the line number hasn't been reported yet or is None
                 if report_key is None or report_key not in reported_lines:
                     print(f"- Line: {item.get('line', 'N/A')}, Severity: {item.get('severity', 'N/A')}, Issue: {item.get('issue', 'N/A')}")
                     if report_key is not None:
                         reported_lines.add(report_key)
                     unique_issues_count += 1
            
            if unique_issues_count == 0 and len(result) > 0:
                 print("(Filtered out all reports - potentially duplicates on same line)")
            elif unique_issues_count < len(result):
                 print(f"(Filtered {len(result) - unique_issues_count} duplicate line reports)")
                 
    else:
        print("Received unexpected result format:")
        print(result)
    # --- End of output formatting for CLI mode ---

if __name__ == "__main__":
    main() 
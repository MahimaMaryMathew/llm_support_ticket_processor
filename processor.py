
import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv
from collections import Counter

 
load_dotenv()


client = genai.Client()

def classify_ticket(ticket_text):
    """
    Sends a support ticket to Gemini and requests a structured JSON response.
    """
    prompt = f"""
    Analyze the customer support ticket below and return a valid JSON object with EXACTLY these three keys:
    1. "category": Choose from ["Billing", "Technical", "General"]
    2. "urgency": Choose from ["Low", "Medium", "High", "Critical"]
    3. "suggested_action": A short, clear instruction for the support team on how to handle this ticket.

    Ticket: "{ticket_text}"
    """

    try:   
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite',  
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction="You are a precise JSON-emitting support triage assistant.",
                response_mime_type="application/json",
                temperature=0.1
            )
        )
        
        parsed_data = json.loads(response.text)
        return parsed_data

    except json.JSONDecodeError as jde:
        print(f"  [Error] Failed to parse JSON response: {jde}")
        return {"category": "Unclassified", "urgency": "Unknown", "suggested_action": "Manual review required due to parsing error."}
    except Exception as e:
        print(f"  [Error] API call failed: {e}")
        return {"category": "Unclassified", "urgency": "Unknown", "suggested_action": "Manual review required due to API error."}

def generate_summary(results):
    """
    Generates and prints a summary showing ticket counts by category and urgency.
    """
    categories = [r.get("category", "Unclassified") for r in results]
    urgencies = [r.get("urgency", "Unknown") for r in results]

    cat_counts = Counter(categories)
    urg_counts = Counter(urgencies)

    print("\n" + "="*40)
    print("       SUPPORT TICKET SUMMARY (GEMINI)")
    print("="*40)
    
    print("\nTickets by Category:")
    for cat, count in cat_counts.items():
        print(f"  - {cat}: {count}")

    print("\n Tickets by Urgency:")
    for urg, count in urg_counts.items():
        print(f"  - {urg}: {count}")
    print("="*40)

def main():
    
    with open("tickets.json", "r") as f:
        tickets = json.load(f)

    processed_results = []
    print(f"Processing {len(tickets)} support tickets using Google Gemini...\n")

    for ticket in tickets:
        print(f"Processing Ticket ID: {ticket['id']} ({ticket['customer']})")
        classification = classify_ticket(ticket['message'])
        
        result = {
            "id": ticket['id'],
            "customer": ticket['customer'],
            "original_message": ticket['message'],
            **classification
        }
        processed_results.append(result)

    
    with open("processed_results.json", "w") as f:
        json.dump(processed_results, f, indent=4)
    print("\nSaved all processed results to 'processed_results.json'.")

    
    generate_summary(processed_results)

if __name__ == "__main__":
    main()

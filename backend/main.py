from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import csv
from collections import defaultdict
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from pydantic import BaseModel
from typing import Dict
import os
import torch
from groq import Groq
from backend.routes.auth import auth_router
from backend.database.connection import get_user_collection




app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
app.include_router(auth_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to SanskritLingo API"}
@app.get("/test-db")
def test_db():
    users = get_user_collection()
    return {"users_count": users.count_documents({})}

# Configure absolute path with verification
CSV_PATH = Path(__file__).parent / "data" / "rigveda.csv"
print(f"CSV PATH VERIFICATION: {CSV_PATH.resolve()}")
print(f"FILE EXISTS: {CSV_PATH.exists()}")

# Precompute Hymn Offsets for all books
book_hymns = defaultdict(set)  # Store unique Hymn Numbers per Book
hymn_offsets = {}  # Store cumulative offsets

try:
    with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:  # Handle BOM
        reader = csv.DictReader(f)
        
        # Debug: Print headers and first row
        print("CSV HEADERS:", reader.fieldnames)
        first_row = next(reader, None)
        print("FIRST ROW SAMPLE:", first_row)
        
        f.seek(0)  # Reset file pointer
        reader = csv.DictReader(f)  # Reinitialize reader
        
        # Step 1: Collect Hymn Numbers for each Book
        for row in reader:
            try:
                book_num = row['Book Number'].strip()
                hymn_num = int(row['Hymn Number'].strip())
                book_hymns[book_num].add(hymn_num)
            except KeyError as e:
                print(f"Missing column in row: {e}")
                continue
            except ValueError as e:
                print(f"Invalid Hymn Number in row: {e}")
                continue
        
        # Step 2: Calculate Offsets
        cumulative_offset = 0
        for book in sorted(book_hymns.keys(), key=lambda x: int(x)):  # Ensure numerical order
            hymn_count = len(book_hymns[book])  # Count unique Hymn Numbers
            hymn_offsets[book] = cumulative_offset
            cumulative_offset += hymn_count
        
        print("Corrected Hymn Offsets:", hymn_offsets)

except Exception as e:
    print(f"ERROR LOADING CSV: {str(e)}")
    raise RuntimeError(f"Failed to load CSV: {str(e)}")


@app.get("/api/vedas/{book}/hymn{hymn}")
def get_hymn(book: str, hymn: int):
    """
    Endpoint to retrieve verses for a specific Book and Hymn.
    """
    try:
        print(f"Requested Book: {book}, Hymn: {hymn}")  # Debugging Request Parameters
        
        # Adjust Hymn Number based on offset
        if book not in hymn_offsets:
            raise HTTPException(status_code=404, detail="Invalid Book Number.")
        
        adjusted_hymn_number = hymn + hymn_offsets[book]
        print(f"Adjusted Hymn Number: {adjusted_hymn_number}")
        
        with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:  # Handle BOM
            reader = csv.DictReader(f)
            
            # Strip whitespace from header names
            reader.fieldnames = [name.strip() for name in reader.fieldnames]
            print("CSV Headers:", reader.fieldnames)  # Debugging Headers

            verses = []
            for row in reader:
                try:
                    # Compare after stripping and ensuring lowercase
                    if (str(row['Book Number']).strip().lower() == str(book).strip().lower() and 
                        int(row['Hymn Number'].strip()) == adjusted_hymn_number):
                        verses.append({
                            "verse": row['Verse Number'].strip(),
                            "sanskrit": row['Sanskrit Verse'].strip(),
                            "translation": row['English Translation'].strip()
                        })
                except KeyError as e:
                    print(f"Missing column in row {row}: {e}")
                    continue
                    
            if not verses:
                print(f"404: No verses found for Book {book}, Hymn {hymn}")
                raise HTTPException(status_code=404, detail=f"404: No verses found for Book {book}, Hymn {hymn}")
                
            return {
                "book": book,
                "hymn": hymn,
                "verses": verses
            }
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/vedas/{book_number}/sukta-count")
def get_sukta_count(book_number: str):
    """
    Endpoint to get the count of Hymns (Suktas) in a specific Book.
    """
    print(f"Requested Book Number for Sukta Count: {book_number}")
    hymns = book_hymns.get(book_number)
    if not hymns:
        raise HTTPException(status_code=404, detail="Book not found or no Hymns available.")
    return {
        "book": book_number,
        "sukta_count": len(hymns)
    }

API_KEY = "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"

# Request Body Structure
class TextInput(BaseModel):
    text: str

# Translation Endpoint for Sanskrit to English using Llama-3.3-70b-versatile
@app.post("/translate/groq/english")
async def translate_to_english(input_data: TextInput) -> Dict[str, str]:
    client = Groq(api_key=API_KEY)
    text = input_data.text

    try:
        # Initialize Groq Chat Completion with Llama-3.3-70b-versatile
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": f"Translate this Sanskrit verse to English(Only give the translation(contextual) do not generate anything else): {text}"
                }
            ],
            temperature=0.7,  # Lower temperature for more accurate translations
            max_completion_tokens=1024,
            top_p=1,
            stream=True,  # Stream response for faster output
            stop=None,
        )

        # Collect the streamed response
        translated_text = ""
        for chunk in completion:
            translated_text += chunk.choices[0].delta.content or ""

        # Return the translated text
        return {"translation": translated_text.strip()}

    except Exception as e:
        print(f"ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to translate using Llama-3.3-70b-versatile")
    
# Request Body Structure
class TextInput(BaseModel):
    text: str

# Translation Endpoint for Sanskrit to English using Llama-3.3-70b-versatile
@app.post("/translate/groq/hindi")
async def translate_to_english(input_data: TextInput) -> Dict[str, str]:
    client = Groq(api_key=API_KEY)
    text = input_data.text

    try:
        # Initialize Groq Chat Completion with Llama-3.3-70b-versatile
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": f"Translate this Sanskrit verse to Hindi(Only give the translation do not generate anything else): {text}"
                }
            ],
            temperature=0.7,  # Lower temperature for more accurate translations
            max_completion_tokens=1024,
            top_p=1,
            stream=True,  # Stream response for faster output
            stop=None,
        )

        # Collect the streamed response
        translated_text = ""
        for chunk in completion:
            translated_text += chunk.choices[0].delta.content or ""

        # Return the translated text
        return {"translation": translated_text.strip()}

    except Exception as e:
        print(f"ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to translate using Llama-3.3-70b-versatile")
    
class TextInput(BaseModel):
    text: str

# Load Swami Tucat's Sanskrit to English model
MODEL_NAME = "Swamitucats/M2M100_Sanskrit_English"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

# Translation Endpoint using Swami Tucat's Model
@app.post("/translate/swami/eng")
async def translate_to_english(input_data: TextInput) -> Dict[str, str]:
    text = input_data.text

    try:
        # Prepare the input for the model
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        
        # Generate translation using the model
        with torch.no_grad():
            translated_tokens = model.generate(**inputs, max_length=1024, num_beams=5, early_stopping=True)

        # Decode the generated tokens to get the translation
        translated_text = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)

        return {"translation": translated_text.strip()}

    except Exception as e:
        print(f"ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to translate using Swami Tucat's Model")
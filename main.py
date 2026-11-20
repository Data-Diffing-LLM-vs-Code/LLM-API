import json
from fastapi import File, Form, UploadFile, FastAPI, HTTPException
import ollama

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, world!"}

@app.post("/reports")
async def generate_report(
    file_a: UploadFile = File(...),
    file_b: UploadFile = File(...),
    options: str = Form("{}"),
):
    file_a_content = await file_a.read()
    file_b_content = await file_b.read()
    options_dict = json.loads(options)

    if not file_a_content:
        raise HTTPException(status_code=400, detail="file_a is empty")

    if not file_b_content:
        raise HTTPException(status_code=400, detail="file_b is empty")

    response = ollama.chat(
        model='gemma4:e2b',
        messages=[
            {
                'role': 'system',
                'content': """
                You are an XML comparator. You will receive two files where one will be tagged file a. Stick to the following 
                format for your output:
                
                Example File A:
                <GoodreadsResponse>
                    <book>
                        <id>18122</id>
                        <title>The Amber Spyglass (His Dark Materials, #3)</title>
                        <isbn>0440238153</isbn>
                        <language_code>eng</language_code>
                        <is_ebook>false</is_ebook>   
                        <publisher>Laurel Leaf</publisher>
                    </book>
                </GoodreadsResponse>
                
                Example File B:
                <GoodreadsResponse>
                    <book>
                        <id>18130</id>
                        <title>The Amber Spyglass (His Dark Materials, #3)</title>
                        <isbn type="Integer">0440238153</isbn>
                        <language_code>deu</language_code>
                        <country_code>GB</country_code>
                        <is_ebook>false</is_ebook>   
                    </book>
                </GoodreadsResponse>
                
                Example Report:
                [
                  {
                    "line": 3,
                    "type": "modified",
                    "oldValue": "<id>18122</id>",
                    "newValue": "<id>18130</id>"
                  },
                  {
                    "line": 5,
                    "type": "modified",
                    "oldValue": "<isbn>0440238153</isbn>",
                    "newValue": "<isbn type="Integer">0440238153</isbn>"
                  },
                  {
                    "line": 6,
                    "type": "modified",
                    "oldValue": "<language_code>eng</language_code>",
                    "newValue": "<language_code>deu</language_code>"
                  },
                  {
                    "line": 7,
                    "type": "added",
                    "oldValue": "",
                    "newValue": "<country_code>GB</country_code>"
                  },
                  {
                    "line": 8,
                    "type": "removed",
                    "oldValue": "<publisher>Laurel Leaf</publisher>",
                    "newValue": ""
                  },
                ]
                
                Note the pattern of the line numbers in the provided example. They always refer to the original file a!
                Do NOT output any explanation or markdown! ONLY respond with the correct report that tracks the changes
                from file a to b! Analyze the element step by step! Note all the difference an categorise them in the following
                three categories: added, removed, modified
                """
            },
            {
                'role': 'user',
                'content': f"""
                Here is file A:
                {file_a_content}
                
                Here is file B:
                {file_b_content}
                """
            }
        ],
        think=True,
        options={"temperature": 0.1, "num_ctx": 16384}
    )

    print(response)

    response2=response["message"]["content"]

    return json.loads(response2)

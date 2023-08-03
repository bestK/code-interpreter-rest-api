import base64
from typing import Optional

from codeinterpreterapi import CodeInterpreterSession
from codeinterpreterapi.schema import File
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


class UserRequest(BaseModel):
    prompt: str
    openai_api_key: str
    model: Optional[str] = "gpt-3.5-turbo"
    file_base64: Optional[str]
    filename: Optional[str]
    resp_type: Optional[str] = "json"


@app.post("/run")
async def run(request: UserRequest):
    prompt = request.prompt
    file_base64 = request.file_base64
    filename = request.filename
    resp_type = request.resp_type
    openai_api_key = request.openai_api_key
    model = request.model

    input_files: list[File] = []
    if file_base64 is not None:
        _file = File(name=filename, content=base64.b64decode(file_base64))
        input_files.append(_file)

    # create a session
    session = CodeInterpreterSession(model=model, openai_api_key=openai_api_key)

    # generate a response based on user input
    response = await session.generate_response(prompt, files=input_files)

    # output the response (text + image)
    print("AI: ", response.content)

    if resp_type == "html":
        html_content = f"<html><body>{response.content}"
        for file in response.files:
            file.show_image()
            # html_content += f'<h3>{file.name}</h3>'
            html_content += f'<img src="data:image/png;base64,{base64.b64encode(file.content).decode("utf-8")}"/><br/>'
        html_content += "</body></html>"
        response = Response(content=html_content, media_type="text/html")
    else:
        response = {
            "content": response.content,
            "files": [
                {
                    "name": file.name,
                    "content": base64.b64encode(file.content).decode("utf-8"),
                }
                for file in response.files
            ],
        }

        response = JSONResponse(content=response)
    # terminate the session
    await session.astop()

    return response

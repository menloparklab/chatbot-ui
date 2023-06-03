#!/usr/bin/env python3
import logging
from enum import StrEnum

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from lanarky.responses import StreamingResponse
from lanarky.routing import LangchainRouter, LLMCacheMode
from pydantic import BaseModel, constr

logger = logging.getLogger(__name__)

security = HTTPBearer()


def validate_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    api_key = credentials.credentials
    if not api_key:
        raise HTTPException(status_code=401, detail="OpenAI API key is missing")
    return api_key


class Role(StrEnum):
    SYSTEM = "system"
    ASSISTANT = "assistant"
    USER = "user"


class Message(BaseModel):
    role: constr(regex=f"^({Role.ASSISTANT}|{Role.USER}|{Role.SYSTEM})$")  # noqa: E501
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: list[Message]
    max_tokens: int
    temperature: float


def create_chain(
    model: str,
    messages: list[Message],
    max_tokens: int,
    temperature: float,
    openai_api_key: str,
):
    from langchain.chains import LLMChain
    from langchain.chat_models import ChatOpenAI
    from langchain.memory import ConversationBufferMemory
    from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory
    from langchain.prompts.chat import (
        ChatPromptTemplate,
        HumanMessagePromptTemplate,
        MessagesPlaceholder,
        SystemMessagePromptTemplate,
    )

    system_prompt = next(
        (message.content for message in messages if message.role == Role.SYSTEM),
        "You are a helpful assistant",
    )
    chat_prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(system_prompt),
            MessagesPlaceholder(variable_name="history"),
            HumanMessagePromptTemplate.from_template("{query}"),
        ]
    )

    chat_memory = ChatMessageHistory()
    for message in messages:
        if message.role == Role.USER:
            chat_memory.add_user_message(message.content)
        elif message.role == Role.ASSISTANT:
            chat_memory.add_ai_message(message.content)

    memory = ConversationBufferMemory(
        chat_memory=chat_memory, input_key="query", return_messages=True
    )

    llm = ChatOpenAI(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        openai_api_key=openai_api_key,
        streaming=True,
        verbose=True,
    )

    return LLMChain(
        llm=llm, prompt=chat_prompt, memory=memory, verbose=True, output_key="answer"
    )


router = LangchainRouter(llm_cache_mode=LLMCacheMode.IN_MEMORY)


@router.post(
    "/chat",
    summary="Langchain Chat",
    description="Chat with OpenAI's chat models using Langchain",
)
def chat(request: ChatRequest, openai_api_key: str = Depends(validate_api_key)):
    chain = create_chain(
        model=request.model,
        messages=request.messages[:-1],
        max_tokens=request.max_tokens,
        temperature=request.temperature,
        openai_api_key=openai_api_key,
    )
    return StreamingResponse.from_chain(chain, request.messages[-1].content)


app = FastAPI(dependencies=[Depends(validate_api_key)])
app.include_router(router, tags=["chat"])

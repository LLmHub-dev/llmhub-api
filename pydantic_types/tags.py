from pydantic import BaseModel
from typing import List, Optional


class Tag(BaseModel):
    name: str
    description: str


class Assistants(Tag):
    name: str = "Assistants"
    description: str = "Build Assistants that can call models and use tools."


class Audio(Tag):
    name: str = "Audio"
    description: str = "Turn audio into text or text into audio."


class Chat(Tag):
    name: str = "Chat"
    description: str = (
        "Given a list of messages comprising a conversation, the model will return a response."
    )


class Completions(Tag):
    name: str = "Completions"
    description: str = (
        "Given a prompt, the model will return one or more predicted completions, and can also return the probabilities of alternative tokens at each position."
    )


class Embeddings(Tag):
    name: str = "Embeddings"
    description: str = (
        "Get a vector representation of a given input that can be easily consumed by machine learning models and algorithms."
    )


class FineTuning(Tag):
    name: str = "Fine-tuning"
    description: str = (
        "Manage fine-tuning jobs to tailor a model to your specific training data."
    )


class Batch(Tag):
    name: str = "Batch"
    description: str = "Create large batches of API requests to run asynchronously."


class Files(Tag):
    name: str = "Files"
    description: str = (
        "Files are used to upload documents that can be used with features like Assistants and Fine-tuning."
    )


class Uploads(Tag):
    name: str = "Uploads"
    description: str = "Use Uploads to upload large files in multiple parts."


class Images(Tag):
    name: str = "Images"
    description: str = (
        "Given a prompt and/or an input image, the model will generate a new image."
    )


class Models(Tag):
    name: str = "Models"
    description: str = "List and describe the various models available in the API."


class Moderations(Tag):
    name: str = "Moderations"
    description: str = (
        "Given text and/or image inputs, classifies if those inputs are potentially harmful."
    )


class AuditLogs(Tag):
    name: str = "Audit Logs"
    description: str = (
        "List user actions and configuration changes within this organization."
    )


# Model for the full list of tags
class TagList(BaseModel):
    tags: List[Tag]


# Example to initialize all tags
all_tags = TagList(
    tags=[
        Assistants(),
        Audio(),
        Chat(),
        Completions(),
        Embeddings(),
        FineTuning(),
        Batch(),
        Files(),
        Uploads(),
        Images(),
        Models(),
        Moderations(),
        AuditLogs(),
    ]
)

# Example usage:
print(all_tags)

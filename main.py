from pathlib import Path
from openai import OpenAI
import json

configFilePath = Path(__file__).parent / "config.json"
with configFilePath.open("r", encoding="utf-8") as file:
    config = json.load(file)

openAIModel = config["openAIModel"]
openAIVoice = config["openAIVoice"]
defaultTitle = config["defaultTitle"]
defaultIdNumber = config["defaultIdNumber"]

client = OpenAI()

inputFilePath = Path(__file__).parent / "text.txt"
with inputFilePath.open("r", encoding="utf-8") as file:
    text = file.read()

def printf(text, process, type):
    print(f"[TTS: {process}] [{type}]: {text}")

printf(f"Enter Title Text ({defaultTitle}): ", "Main", "INFO")
title = input()

if len(title) == 0:
    title = defaultTitle

printf(f"Enter ID Number ({defaultIdNumber}): ", "Main", "INFO")
idNumber = input()

if len(idNumber) == 0:
    idNumber = defaultIdNumber

printf(f"Title Text: {title}", "Main", "INFO")
printf(f"ID Number: {idNumber}", "Main", "INFO")

def splitTextIntoChunks(text):
    printf("Splitting text into chunks of 4000 characters...", "Chunker", "INFO")
    words = text.split()
    chunks = []
    currentChunk = []
    currentLength = 0

    for word in words:
        wordLength = len(word) + 1
        if currentLength + wordLength > 4000:
            chunks.append(" ".join(currentChunk))
            currentChunk = []
            currentLength = 0
        currentChunk.append(word)
        currentLength += wordLength

    if currentChunk:
        chunks.append(" ".join(currentChunk))

    printf("Text split into chunks successfully.", "Chunker", "INFO")

    return chunks

chunks = splitTextIntoChunks(text)

for i, chunk in enumerate(chunks):
    printf(f"Generating audio file {i+1} of {len(chunks)}...", "TTS System", "INFO") 
    part = ""

    if len(chunks) > 1:
        part = f" Part {i+1} of {len(chunks)}"

    speechFilePath = Path(__file__).parent / f"{title} {idNumber}{part}.mp3"
    response = client.audio.speech.create(
        model=openAIModel,
        voice=openAIVoice,
        input=chunk
    )
    response.stream_to_file(speechFilePath)
    printf(f"Audio file {i+1} of {len(chunks)} generated.", "TTS System", "INFO")

printf("Audio files generated successfully.", "Main", "INFO")
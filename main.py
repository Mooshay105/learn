from pathlib import Path
from openai import OpenAI
import json
import subprocess

configFilePath = Path(__file__).parent / "config.json"
with configFilePath.open("r", encoding="utf-8") as file:
    config = json.load(file)

openAIModel = config["openAIModel"]
openAIVoice = config["openAIVoice"]
openAIInstructions = config["openAIInstructions"]
defaultTitle = config["defaultTitle"]
defaultIdNumber = config["defaultIdNumber"]

client = OpenAI()

inputFilePath = Path(__file__).parent / "text.txt"
with inputFilePath.open("r", encoding="utf-8") as file:
    text = file.read()

def printf(text, type):
    print(f"[TTS] [{type}]: {text}")

printf(f"Enter Title Text ({defaultTitle}): ", "INFO")
title = input()

if len(title) == 0:
    title = defaultTitle

printf(f"Enter ID Number ({defaultIdNumber}): ", "INFO")
idNumber = input()

if len(idNumber) == 0:
    idNumber = defaultIdNumber

printf(f"Title Text: {title}", "INFO")
printf(f"ID Number: {idNumber}", "INFO")

def splitTextIntoChunks(text):
    printf("Splitting text into chunks of 4000 characters...", "INFO")
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

    printf("Text split into chunks successfully.", "INFO")

    return chunks

chunks = splitTextIntoChunks(text)

for i, chunk in enumerate(chunks):
    printf(f"Generating audio file {i+1} of {len(chunks)}...", "INFO") 
    part = ""

    if len(chunks) > 1:
        part = f" Part {i+1} of {len(chunks)}"

    speechFilePath = Path(__file__).parent / f"{title} {idNumber}{part}.mp3"
    #response = client.audio.speech.create(
    #    model=openAIModel,
    #    voice=openAIVoice,
    #    input=chunk
    #)
    #response.stream_to_file(speechFilePath)
    with client.audio.speech.with_streaming_response.create(
        model=openAIModel,
        voice=openAIVoice,
        input=chunk,
        instructions=openAIInstructions
    ) as response:
        response.stream_to_file(speechFilePath)
    printf(f"Audio file {i+1} of {len(chunks)} generated.", "INFO")

if len(chunks) > 1:
    filesPath = "files.txt"
    with open(filesPath, "w") as f:
        for i, chunk in enumerate(chunks):
            f.write(f"file '{title} {idNumber} Part {i+1} of {len(chunks)}.mp3'\n")


    # Run FFmpeg to concatenate
    printf("Running FFmpeg to concatenate audio files...", "INFO")
    with open("/dev/null", "w") as devnull:
        subprocess.run(
            ["ffmpeg", "-f", "concat", "-safe", "0", "-i", filesPath, "-c", "copy", f"{title} {idNumber}.mp3"],
            stdout=devnull, stderr=devnull, check=True
	    )
    printf(f"Audio file {title} {idNumber}.mp3 generated.", "INFO")

    # Delete the files
    printf("Deleting old audio files...", "INFO")
    for i, chunk in enumerate(chunks):
        filePath = Path(__file__).parent / f"{title} {idNumber} Part {i+1} of {len(chunks)}.mp3"
        filePath.unlink()
    printf("Old audio files deleted successfully.", "INFO")

printf("Audio files generated successfully.", "INFO")
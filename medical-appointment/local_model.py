"""Small, fully local baseline for the medical appointment challenge."""

import logging
import os
import re
from io import BytesIO

import numpy as np
import onnxruntime as ort
from faster_whisper import WhisperModel
from tokenizers import Tokenizer

from dtos import ASRQuestionRequestDto, ASRQuestionResponseDto
from utils import decode_audio


def required_path(name: str) -> str:
    path = os.environ.get(name)
    if not path or not os.path.isdir(path):
        raise RuntimeError(f"Set {name} to an existing local model directory")
    return path


ASR = WhisperModel(
    required_path("ASR_MODEL_DIR"),
    device=os.environ.get("ASR_DEVICE", "cpu"),
    compute_type=os.environ.get("ASR_COMPUTE_TYPE", "int8"),
    cpu_threads=int(os.environ.get("ASR_CPU_THREADS", "8")),
)
NLI_DIR = required_path("NLI_MODEL_DIR")
TOKENIZER = Tokenizer.from_file(os.path.join(NLI_DIR, "tokenizer.json"))
TOKENIZER.enable_truncation(max_length=256)
TOKENIZER.enable_padding(pad_id=0, pad_token="[PAD]")
NLI = ort.InferenceSession(
    os.path.join(NLI_DIR, "onnx", "model_quint8_avx2.onnx"),
    providers=["CPUExecutionProvider"],
)

STOP = set(
    "a an the is are was were did does do has have had can could should would "
    "will be been being to with on for of in at by from there any some it its "
    "this that their they he she we you i patient doctor whether if about "
    "actually really found given said discussion mention visit".split()
)


def content_words(text: str) -> set[str]:
    words = set()
    for word in re.findall(r"[a-z]+|\d+(?:\.\d+)?", text.lower()):
        if word in STOP:
            continue
        if len(word) > 5 and word.endswith("ing"):
            word = word[:-3]
        elif len(word) > 4 and word.endswith("ed"):
            word = word[:-2]
        elif len(word) > 4 and word.endswith("s"):
            word = word[:-1]
        words.add(word)
    return words


def windows_from(segments: list[dict]) -> list[tuple[float, float, str]]:
    windows = []
    for i in range(len(segments)):
        for width in (1, 2, 3):
            chunk = segments[i : i + width]
            if len(chunk) == width:
                windows.append(
                    (chunk[0]["start"], chunk[-1]["end"], " ".join(s["text"] for s in chunk))
                )
    return windows

def narrow_evidence(
    question: str, window: tuple[float, float, str], segments: list[dict]
) -> tuple[float, float]:
    """Choose a question-matching speech segment inside the selected window."""
    question_words = content_words(question)
    candidates = []
    for index, segment in enumerate(segments):
        if segment["start"] < window[0] - 0.02 or segment["end"] > window[1] + 0.02:
            continue
        overlap = len(question_words & content_words(segment["text"]))
        if overlap:
            duration = segment["end"] - segment["start"]
            candidates.append((overlap, -duration, index))
    if not candidates:
        return window[0], window[1]
    segment = segments[max(candidates)[2]]
    return segment["start"], segment["end"]


def entailment_scores(questions: list[str], windows: list[tuple[float, float, str]]) -> np.ndarray:
    pairs = [(window[2], question) for question in questions for window in windows]
    encoded = TOKENIZER.encode_batch(pairs)
    ids = np.asarray([item.ids for item in encoded], dtype=np.int64)
    masks = np.asarray([item.attention_mask for item in encoded], dtype=np.int64)
    logits = np.concatenate(
        [
            NLI.run(None, {"input_ids": ids[i : i + 32], "attention_mask": masks[i : i + 32]})[0]
            for i in range(0, len(ids), 32)
        ]
    )
    exp = np.exp(logits - logits.max(axis=1, keepdims=True))
    return (exp / exp.sum(axis=1, keepdims=True))[:, 1].reshape(len(questions), len(windows))


def predict(request: ASRQuestionRequestDto) -> ASRQuestionResponseDto:
    try:
        audio = BytesIO(decode_audio(request.audio_base64))
        raw_segments, _ = ASR.transcribe(audio, language="en", beam_size=3, vad_filter=True)
        segments = [
            {"start": segment.start, "end": segment.end, "text": segment.text.strip()}
            for segment in raw_segments
        ]
        windows = windows_from(segments)
        if not windows:
            raise ValueError("No speech segments found")
        scores = entailment_scores(request.questions, windows)
        answers, starts, ends = [], [], []
        for question, row in zip(request.questions, scores):
            words = content_words(question)
            candidates = []
            for index, window in enumerate(windows):
                overlap = len(words & content_words(window[2])) / max(1, len(words))
                if overlap > 0:
                    candidates.append((float(row[index]) * (0.5 + 0.5 * overlap), float(row[index]), index))
            if candidates:
                _, confidence, index = max(candidates)
                answer = confidence >= 0.20
            else:
                answer, index = False, 0
            answers.append(answer)
            if answer:
                start, end = narrow_evidence(question, windows[index], segments)
                starts.append(start)
                ends.append(end)
            else:
                starts.append(None)
                ends.append(None)
    except Exception:
        logging.exception("Local prediction failed for %s", request.audio_filename)
        answers = [False] * len(request.questions)
        starts = [None] * len(request.questions)
        ends = [None] * len(request.questions)
    return ASRQuestionResponseDto(answers=answers, evidence_start=starts, evidence_end=ends)

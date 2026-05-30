import re
from typing import Generator

from vidsift.shared.text_normalizer import TextNormalizer


class TranscriptChunkGenerator:
    def __init__(self, char_chunk_size: int):
        self.char_chunk_size = char_chunk_size
        self.text_normalizer = TextNormalizer()

    def split_into_sentences(self, transcript: str) -> Generator[str, None, None]:
        sentence_splitters = ['.', '!', '?', '\n']
        next_sentence: list[str] = []
        for char in transcript:
            next_sentence.append(char)
            if char in sentence_splitters:
                to_yield = ''.join(next_sentence)
                yield self.text_normalizer.normalize(re.sub("\n", " ", to_yield))  # Replace newlines with spaces in the yielded sentence
                next_sentence = []
            elif len(next_sentence) >= self.char_chunk_size:
                if char.isspace():
                    to_yield = ''.join(next_sentence)
                    yield self.text_normalizer.normalize(re.sub("\n", " ", to_yield))  # Replace newlines with spaces in the yielded sentence
                    next_sentence = []
        if next_sentence:
            to_yield = ''.join(next_sentence)
            yield self.text_normalizer.normalize(re.sub("\n", " ", to_yield))  # Replace newlines with spaces in the yielded sentence

    def build_chunks(self, sentences: Generator[str, None, None]):
        current_chunk_sentences: list[str] = []
        char_count: int = 0

        for sentence in sentences:
            current_chunk_sentences.append(sentence)
            char_count += len(sentence)
            if char_count >= self.char_chunk_size:
                yield ''.join(current_chunk_sentences)
                current_chunk_sentences = []
                char_count = 0
        if current_chunk_sentences:
            yield ''.join(current_chunk_sentences)  # Yield any remaining sentences as the last chunk








if __name__ == "__main__":
    tcg = TranscriptChunkGenerator(char_chunk_size=30)
    transcript = """This is a sample transcript. 
It contains multiple sentences. 
Each sentence will be processed. 
This is the fourth sentence. 
And this is the fifth sentence. 
This is one random midldle sentence that is quite long and should be split into multiple chunks because it exceeds the chunk size.
This sentence is really long and should be included in the last chunk, and also it ends with a period."""
    for chunk in tcg.build_chunks(tcg.split_into_sentences(transcript)):
        print(f"Chunk: {repr(chunk)}")

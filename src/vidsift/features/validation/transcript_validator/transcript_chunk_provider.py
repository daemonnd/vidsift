import collections
from typing import Generator, Tuple

from vidsift.config.models import AppConfig
from vidsift.features.validation.errors import NoMiddleChunkError
from vidsift.shared.transcript_chunk_generator import TranscriptChunkGenerator


class TranscriptChunkProvider:
    def __init__(self, config: AppConfig):
        
        self.transcript_chunk_generator = TranscriptChunkGenerator(char_chunk_size=config.validation.transcript_chunk_char_size)


    def collect_chunk_metadata(self, transcript: str):
        """
        Method to get the first two chunks of the transcript for validation and the total number of chunks.
        Returns a tuple of the list of the first two chunks and the total number of chunks.
        Can raise an EmptyTranscriptError if the transcript is empty and cannot be chunked.
        """
        chunks: Generator[Tuple[str, int], None, None] = self.transcript_chunk_generator.build_chunks(
            sentences=self.transcript_chunk_generator.split_into_sentences(transcript=transcript)
        )


        first_chunks: list[str] = []
        last_chunks = collections.deque(maxlen=2)
        chunk_index: int = 0


        for chunk, chunk_index in chunks:
            if chunk_index < 2:
                first_chunks.append(chunk)
            last_chunks.append(chunk)
            #print(f"Chunks: {last_chunks}")

        total_chunks = chunk_index + 1

        return first_chunks, last_chunks, total_chunks

    def get_middle_chunk(self, transcript: str, total_chunk_index: int) -> str:
        """
        Method to get one middle chunk of the transcript for validation.
        Returns the middle chunk as a string.
        """
        chunks: Generator[Tuple[str, int], None, None] = self.transcript_chunk_generator.build_chunks(
            sentences=self.transcript_chunk_generator.split_into_sentences(transcript=transcript)
        )
        for chunk, chunk_index in chunks:
            if chunk_index == total_chunk_index // 2:
                return chunk

        raise NoMiddleChunkError("No middle chunk found in the transcript.")

    def remove_duplication(self, first_chunks: list[str], last_chunks) -> Tuple[list[str], list[str]]:
        for chunk in first_chunks:
            if chunk in last_chunks:
                last_chunks.remove(chunk)
        return first_chunks, last_chunks

    def get_necessary_chunks(self, transcript: str) -> str:
        """
        Method to get the necessary chunks of the transcript for validation.
        Returns a string containing the first two chunks, the middle chunk (if applicable), and the last two chunks of the transcript for validation.
        """
        first_chunks, last_chunks, chunk_index = self.collect_chunk_metadata(transcript=transcript)
        first_chunks, last_chunks = self.remove_duplication(
            first_chunks=first_chunks, 
            last_chunks=last_chunks
        )
        if chunk_index < 3:
            return f"""First Chunks:
{"\n".join(first_chunks)}


Last Chunks:
{"\n".join(last_chunks)}
"""

        else:
            middle_chunk = self.get_middle_chunk(transcript=transcript, total_chunk_index=chunk_index)
            return f"""First Chunks:
{"\n".join(first_chunks)}

Middle Chunk:
{middle_chunk}

Last Chunks:
{"\n".join(last_chunks)}
"""

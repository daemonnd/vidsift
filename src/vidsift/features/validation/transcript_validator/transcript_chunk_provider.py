import collections
from typing import Generator, Tuple

from vidsift.config.parser import TRANSCRIPT_CHUNK_CHAR_SIZE
from vidsift.features.validation.errors import NoMiddleChunkError
from vidsift.shared.transcript_chunk_generator import TranscriptChunkGenerator


class TranscriptChunkProvider:
    def __init__(self, char_chunk_size: int = TRANSCRIPT_CHUNK_CHAR_SIZE):
        self.transcript_chunk_generator = TranscriptChunkGenerator(char_chunk_size=char_chunk_size)


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
        Returns a tuple of the list of the first two chunks, the list of the last two chunks, and one middle chunk.
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







if __name__ == "__main__":
    tcp = TranscriptChunkProvider()
    transcript = """This is a sample transcript. 
    It contains multiple sentences. 
    Each sentence will be processed.
    This is the fourth sentence.
    And this is the fifth sentence.
    This is one random midldle sentence that is quite long and should be split into multiple chunks because it exceeds the chunk size.
    This sentence is really long and should be included in the last chunk,
    and also it ends with a period."""
    transcript = "this is simple."
    transcript = ""
    print(tcp.get_necessary_chunks(transcript=transcript))

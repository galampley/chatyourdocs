import pytest
from functions_v2 import chunk_content, read_pdf
#from PyPDF2 import PdfReader
from pypdf import PdfReader

def test_chunk_content():
    """
    Test the chunk_content function.
    """
    # Test content that is shorter than max_words
    content_short = "This is a short content."
    chunks_short = chunk_content(content_short, max_words=1000)
    assert len(chunks_short) == 1 and chunks_short[0] == content_short, "Failed for short content."

    # Test content that is exactly max_words long
    content_exact = " ".join(["word"] * 1000)
    chunks_exact = chunk_content(content_exact, max_words=1000)
    assert len(chunks_exact) == 1 and len(chunks_exact[0].split()) == 1000, "Failed for exact content."

    # Test content that is longer than max_words, which should result in multiple chunks
    content_long = " ".join(["word"] * 2001)
    chunks_long = chunk_content(content_long, max_words=1000)
    assert len(chunks_long) == 3, "Failed for long content."
    assert all(len(chunk.split()) == 1000 for chunk in chunks_long[:-1]), "Failed chunk size for long content."
    assert len(chunks_long[-1].split()) == 1, "Failed last chunk size for long content."

def test_read_pdf(monkeypatch):
    """
    Test the read_pdf function.
    """
    # Mock classes
    class MockPdfReader:
        def __init__(self, file_path):
            self.pages = [MockPdfPage()]

    class MockPdfPage:
        def extract_text(self):
            return "word " * 500  # Simulate 500 words per page

    # Mock the PdfReader to return a mock reader instance
    monkeypatch.setattr('pypdf.PdfReader', MockPdfReader)
    
    # Call read_pdf and assert the resulting chunks are as expected
    content_chunks = read_pdf("/Users/galampley/Desktop/ChatYourDocs/TheNeedToRead_Graham.pdf")
    assert len(content_chunks) == 1, "Failed to read and chunk PDF content correctly."

# Run the tests
if __name__ == '__main__':
    pytest.main()

from pypdf import PdfWriter

from backend.services.rag.document_loader import load_pdf


def test_load_pdf_file_not_found(tmp_path):
    pdf_path = tmp_path / "missing.pdf"

    try:
        load_pdf(str(pdf_path))
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError:
        assert True


def test_load_pdf_path_is_directory(tmp_path):
    try:
        load_pdf(str(tmp_path))
        assert False, "Expected ValueError"
    except ValueError:
        assert True


def test_load_pdf_empty_document(tmp_path):
    pdf_path = tmp_path / "empty.pdf"

    writer = PdfWriter()
    writer.add_blank_page(width=300, height=300)

    with open(pdf_path, "wb") as pdf_file:
        writer.write(pdf_file)

    try:
        load_pdf(str(pdf_path))
        assert False, "Expected ValueError"
    except ValueError as error:
        assert "no extractable text" in str(error)


def test_load_pdf_encrypted_document(tmp_path):
    pdf_path = tmp_path / "encrypted.pdf"

    writer = PdfWriter()
    writer.add_blank_page(width=300, height=300)
    writer.encrypt("test123")

    with open(pdf_path, "wb") as pdf_file:
        writer.write(pdf_file)

    try:
        load_pdf(str(pdf_path))
        assert False, "Expected ValueError"
    except ValueError as error:
        assert "Encrypted PDFs" in str(error)

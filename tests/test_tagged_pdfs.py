"""Mutate disposable copies of an actual tagged document; never edit public files."""
from pathlib import Path
import importlib.util
import tempfile
import unittest

try:
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import NameObject, TextStringObject, ArrayObject
except ImportError:
    PdfReader = None

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipIf(PdfReader is None, 'Install requirements-documents.txt for PDF tests')
class TaggedPdfSafety(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('pdf_auditor', ROOT/'scripts/audit_tagged_legal_candidates.py')
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def check_copy(self, mutate):
        writer = PdfWriter()
        writer.clone_document_from_reader(PdfReader(ROOT/'site/documents/hornigold-policies-pl.pdf'))
        mutate(writer)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'hornigold-policies-pl.pdf'
            with path.open('wb') as stream:
                writer.write(stream)
            return self.module.audit(path)['errors']

    def test_valid_document_passes(self):
        self.assertEqual(self.check_copy(lambda writer: None), [])

    def test_missing_structure_fails(self):
        errors = self.check_copy(lambda w: w.root_object.pop('/StructTreeRoot'))
        self.assertIn('Missing marked structure tree', errors)

    def test_wrong_language_fails(self):
        errors = self.check_copy(lambda w: w.root_object.__setitem__(NameObject('/Lang'), TextStringObject('en')))
        self.assertIn('Incorrect document language', errors)

    def test_changed_reading_order_fails(self):
        def mutate(w):
            top = w.root_object['/StructTreeRoot']['/K']
            document = top[0].get_object() if isinstance(top, list) else top.get_object()
            children = document['/K']
            children[0], children[1] = children[1], children[0]
        self.assertIn('Structure order differs from page content order', self.check_copy(mutate))

    def test_removed_link_fails(self):
        def mutate(w):
            for page in w.pages:
                annotations = page.get('/Annots', [])
                for index, annotation in enumerate(annotations):
                    if annotation.get_object().get('/Subtype') == '/Link':
                        page[NameObject('/Annots')] = ArrayObject(list(annotations[:index])+list(annotations[index+1:]))
                        return
            raise AssertionError('Fixture has no link')
        self.assertIn('Link annotation / structure references mismatch', self.check_copy(mutate))

    def test_unembedded_font_fails(self):
        def mutate(w):
            for page in w.pages:
                for font_ref in page['/Resources']['/Font'].values():
                    font = font_ref.get_object()
                    for child in font.get('/DescendantFonts', [font]):
                        descriptor = child.get_object().get('/FontDescriptor', {})
                        for key in ('/FontFile', '/FontFile2', '/FontFile3'):
                            descriptor.pop(key, None)
        self.assertIn('Font not embedded', self.check_copy(mutate))


if __name__ == '__main__':
    unittest.main()

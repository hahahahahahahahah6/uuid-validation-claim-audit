import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from uuid_validation_claim_audit.audit import audit, evidence, matches
from uuid_validation_claim_audit.phrases import UUIDVALIDATION, NOUUIDVALIDATION, GENERIC_NAMES

ROOT = Path(__file__).resolve().parents[1]

class AuditTests(unittest.TestCase):
    def test_routes(self):
        cases = ['import uuid\nuuid.UUID(x)', 'import uuid as u\nu.UUID(x)', 'from uuid import UUID\nUUID(x)', 'from uuid import UUID as U\nU(x)', 'import validators\nvalidators.uuid(x)', 'import validators as v\nv.uuid(x)', 'from validators import uuid\nuuid(x)', 'from validators import uuid as u\nu(x)']
        cases += ['obj.%s(x)' % name for name in GENERIC_NAMES]
        cases += ['from other import %s as f\nf(x)' % name for name in GENERIC_NAMES]
        cases += ['obj = factory()\nobj.validate_uuid(x)']
        for source in cases:
            with self.subTest(source=source): self.assertTrue(evidence(source))

    def test_non_evidence(self):
        cases = ['import uuid', 'import validators', 'UUID(x)', 'uuid(x)', 'obj.UUID(x)', 'obj.uuid(x)', 'import uuid\nuuid.getnode()', 'import re\nre.match(pattern, x)', 'import re\nre.search(pattern, x)', 'import re\nre.fullmatch(pattern, x)', 'from urllib.parse import urlparse\nurlparse(x)', 'from urllib.parse import urlsplit\nurlsplit(x)', 'payment.process(x)', 'extract(x)', 'import subprocess\nsubprocess.run(["validate uuid"])', '"validate uuid"', '# validate uuid', 'obj.validate_uuid', 'def broken(:', 'import uuid as u\nu = x\nu.UUID(x)', 'from uuid import UUID\ndef UUID(x): pass\nUUID(x)', 'def validate_uuid(x): pass\nobj.validate_uuid(x)']
        cases += ['import uuid\nuuid.uuid%s()' % n for n in (1,3,4,5)]
        cases += ['x.%s' % n for n in ('hex','int','bytes','bytes_le','fields','time','clock_seq','node','version','variant','urn')]
        cases += ['from pydantic import UUID%s\nx: UUID%s' % (n,n) for n in (1,3,4,5)]
        cases += ['from pydantic import UUID%s\nUUID%s(x)' % (n,n) for n in (1,3,4,5)]
        cases += ['import validators\nvalidators.%s(x)' % n for n in ('url','ipv4','ipv6','email','card_number','domain')]
        cases += ['import isbnlib\nisbnlib.%s(x)' % n for n in ('is_isbn10','is_isbn13','notisbn','Isbn')]
        cases += ['from stdnum import %s\n%s.%s(x)' % (n,n,fn) for n in ('isbn','issn','iban') for fn in ('validate','is_valid')]
        cases += ['from schwifty import IBAN\nIBAN(x)']
        for source in cases:
            with self.subTest(source=source): self.assertFalse(evidence(source))

    def test_phrases(self):
        self.assertEqual((len(UUIDVALIDATION),len(NOUUIDVALIDATION),len(GENERIC_NAMES)), (50,24,24))
        for phrase in UUIDVALIDATION:
            with self.subTest(phrase=phrase): self.assertTrue(matches(phrase)[0])
        for phrase in NOUUIDVALIDATION:
            with self.subTest(phrase=phrase): self.assertEqual(matches(phrase), ([],[phrase]))
        self.assertEqual(matches('```\nvalidate uuid\n```'), ([], []))
        self.assertTrue(matches('`validate uuid`')[0])

    def test_findings(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); doc=root/'README.md'; doc.write_text('validate uuid')
            self.assertEqual(audit(root)['findings'][0]['severity'], 'HIGH')
            (root/'tests').mkdir(); (root/'tests/test_x.py').write_text('import uuid\nuuid.UUID(x)')
            self.assertEqual(audit(root)['findings'][0]['severity'], 'MEDIUM')
            (root/'a.py').write_text('import uuid\nuuid.UUID(x)')
            self.assertFalse(audit(root)['findings'])
            doc.write_text('no uuid validation')
            self.assertEqual(audit(root)['findings'][0]['severity'], 'HIGH')
            (root/'a.py').unlink(); (root/'tests/test_x.py').unlink()
            self.assertFalse(audit(root)['findings'])
            doc.write_text('validate uuid'); (root/'a.py').write_text('import uuid'); (root/'b.py').write_text('uuid.UUID(x)')
            self.assertEqual(audit(root)['findings'][0]['severity'], 'HIGH')

    def test_cli(self):
        result=subprocess.run([sys.executable, '-m', 'uuid_validation_claim_audit', 'audit', str(ROOT), '--json'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0); self.assertEqual(json.loads(result.stdout)['findings'], [])
        self.assertEqual(audit(ROOT/'README.md')['findings'], [])

    def test_limitations_prose(self):
        text=(ROOT/'README.md').read_text().split('## Limitations',1)[1]
        self.assertEqual(matches(text), ([], []))

if __name__ == '__main__': unittest.main()

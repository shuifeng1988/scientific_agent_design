import unittest
import subprocess
import tempfile
import sys
import json
from pathlib import Path
from structured_output import decode_object, proposal_object
from recovery_policy import classify_failure


class StructuredTests(unittest.TestCase):
    def test_real_worker_wrapper_preserves_raw_and_recovers_extra_brace(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);request=root/'request.json';request.write_text('{"nodes":[],"state":{}}')
            fake=root/'fixture_codex.py'
            fake.write_text('#!'+sys.executable+'\nimport sys,pathlib\n'
                'pathlib.Path(sys.argv[sys.argv.index("--output-last-message")+1]).write_text('
                '\'{"contracts":[],"blocked":[]} }\')\n')
            fake.chmod(0o700)
            worker=Path(__file__).with_name('progress_worker.py')
            p=subprocess.run([sys.executable,'-B',str(worker),'--root',str(root),
                              '--request',str(request),'--codex',str(fake)],capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stderr)
            self.assertTrue((root/'proposal.raw.txt').read_text().endswith('} }'))
            self.assertEqual(json.loads((root/'proposal.json').read_text()),dict(contracts=[],blocked=[]))
            self.assertEqual(json.loads((root/'output_validation.json').read_text())['normalization']['removed_suffix'],'}')

    def test_single_extra_brace_repaired_and_logged(self):
        obj,audit=proposal_object('{"contracts":[],"blocked":[]} }')
        self.assertEqual(obj,dict(contracts=[],blocked=[]))
        self.assertEqual(audit['removed_suffix'],'}')

    def test_ambiguous_truncated_duplicate_nonfinite_rejected(self):
        for raw in ('{}{}','{} explanation','{','{"x":1,"x":2}','{"x":NaN}','[]','{} }}'):
            with self.subTest(raw=raw),self.assertRaises(ValueError):decode_object(raw,True)

    def test_missing_schema_fields_or_conflicting_nodes_rejected(self):
        for raw in ('{}','{"contracts":[],"blocked":"bad"}',
                    '{"contracts":[{"id":"A","contract":{}}],"blocked":[{"id":"A","reason":"x","needs_user":false}]}'):
            with self.subTest(raw=raw),self.assertRaises(ValueError):proposal_object(raw)

    def test_error_classification_is_not_claimed_root_cause(self):
        for text,category in [('JSONDecodeError: Extra data','serialization'),('ModuleNotFoundError','environment'),
                              ('CUDA out of memory','resources'),('Permission denied','credentials'),
                              ('Result=timeout','timeout'),('Connection reset','network'),('unknown','unclassified')]:
            d=classify_failure(dict(state='failed',log_tail=text))
            self.assertEqual(d['category'],category);self.assertFalse(d['root_cause_confirmed'])


if __name__=='__main__':unittest.main()

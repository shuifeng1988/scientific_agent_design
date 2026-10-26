"""Offline fake-host tests. Do not represent live provider quality or sandbox penetration tests."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
import literature_adapter as la
import module_provider as mp
import research_workflow as rw
import scientific_review as sr
import review_worker as worker
from test_research_workflow import build_project, fixture_review


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup); self.root=Path(self.tmp.name)
        build_project(self.root)

    def test_readonly_reviewer_receipts_and_target_tampering(self):
        d=rw.read(self.root/'registry/design.json');subject=sr.design_subject(self.root,self.root/d['proposal']['path'])
        source=self.root/'fixture_review.json';fixture_review(self.root,subject,source)
        response={k:rw.read(source)[k] for k in ('verdict','criteria','findings')}
        fake=self.root/'fake_codex'
        fake.write_text('#!'+sys.executable+'\nimport pathlib,sys,json\n'
            'assert "--approve-for-me" not in sys.argv\n'
            'assert sys.argv[sys.argv.index("--sandbox")+1]=="read-only"\n'
            'sys.stdin.read()\n'
            'pathlib.Path(sys.argv[sys.argv.index("--output-last-message")+1]).write_text('+repr(json.dumps(response))+')\n')
        fake.chmod(0o700)
        out=worker.run(self.root,subject,str(fake),10)
        self.assertFalse(out['accepted']);self.assertEqual(out['verdict'],'adequate')
        review=sr.verify(self.root,out['review'],subject)
        invocation=rw.read(rw.receipt(self.root,review['invocation']))
        self.assertEqual(invocation['sandbox'],'read-only')
        fake.write_text(fake.read_text()+'pathlib.Path('+repr(str(self.root/d['proposal']['path']))+').write_text("tampered")\n')
        with self.assertRaisesRegex(ValueError,'hash mismatch'):worker.run(self.root,subject,str(fake),10)

    def test_review_timeout_does_not_produce_accepted_receipt(self):
        d=rw.read(self.root/'registry/design.json');subject=sr.design_subject(self.root,self.root/d['proposal']['path'])
        fake=self.root/'slow_codex';fake.write_text('#!'+sys.executable+'\nimport time\ntime.sleep(10)\n');fake.chmod(0o700)
        with self.assertRaisesRegex(ValueError,'timed out'):worker.run(self.root,subject,str(fake),1)
        self.assertEqual(list((self.root/'provenance/reviews').glob('*/review.json')),[])

    def test_real_adapter_path_normalizes_synthetic_host_outputs(self):
        entry=self.root/'external/SKILL.md';entry.parent.mkdir();entry.write_text('---\nname: literature-review\n---\nSYNTHETIC fixture provider')
        rw.atomic(self.root/mp.CONFIG,la.config(entry,['codex']))
        request=mp.prepare(self.root,'evidence','codex','Synthetic case')
        appraisal=rw.read(self.root/'provenance/appraisal.json');appraisal['status']='ready_for_design_review'
        ap=request.with_name('appraisal.json');rw.atomic(ap,appraisal)
        raw=request.with_name('raw.txt');raw.write_text('SYNTHETIC raw outputs; no real search')
        out=la.normalize(self.root,request,ap,[raw],{'tools':['fake-host'], 'access_limits':['offline synthetic data']})
        self.assertTrue(out['handoff_valid']);self.assertFalse(out['task_complete'])
        raw.write_text('changed raw output')
        with self.assertRaises(ValueError):mp.check_output(self.root,request,request.with_name('output.json'))


if __name__ == '__main__':unittest.main()

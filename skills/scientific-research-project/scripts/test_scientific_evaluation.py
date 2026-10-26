"""Test scoring mechanics with artificial grades, never an observed quality score."""
from pathlib import Path
import copy
import tempfile
import unittest
import scientific_evaluation as se
import research_workflow as rw


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        se.export('analysis_units',self.root/'input')
        self.assertEqual([p.name for p in (self.root/'input').iterdir()],['case.json'])
        output=self.root/'output.txt';output.write_text('SYNTHETIC evaluator test; not an agent answer')
        self.runpath=self.root/'run.json';case=rw.descriptor(self.root/'input/case.json',self.root)
        self.run=dict(case=case,output=rw.descriptor(output,self.root),author_invocation_id='fixture-author',configuration='fixture',
                      comparison_context=dict(model='fixture',tools=[],budget={'tokens':100},environment='offline',input_sha256=case['sha256']),
                      observed_metrics=dict(elapsed_seconds=None,input_tokens=None,output_tokens=None,cost=None))
        rw.atomic(self.runpath,self.run)
        self.judgment=self.root/'judgment.json'
        rubric=rw.read(se.CASES/'analysis_units.rubric.json')
        self.j=dict(run=rw.descriptor(self.runpath,self.root),output=self.run['output'],reviewer_id='fixture-reviewer',human_review=True,
                    grades={c['id']:dict(score=2,rationale='synthetic test grade',response_locator='line 1') for c in rubric['criteria']})
        rw.atomic(self.judgment,self.j)

    def test_unobserved_grading_is_pending_and_cannot_be_compared(self):
        a=se.score(self.root,self.runpath)
        self.assertIsNone(a['score']);self.assertEqual(a['status'],'pending_human_review')
        with self.assertRaisesRegex(ValueError,'unreviewed'):se.compare(a,a)

    def test_critical_failure_not_hidden_by_average_and_context_must_match(self):
        a=se.score(self.root,self.runpath,self.judgment)
        self.j['grades']['pseudoreplication']['score']=0;rw.atomic(self.judgment,self.j)
        b=se.score(self.root,self.runpath,self.judgment)
        self.assertEqual(b['status'],'needs_revision');self.assertIn('pseudoreplication',b['critical_failures'])
        self.assertLess(se.compare(a,b)['score_difference'],0)
        b['comparison_context']['budget']={'tokens':200}
        with self.assertRaisesRegex(ValueError,'identical'):se.compare(a,b)

    def test_stale_run_or_self_grade_rejected(self):
        self.j['reviewer_id']='fixture-author';rw.atomic(self.judgment,self.j)
        with self.assertRaisesRegex(ValueError,'separate'):se.score(self.root,self.runpath,self.judgment)
        (self.root/'output.txt').write_text('changed response')
        with self.assertRaises(ValueError):se.score(self.root,self.runpath,self.judgment)


if __name__=='__main__':unittest.main()

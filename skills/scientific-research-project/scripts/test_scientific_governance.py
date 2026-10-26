"""Synthetic scientific-governance fixtures; no live model/reviewer/approval is claimed."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import research_workflow as rw
import scientific_review as sr
import plan_amendment as pa
import supplementary_tasks as st
import supervisor_daemon as sd
import project_events as pe
from test_research_workflow import build_project, prepare_report, finish_report, fixture_review, fixture_config


class GovernanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)

    def package(self):
        build_project(self.root)
        p=prepare_report(self.root,'Q01.01','R1');rw.render_report(self.root,'Q01.01',p)
        return finish_report(self.root,'Q01.01','R1')

    def event(self):
        return dict(event_type='qc.passed',task_id='Q01.01',verified=True,
                    path='results/Q01/Q01.01',message='SYNTHETIC fixture only',meta={})

    def test_new_freeze_requires_independent_review_without_mutating_roots(self):
        p,a=build_project(self.root,False)
        review=self.root/'provenance/design_review.json';review.unlink()
        with self.assertRaisesRegex(ValueError,'review receipt missing'):rw.freeze(self.root,p,a)
        self.assertFalse((self.root/'registry/design.json').exists())
        self.assertFalse((self.root/'02_SOFTWARE.md').exists())

    def test_self_review_stale_review_and_open_major_issue_rejected(self):
        result=self.package();path=result/'_evidence/scientific_review.json';original=rw.read(path)
        variants=[]
        r=copy.deepcopy(original);r['reviewer_invocation_id']=r['subject']['author_invocation_id'];variants.append(r)
        r=copy.deepcopy(original);r['subject']['run_id']='wrong';variants.append(r)
        r=copy.deepcopy(original);r['findings']=[dict(id='leakage',severity='major',status='open',
            rationale='SYNTHETIC leakage finding',evidence=r['subject']['targets'][:1])];variants.append(r)
        for r in variants:
            rw.atomic(path,r)
            with self.subTest(review=r),self.assertRaises(sr.ReviewPending):pe.emit(self.root,self.event())
        rw.atomic(path,original);pe.emit(self.root,self.event())
        self.assertEqual(rw.task(self.root,'Q01.01')['status'],'complete')

    def test_review_policy_cannot_be_removed_from_current_design(self):
        build_project(self.root);p=self.root/'registry/design.json';d=rw.read(p);d.pop('review_policy');rw.atomic(p,d)
        with self.assertRaisesRegex(ValueError,'policy drift'):rw.verify_design(self.root)

    def test_legacy_frozen_baseline_is_not_silently_upgraded(self):
        build_project(self.root)
        dp=self.root/'registry/design.json';d=rw.read(dp)
        pp=self.root/d['proposal']['path'];p=rw.read(pp);p.pop('review_policy');rw.atomic(pp,p)
        ap=self.root/d['approval']['path'];a=rw.read(ap);a['proposal_sha256']=rw.sha(pp);rw.atomic(ap,a)
        d.update(proposal=rw.descriptor(pp,self.root),approval=rw.descriptor(ap,self.root));d.pop('review_policy');d.pop('design_review')
        rw.atomic(dp,d)
        self.assertTrue(rw.verify_design(self.root)['passed'])

    def amendment(self):
        d=rw.read(self.root/'registry/design.json');p=copy.deepcopy(rw.read(self.root/d['proposal']['path']))
        p['version']='fixture-v2';p['amendment']=dict(base_design_sha256=rw.sha(self.root/'registry/design.json'),
            reason='SYNTHETIC additive research task',affected_task_ids=['Q01.03'],new_dependencies={'Q01.03':[]})
        p['tasks'].append(dict(task_id='Q01.03',question_id='Q01',title='New fixture',result_path='results/Q01/Q01.03',
                             required_models='fixture',required_data='fixture'))
        p['documents']['01_PLAN.md']+='\nQ01.03 results/Q01/Q01.03\n'
        appraisal=rw.read(self.root/p['appraisal']['path']);appraisal['status']='ready_for_design_review'
        ar=self.root/'provenance/revision/appraisal.json';rw.atomic(ar,appraisal);p['appraisal']=rw.descriptor(ar,self.root)
        pp=self.root/'provenance/revision/proposal.json';rw.atomic(pp,p)
        ap=self.root/'provenance/revision/approval.json';a=copy.deepcopy(rw.read(self.root/d['approval']['path']))
        a.update(proposal_sha256=rw.sha(pp),appraisal_sha256=rw.sha(ar));rw.atomic(ap,a)
        rp=self.root/'provenance/revision/review.json';fixture_review(self.root,sr.design_subject(self.root,pp),rp)
        return pp,ap,rp

    def test_amendment_preserves_completed_report_and_old_design(self):
        result=self.package();pe.emit(self.root,self.event())
        old_report=(result/'REPORT.docx').read_bytes();old_d=(self.root/'registry/design.json').read_bytes()
        paths=self.amendment();out=pa.apply(self.root,*paths)
        self.assertTrue(out['applied']);self.assertFalse(out['service_restarted'])
        self.assertEqual((result/'REPORT.docx').read_bytes(),old_report)
        self.assertEqual(rw.task(self.root,'Q01.01')['status'],'complete')
        self.assertEqual(rw.task(self.root,'Q01.03')['status'],'pending')
        self.assertTrue(rw.validate_package(self.root,'Q01.01','results/Q01/Q01.01','R1')['passed'])
        d=rw.read(self.root/'registry/design.json');h=rw.read(rw.receipt(self.root,d['history'][0]['design']))
        self.assertEqual(h['version'],'fixture-v1')
        self.assertFalse((self.root/pa.JOURNAL).exists())

    def test_amendment_refuses_unknown_job_and_rolls_back_write_failure(self):
        build_project(self.root);c=fixture_config(self.root);c['paused']=True;rw.atomic(self.root/'registry/supervisor.json',c)
        paths=self.amendment();s=self.root/'provenance/supervisor/state.json'
        rw.atomic(s,dict(nodes={'A':dict(status='unknown',attempt=1)}))
        with self.assertRaisesRegex(ValueError,'reconciled'):pa.apply(self.root,*paths)
        rw.atomic(s,dict(nodes={}))
        before={name:(self.root/name).read_bytes() for name in rw.ROOT_DOCS+('registry/design.json',)}
        with patch.object(pe,'rebuild',side_effect=RuntimeError('fixture write failure')):
            with self.assertRaisesRegex(RuntimeError,'fixture write'):pa.apply(self.root,*paths)
        self.assertEqual(before,{name:(self.root/name).read_bytes() for name in before})
        self.assertTrue(rw.verify_design(self.root)['passed'])
        self.assertTrue(pa.apply(self.root,*paths)['applied'])

    def test_amendment_rebinds_unstarted_scope_gates_without_auto_launch(self):
        build_project(self.root);c=fixture_config(self.root);c['paused']=True
        c['nodes'][0]['required_scope_gates']=[rw.descriptor(self.root/'01_PLAN.md',self.root)]
        c['nodes'][0]['contract']=None
        rw.atomic(self.root/'registry/supervisor.json',c)
        paths=self.amendment();out=pa.apply(self.root,*paths)
        updated=rw.read(self.root/'registry/supervisor.json')
        self.assertTrue(updated['paused']);self.assertFalse(out['service_restarted'])
        for n in updated['nodes']:
            self.assertIsNone(n['contract'])
            self.assertIn(rw.descriptor(self.root/'01_PLAN.md',self.root),n['required_scope_gates'])
        self.assertFalse((self.root/'provenance/supervisor/state.json').exists())

    def test_recover_precommit_and_postcommit_event_failure(self):
        build_project(self.root);paths=self.amendment()
        with patch.object(pe,'emit',side_effect=RuntimeError('fixture event outage')):
            with self.assertRaisesRegex(RuntimeError,'event outage'):pa.apply(self.root,*paths)
        self.assertEqual(rw.read(self.root/pa.JOURNAL)['stage'],'committed')
        self.assertTrue(pa.recover(self.root)['applied'])
        original=(self.root/'01_PLAN.md').read_text()
        rw.atomic(self.root/pa.JOURNAL,dict(stage='prepared',before={'01_PLAN.md':original}))
        rw.atomic(self.root/'01_PLAN.md','partial transaction')
        with self.assertRaisesRegex(ValueError,'recovery required'):rw.verify_design(self.root)
        self.assertTrue(pa.recover(self.root)['rolled_back'])
        self.assertTrue(rw.verify_design(self.root)['passed'])

    def supplement(self,necessity='required'):
        result=self.root/'results/Q01/Q01.01'
        source=result/'_evidence/reflection.json'
        c=fixture_config(self.root);rw.atomic(self.root/'registry/supervisor.json',c)
        spec=dict(task_id='Q01.01',id='control',necessity=necessity,rationale='fixture rationale',
            scope_justification='fixture within approved task',stopping_rule='one fixture check',
            analysis_label='exploratory_post_hoc',source=rw.descriptor(source,self.root),
            scope=rw.descriptor(self.root/'01_PLAN.md',self.root),depends_on=[],contract=None)
        p=result/'_evidence/supplement_spec.json';rw.atomic(p,spec)
        return p,st.register(self.root,p)

    def test_required_supplement_blocks_until_registered_verified_and_interpreted(self):
        result=self.package();p,out=self.supplement();self.assertTrue(st.register(self.root,p)['duplicate'])
        ref=rw.read(result/'_evidence/reflection.json')
        ref.update(decision='supplement',supplements=[dict(node_id=out['node_id'],necessity='required',rationale='fixture')])
        with self.assertRaisesRegex(ValueError,'pending'):st.verify_supplements(self.root,'Q01.01',ref)
        nr=self.root/out['result_path'];rw.atomic(nr/'README.md','fixture method');rw.atomic(nr/'data.txt','fixture result')
        rw.atomic(nr/'_evidence/qc.json',dict(run_id='SUP1',passed=True,artifacts=[rw.descriptor(nr/'data.txt',nr)]))
        rw.atomic(self.root/'provenance/supervisor/state.json',dict(nodes={out['node_id']:dict(status='complete',run_id='SUP1')}))
        with self.assertRaisesRegex(ValueError,'incorporated'):st.verify_supplements(self.root,'Q01.01',ref)
        ref['supplements'][0]['evidence']=[rw.descriptor(nr/'data.txt',self.root)]
        st.verify_supplements(self.root,'Q01.01',ref)
        rw.atomic(nr/'data.txt','tampered')
        with self.assertRaises(ValueError):st.verify_supplements(self.root,'Q01.01',ref)

    def test_optional_supplement_must_be_registered_but_need_not_finish(self):
        result=self.package();p,out=self.supplement('optional')
        ref=dict(decision='supplement',supplements=[dict(node_id=out['node_id'],necessity='optional',rationale='fixture')])
        st.verify_supplements(self.root,'Q01.01',ref)
        ref['supplements'][0]['node_id']='missing'
        with self.assertRaisesRegex(ValueError,'not registered'):st.verify_supplements(self.root,'Q01.01',ref)

    def test_supplement_cannot_deadlock_on_own_finalizer(self):
        self.package();p,out=self.supplement()
        s=rw.read(p);s['id']='deadlock';s['depends_on']=['Q01.01'];rw.atomic(p,s)
        with self.assertRaisesRegex(ValueError,'own scientific completion'):st.register(self.root,p)


if __name__=='__main__':unittest.main()

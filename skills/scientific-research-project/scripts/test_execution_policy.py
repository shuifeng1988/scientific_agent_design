import copy
import json
import time
from pathlib import Path
from unittest.mock import patch
import unittest
import test_supervisor_daemon as fixtures
import supervisor_daemon as sd
from execution_policy import apply_expansions, incident


class ExecutionFirstTests(unittest.TestCase):
    setUp = fixtures.SchedulingTests.setUp
    tearDown = fixtures.SchedulingTests.tearDown
    node = fixtures.SchedulingTests.node
    save_config = fixtures.SchedulingTests.save_config
    driver = fixtures.SchedulingTests.driver
    supervisor = fixtures.SchedulingTests.supervisor
    setup_worker = fixtures.SchedulingTests.setup_worker
    failed_interpret = fixtures.SchedulingTests.failed_interpret
    def artifact(self, index=0):
        n=self.config['nodes'][index]
        n['completion_policy']='artifact'
        del n['contract']['interpret']
        n['approved_contract_sha256']=sd.digest(n['contract'])
        self.config['execution_policy']='v2';self.save_config()
        return n

    def test_artifact_releases_compute_without_literature(self):
        n=self.artifact();s=self.supervisor();s.tick();a=s.state['nodes']['A']
        self.jobs[a['job_id']]=dict(state='succeeded');s.tick()
        d=self.root/n['result_path'];d.mkdir(parents=True)
        (d/'README.md').write_text('methods and provenance')
        sd.atomic(d/'_evidence/qc.json',dict(run_id=a['run_id'],passed=True,
                  artifacts=[dict(path='README.md',sha256=sd.file_hash(d/'README.md'))]))
        self.jobs[a['job_id']]=dict(state='succeeded');s.tick()
        self.assertTrue(a['artifact_verified'])
        self.assertEqual(a['status'],'complete')
        self.assertEqual(s.state['nodes']['C']['status'],'submitting')

    def test_artifact_cannot_bypass_science_or_bad_hash(self):
        n=self.artifact();n['finalizes_task']=True;self.save_config()
        with self.assertRaises(ValueError):sd.load_config(self.root)

    def test_full_node_dependency_table_is_generated(self):
        self.artifact();s=self.supervisor();s.tick()
        import csv
        with (self.root/'registry/task_dependencies.tsv').open() as f:
            rows=list(csv.DictReader(f,delimiter='\t'))
        self.assertEqual(len(rows),3)
        self.assertEqual(rows[0]['completion_policy'],'artifact')
        self.assertEqual(rows[2]['depends_on'],'A')

    def test_normal_planning_not_capped_by_legacy_call_count(self):
        self.setup_worker();self.config['execution_policy']='v2'
        self.config['progress_worker']['budget_scope']='per_node';self.save_config()
        s=self.supervisor();s.state['nodes']['A']=dict(status='pending',phase='run',attempt=0,planner_visits=30)
        s.tick();self.assertEqual(s.state['worker']['requested'],['A'])
        self.assertEqual(incident(s.state,s.state['nodes']['A'])['worker_calls'],0)

    def test_nonproductive_planning_stops_with_stall_not_success(self):
        self.setup_worker();self.config['execution_policy']='v2'
        self.config['progress_worker']['budget_scope']='per_node'
        self.config['nodes']=self.config['nodes'][:1];self.save_config()
        s=self.supervisor();s.state['nodes']['A']=dict(status='pending',phase='run',attempt=0,no_progress_visits=2)
        s.tick();self.assertNotIn('job_id',s.state['worker'])
        self.assertEqual(s.state['progression']['status'],'stalled')

    def expansion_fixture(self):
        self.setup_worker();self.config['execution_policy']='v2'
        p=self.config['nodes'][0];p['expansion_policy']=dict(models=['M1','M2'],stages=['prepare','compute'],
              stage_dependencies={'compute':['prepare']},max_new_nodes=4)
        self.save_config();s=self.supervisor();s.tick()
        nodes=[]
        for m in ('M1','M2'):
            for stage in ('prepare','compute'):
                nodes.append(dict(id='A.'+m+'.'+stage,model_id=m,stage=stage,task_id='Q01.01',
                     depends_on=[] if stage=='prepare' else ['A.'+m+'.prepare'],
                     result_path=p['result_path']+'/models/'+m+'/'+stage,scientific_result=False,
                     completion_policy='artifact',contract=None))
        return s,dict(parent_id='A',nodes=nodes)

    def test_expansion_retains_panel_and_rejects_renamed_or_partial(self):
        s,e=self.expansion_fixture()
        c,added=apply_expansions(self.config,s.state['nodes'],['A'],[e]);self.assertEqual(len(added),4)
        self.assertEqual(len(self.config['nodes']),3)
        e['nodes'][0]['id']='A.other'
        with self.assertRaises(ValueError):apply_expansions(self.config,s.state['nodes'],['A'],[e])
        e['nodes']=e['nodes'][1:]
        with self.assertRaises(ValueError):apply_expansions(self.config,s.state['nodes'],['A'],[e])

    def test_expansion_is_adopted_transactionally(self):
        s,e=self.expansion_fixture();w=s.state['worker']
        sd.atomic(Path(w['request']).with_name('proposal.json'),dict(contracts=[],blocked=[],expansions=[e]))
        self.jobs[w['job_id']]=dict(state='succeeded');s.tick()
        c=sd.load_config(self.root)
        self.assertEqual(len(c['nodes']),7)
        self.assertEqual(s.state['nodes']['A.M1.prepare']['status'],'pending')
        self.assertEqual(s.state['nodes']['A']['no_progress_visits'],0)

    def test_durable_hook_outage_does_not_stop_unrelated_artifact_launch(self):
        self.artifact()
        with patch.object(sd.Supervisor,'flush_events',return_value=False):
            s=self.supervisor();s.tick()
        self.assertEqual(s.state['nodes']['A']['status'],'submitting')
        self.assertTrue(s.state['outbox'])

    def test_failure_budget_is_phase_local_and_not_reset_by_new_job(self):
        s,a=self.failed_interpret();self.config['execution_policy']='v2';self.save_config();s.tick()
        a['execution_policy']='v2'
        inc=incident(s.state,a);inc.update(worker_calls=3,retries=3)
        before=copy.deepcopy(inc);a['job_id']='different-process-id'
        self.assertEqual(incident(s.state,a),before)
        self.assertEqual(incident(s.state,a,'run')['retries'],0)

    def test_publication_waits_for_its_hook_acknowledgement(self):
        s=self.supervisor();s.tick();n=self.config['nodes'][0];a=s.state['nodes']['A']
        self.hook.stop()
        s.event(n,'qc.passed','final package','complete')
        a.update(status='publishing',publication_event=s.state['outbox'][-1]['id'])
        hook=self.root/'scripts/hooks/project_event.py';hook.parent.mkdir(parents=True,exist_ok=True)
        hook.write_text('# fixture')
        with patch.object(sd.subprocess,'run',return_value=type('P',(),dict(returncode=1,stderr='outage'))()):
            self.assertFalse(sd.Supervisor.flush_events(s))
        self.assertEqual(a['status'],'publishing')
        with patch.object(sd.subprocess,'run',return_value=type('P',(),dict(returncode=0,stderr=''))()):
            self.assertTrue(sd.Supervisor.flush_events(s))
        self.assertEqual(a['status'],'complete')

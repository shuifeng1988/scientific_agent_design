"""Fast isolated regression checks: no GPU, network or real scientific jobs."""
import copy
import json
import tempfile
import subprocess
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import supervisor_daemon as sd


class SchedulingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for name in ('00_PROJECT.md', '01_PLAN.md', '02_SOFTWARE.md', '03_DATA.md', '04_STATUS.md'):
            (self.root / name).write_text('# fixture\n')
        (self.root / 'registry').mkdir()
        (self.root / 'registry/tasks.tsv').write_text('task_id\tresult_path\nQ01.01\tresults/Q01/Q01.01\n')
        (self.root / 'gate').write_text('approved evidence')
        spec = dict(host='H100', argv=['true'], cwd='/tmp', timeout_seconds=60,
                    resources=dict(cpus=1, memory_gb=1, gpus=1, gpu_memory_gb=2))
        self.contract = {p: copy.deepcopy(spec) for p in sd.PHASES}
        self.contract.update(gates=[dict(path='gate', sha256=sd.file_hash(self.root/'gate'))], max_attempts=2)
        self.config = {'hosts': {'H100': {'driver': ['fake'], 'limits': dict(max_jobs=4, cpus=4, memory_gb=10)}},
                       'nodes': [self.node('A'), self.node('B'), self.node('C', ['A'])]}
        self.jobs, self.launches = {}, []
        self.mock = patch.object(sd, 'driver', side_effect=self.driver)
        self.mock.start()
        self.hook = patch.object(sd.Supervisor, 'flush_events', return_value=True)
        self.hook.start()
        self.monitor=patch.object(sd.Supervisor,'sync_monitor')
        self.monitor.start()
        self.save_config()

    def tearDown(self):
        self.mock.stop(); self.hook.stop(); self.monitor.stop(); self.temp.cleanup()

    def node(self, name, deps=None):
        c = copy.deepcopy(self.contract)
        return dict(id=name, task_id='Q01.01', depends_on=deps or [],
                    result_path='results/Q01/Q01.01/' + name, contract=c,
                    approved_contract_sha256=sd.digest(c), scientific_result=False)

    def save_config(self):
        sd.atomic(self.root/'registry/supervisor.json', self.config)

    def driver(self, host, action, q):
        if action == 'resources':
            return dict(timestamp=time.time(), free_cpus=4, free_memory_gb=10,
                        gpus=[dict(id=str(i), free_gb=8, utilization=0) for i in range(2)])
        if action == 'launch':
            self.launches.append(q['job_id'])
            self.jobs[q['job_id']] = dict(state='running')
            return dict(job_id=q['job_id'])
        return self.jobs.get(q['job_id'], dict(state='not_found'))

    def supervisor(self):
        return sd.Supervisor(self.root)

    def test_parallel_and_dependencies_and_exclusive_gpus(self):
        s = self.supervisor(); s.tick()
        self.assertEqual(len(self.launches), 2)
        self.assertEqual(s.state['nodes']['C']['reason'], 'waiting_dependencies')
        self.assertNotEqual(s.state['nodes']['A']['gpu_ids'], s.state['nodes']['B']['gpu_ids'])

    def test_restart_does_not_duplicate(self):
        self.supervisor().tick(); self.supervisor().tick()
        self.assertEqual(len(self.launches), 2)

    def test_unknown_reserves_and_does_not_retry(self):
        s = self.supervisor(); s.tick(); s.tick()
        self.jobs.clear(); s.tick()
        self.assertEqual(s.state['nodes']['A']['status'], 'unknown')
        self.assertEqual(len(self.launches), 2)

    def test_uncertain_submit_reconciles_same_id(self):
        original = self.driver
        def fail_response(host, action, q):
            result = original(host, action, q)
            if action == 'launch':
                raise TimeoutError('network response lost')
            return result
        with patch.object(sd, 'driver', side_effect=fail_response):
            self.supervisor().tick()
        self.supervisor().tick()
        self.assertEqual(len(self.launches), 2)

    def test_zero_exit_does_not_release_dependency(self):
        s = self.supervisor(); s.tick()
        self.jobs[s.state['nodes']['A']['job_id']] = dict(state='succeeded')
        s.tick()
        self.assertEqual(s.state['nodes']['A']['phase'], 'validate')
        self.assertEqual(s.state['nodes']['C']['reason'], 'waiting_dependencies')

    def test_bounded_retry(self):
        s = self.supervisor(); s.tick()
        a = s.state['nodes']['A']
        self.jobs[a['job_id']] = dict(state='failed', retryable=True, reason='oom-kill')
        s.tick(); self.assertEqual(a['status'], 'needs_attention')
        self.assertEqual(a['failure_category'],'resources')
        self.assertTrue(a['repairable'])
        a['retry_after'] = 0
        before=len(self.launches)
        s.tick(); self.assertEqual(a['attempt'], 1)
        self.assertEqual(before,len(self.launches))
        a['attempt']=2
        s.fail(self.config['nodes'][0],a,'oom-kill',job_failure=True)
        self.assertFalse(a['repairable'])

    def test_input_hash_gate(self):
        (self.root/'gate').write_text('changed input')
        s = self.supervisor(); s.tick()
        self.assertEqual(self.launches, [])
        self.assertIn('input_gate_failed', s.state['nodes']['A']['reason'])

    def test_contract_not_implicitly_approved(self):
        self.config['nodes'][0]['contract']['run']['argv'] = ['changed']
        self.save_config(); s = self.supervisor(); s.tick()
        self.assertEqual(s.state['nodes']['A']['reason'], 'needs_execution_contract')

    def test_cycle_rejected(self):
        self.config['nodes'][0]['depends_on'] = ['C']; self.save_config()
        with self.assertRaisesRegex(ValueError, 'cycle'):
            sd.load_config(self.root)

    def test_unknown_dependency_rejected(self):
        self.config['nodes'][0]['depends_on'] = ['missing']; self.save_config()
        with self.assertRaisesRegex(ValueError, 'unknown dependency'):
            sd.load_config(self.root)

    def test_stale_resource_probe_blocks(self):
        original = self.driver
        def stale(host, action, q):
            result = original(host, action, q)
            if action == 'resources': result['timestamp'] = 0
            return result
        with patch.object(sd, 'driver', side_effect=stale): self.supervisor().tick()
        self.assertEqual(self.launches, [])

    def test_pause_still_reconciles(self):
        s = self.supervisor(); s.tick()
        (s.directory/'PAUSE').touch()
        self.jobs[s.state['nodes']['A']['job_id']] = dict(state='succeeded')
        s.tick()
        self.assertEqual(s.state['nodes']['A']['phase'], 'validate')
        self.assertEqual(len(self.launches), 2)

    def write_evidence(self, n, a, decision='continue'):
        d = self.root/n['result_path']; (d/'_evidence').mkdir(parents=True, exist_ok=True)
        (d/'README.md').write_text('actual fixture output')
        sd.atomic(d/'_evidence/qc.json', dict(run_id=a['run_id'], passed=True,
                  artifacts=[dict(path='README.md', sha256=sd.file_hash(d/'README.md'))]))
        r = {k: 'fixture' for k in ('expected','observed','uncertainty','reasoning','alternative_explanations',
                                   'evidence_strength','limitations','next_step_impact')}
        r.update(run_id=a['run_id'], decision=decision,
                 literature_search=dict(queries=['fixture'],searched_at='fixture',status='no_relevant_results'))
        sd.atomic(d/'_evidence/reflection.json', r)

    def complete_a(self, decision='continue'):
        s = self.supervisor(); s.tick()
        for _ in range(2):
            self.jobs[s.state['nodes']['A']['job_id']] = dict(state='succeeded'); s.tick()
        a=s.state['nodes']['A']; self.write_evidence(self.config['nodes'][0], a, decision)
        self.jobs[a['job_id']] = dict(state='succeeded'); s.tick()
        return s

    def test_complete_automatically_launches_next(self):
        s = self.complete_a()
        self.assertEqual(s.state['nodes']['A']['status'], 'complete')
        self.assertEqual(s.state['nodes']['C']['status'], 'submitting')

    def test_scientific_hold_blocks_only_branch(self):
        s=self.complete_a('needs_user')
        self.assertEqual(s.state['nodes']['A']['status'], 'needs_user')
        self.assertEqual(s.state['nodes']['C']['reason'], 'waiting_dependencies')
        self.assertEqual(s.state['nodes']['B']['status'], 'running')

    def test_missing_reflection_not_completed(self):
        s=self.supervisor(); s.tick()
        for _ in range(3):
            self.jobs[s.state['nodes']['A']['job_id']] = dict(state='succeeded'); s.tick()
        self.assertEqual(s.state['nodes']['A']['status'], 'needs_attention')

    def test_changed_artifact_rejected(self):
        n=self.config['nodes'][0]; a=dict(run_id='A.R001')
        self.write_evidence(n,a)
        (self.root/n['result_path']/'README.md').write_text('changed')
        with self.assertRaisesRegex(ValueError,'hash mismatch'): sd.verify_review(self.root,n,a)

    def test_per_node_budget_ignores_project_total_and_persists(self):
        self.setup_worker()
        self.config['progress_worker'].pop('budget_scope')
        self.save_config()
        s=self.supervisor(); s.state['worker']=dict(calls=[time.time()]*100,next_at=0)
        s.tick()
        self.assertEqual(s.state['worker']['requested'], ['A'])
        self.assertEqual(sd.budget(s.state['nodes']['A'])['worker_calls'], 1)
        restarted=self.supervisor(); restarted.tick()
        self.assertEqual(sd.budget(restarted.state['nodes']['A'])['worker_calls'], 1)
        self.assertEqual(len(restarted.state['worker']['calls']),101)

    def test_exhausted_a_does_not_block_b(self):
        self.setup_worker(); self.config['progress_worker'].pop('budget_scope')
        self.config['nodes'][1]['contract']=None; self.save_config()
        s=self.supervisor()
        s.state['nodes']['A']=dict(status='pending',attempt=0,phase='run',planner_visits=3)
        s.tick()
        self.assertEqual(s.state['worker']['requested'], ['B'])
        self.assertIn('task worker budget exhausted',s.state['nodes']['A']['reason'])

    def test_intervention_resets_only_target_and_preserves_history(self):
        s,a=self.failed_interpret()
        a['attempt']=8; sd.budget(a)['worker_calls']=3
        before=copy.deepcopy(s.state['nodes']['B'])
        old_job=a['job_id']; old_failure=copy.deepcopy(a['failure_record'])
        s.intervene(self.config,'A','user requested targeted recovery')
        self.assertEqual(a['attempt'],8)
        self.assertEqual(sd.execution_used(a),0)
        self.assertEqual(sd.budget(a)['worker_calls'],0)
        self.assertEqual(sd.budget(a)['round'],2)
        self.assertEqual(a['job_id'],old_job)
        self.assertEqual(a['failure_record'],old_failure)
        self.assertEqual(s.state['nodes']['B'],before)
        record=a['interventions'][0]
        self.assertEqual(sd.file_hash(self.root/record['path']),record['sha256'])
        item=self.repair_proposal(a)
        from recovery_policy import verify_recovery
        verify_recovery(self.root,self.config['nodes'][0],a,item)
        self.assertEqual(sd.execution_used(self.supervisor().state['nodes']['A']),0)

    def test_intervention_rejects_live_unknown_complete_and_hold(self):
        s=self.supervisor();s.tick()
        a=s.state['nodes']['A']
        for status in ('running','unknown','complete','needs_user'):
            a['status']=status
            with self.assertRaises(ValueError):s.intervene(self.config,'A','user')

    def test_intervention_requires_terminal_evidence_and_no_live_worker(self):
        s,a=self.failed_interpret()
        self.jobs[a['job_id']]=dict(state='not_found')
        with self.assertRaisesRegex(ValueError,'not confirmed'):s.intervene(self.config,'A','user')
        self.jobs[a['job_id']]=dict(state='failed')
        s.state['worker']=dict(status='unknown',requested=['A'])
        with self.assertRaisesRegex(ValueError,'worker'):s.intervene(self.config,'A','user')
        s.state['worker']['status']='complete'
        path=self.root/a['failure_record']['path']
        record=json.loads(path.read_text());record['diagnosis']['evidence']['state']='evidence_failed'
        sd.atomic(path,record);a['failure_record']['sha256']=sd.file_hash(path)
        with self.assertRaisesRegex(ValueError,'QC/scientific'):s.intervene(self.config,'A','user')

    def test_manual_grant_cannot_bypass_per_node_limit(self):
        self.setup_worker();self.config['progress_worker'].pop('budget_scope')
        self.config['progress_worker']['manual_dispatch']=dict(id='old',authority='user',node_id='A',expires_at=time.time()+60)
        self.save_config();s=self.supervisor()
        s.state['nodes']['A']=dict(status='pending',attempt=0,phase='run',planner_visits=3)
        s.tick();self.assertNotIn('requested',s.state['worker'])

    def test_three_calls_stop_only_that_task(self):
        self.setup_worker();self.config['progress_worker'].pop('budget_scope')
        self.config['progress_worker']['failure_backoff_seconds']=0
        self.save_config();s=self.supervisor()
        for count in range(1,4):
            s.tick();w=s.state['worker']
            self.assertEqual(sd.budget(s.state['nodes']['A'])['worker_calls'],count)
            self.jobs[w['job_id']]=dict(state='failed',reason='test worker error')
            s.tick()
        before=len(self.launches);s.tick()
        self.assertEqual(len(self.launches),before)
        self.assertEqual(sd.budget(s.state['nodes']['A'])['worker_calls'],3)
        self.assertIn('task worker budget exhausted',s.state['nodes']['A']['reason'])

    def test_reset_then_validated_resume_keeps_monotonic_attempt_ids(self):
        s,a=self.failed_interpret();a['attempt']=8
        s.intervene(self.config,'A','explicit user retry')
        s.tick();w=s.state['worker'];item=self.repair_proposal(a)
        sd.atomic(Path(w['request']).with_name('proposal.json'),dict(contracts=[item],blocked=[]))
        self.jobs[w['job_id']]=dict(state='succeeded');s.tick();s.tick()
        self.assertEqual(a['attempt'],9)
        self.assertEqual(sd.execution_used(a),1)
        self.assertEqual(a['status'],'submitting')

    def setup_worker(self):
        self.config['hosts']['local']=copy.deepcopy(self.config['hosts']['H100'])
        self.config['progress_worker']=dict(enabled=True,argv=['planner'],batch_size=1,max_calls_per_day=2,
                                           budget_scope='legacy_project')
        self.config['nodes'][0]['contract']=None
        self.save_config()

    def test_planner_fills_missing_contract_then_dispatches(self):
        self.setup_worker(); s=self.supervisor(); s.tick()
        w=s.state['worker']; self.assertEqual(w['status'],'submitting')
        self.jobs[w['job_id']]=dict(state='succeeded')
        sd.atomic(Path(w['request']).with_name('proposal.json'),dict(contracts=[dict(id='A',contract=self.contract)],blocked=[]))
        s.tick(); self.assertEqual(s.state['worker']['status'],'complete')
        s.tick(); self.assertEqual(s.state['nodes']['A']['status'],'submitting')

    def test_planner_unknown_never_duplicate(self):
        self.setup_worker(); s=self.supervisor(); s.tick(); s.tick()
        self.jobs.pop(s.state['worker']['job_id'])
        before=len(self.launches); s.tick(); s.tick()
        self.assertEqual(s.state['worker']['status'],'unknown')
        self.assertEqual(before,len(self.launches))

    def test_planner_cannot_edit_unrequested_node(self):
        self.setup_worker(); s=self.supervisor(); s.tick(); w=s.state['worker']
        self.jobs[w['job_id']]=dict(state='succeeded')
        sd.atomic(Path(w['request']).with_name('proposal.json'),dict(contracts=[dict(id='C',contract=self.contract)],blocked=[]))
        s.tick(); self.assertEqual(w['status'],'needs_attention')

    def test_planner_daily_budget(self):
        self.setup_worker(); s=self.supervisor()
        s.state['worker']=dict(status='failed',calls=[time.time(),time.time()],next_at=0)
        s.tick(); self.assertEqual(s.state['worker']['reason'],'daily worker call budget reached')

    def local_qc_with_planner(self, memory):
        self.setup_worker(); s=self.supervisor(); s.tick()
        self.config['hosts']['local']['limits'].update(max_jobs=2,cpus=2,memory_gb=memory)
        n=self.node('local_qc')
        for phase in sd.PHASES:
            n['contract'][phase].update(host='local',lightweight=True)
            n['contract'][phase]['resources'].update(gpus=0,gpu_memory_gb=0)
        n['approved_contract_sha256']=sd.digest(n['contract'])
        self.config['nodes'].append(n);self.save_config();s.tick()
        return s

    def test_local_qc_coexists_with_reserved_planner(self):
        s=self.local_qc_with_planner(3)
        self.assertEqual(s.state['nodes']['local_qc']['status'],'submitting')
        self.assertEqual(s.state['worker']['status'],'running')

    def test_local_qc_waits_when_planner_uses_memory_budget(self):
        s=self.local_qc_with_planner(2)
        self.assertEqual(s.state['nodes']['local_qc']['reason'],'waiting_resources')
        self.assertEqual(s.state['nodes']['local_qc']['attempt'],0)

    def failed_interpret(self):
        s=self.supervisor();s.tick()
        for _ in range(2):
            self.jobs[s.state['nodes']['A']['job_id']]=dict(state='succeeded');s.tick()
        a=s.state['nodes']['A'];self.assertEqual(a['phase'],'interpret')
        d=self.root/self.config['nodes'][0]['result_path'];d.mkdir(parents=True,exist_ok=True)
        (d/'model_output.txt').write_text('immutable completed computation')
        self.jobs[a['job_id']]=dict(state='failed',reason='JSONDecodeError: Extra data',
                                  log_tail='Traceback\nJSONDecodeError: Extra data')
        s.tick();a['retry_after']=0
        self.config['hosts']['local']=copy.deepcopy(self.config['hosts']['H100'])
        self.config['progress_worker']=dict(enabled=True,argv=['repair-worker'],max_calls_per_day=12,
                                            repair_reserved_calls=3,cooldown_seconds=0)
        self.save_config()
        return s,a

    def repair_proposal(self, a):
        n=self.config['nodes'][0]; d=self.root/n['result_path']
        code=d/'repair.py'
        code.write_text('import sys\nsys.path.insert(0,'+repr(str(Path(sd.__file__).parent))+')\n'
                        'from structured_output import decode_object\n'
                        'assert decode_object(\'{"value":1} }\', True)[0]["value"] == 1\nprint("PASS")\n')
        p=subprocess.run([sys.executable,'-B',str(code)],capture_output=True,text=True)
        log=d/'test.log';log.write_text(p.stdout+p.stderr)
        record=lambda p:dict(path=str(p.relative_to(self.root)),sha256=sd.file_hash(p))
        v=d/'validation.json'
        sd.atomic(v,dict(passed=p.returncode==0,exit_code=p.returncode,command=[sys.executable,'-B',str(code)],
                         log=record(log),tested_gates=[record(code)]))
        new=copy.deepcopy(n['contract']);new['interpret']['argv']=[sys.executable,'-B',str(code)]
        new['gates'].append(record(code))
        return dict(id='A',contract=new,recovery=dict(failure_record_sha256=a['failure_record']['sha256'],
               diagnosis='Extra closing brace in executed worker JSON output',
               action='Use narrow strict parser repair and verify no other trailing data accepted',
               resume_phase='interpret',validation=record(v),preserved_artifacts=[record(d/'model_output.txt')],
               reuse_justification='Only report decoding failed; prior model outputs unchanged'))

    def test_fault_injection_repair_resumes_phase_and_releases_successor(self):
        s,a=self.failed_interpret();old_job=a['job_id'];old_run=a['run_id']
        self.assertEqual(a['failure_category'],'serialization')
        failure=json.loads((self.root/a['failure_record']['path']).read_text())
        self.assertEqual(failure['phase'],'interpret')
        s.tick();w=s.state['worker'];self.assertEqual(w['purpose'],'repair')
        item=self.repair_proposal(a)
        sd.atomic(Path(w['request']).with_name('proposal.json'),dict(contracts=[item],blocked=[]))
        self.jobs[w['job_id']]=dict(state='succeeded');s.tick()
        self.assertEqual(a['phase'],'interpret');self.assertTrue(a['resume_pending'])
        s.tick();self.assertEqual(a['attempt'],2);self.assertEqual(a['run_id'],old_run)
        self.assertNotEqual(a['job_id'],old_job)
        self.assertEqual(a['spec']['argv'],item['contract']['interpret']['argv'])
        before=len(self.launches);s=self.supervisor();s.tick();self.assertEqual(before,len(self.launches))
        a=s.state['nodes']['A'];self.write_evidence(self.config['nodes'][0],a)
        self.jobs[a['job_id']]=dict(state='succeeded');s.tick()
        self.assertEqual(a['status'],'complete');self.assertEqual(s.state['nodes']['C']['status'],'submitting')
        self.assertEqual((self.root/self.config['nodes'][0]['result_path']/'model_output.txt').read_text(),
                         'immutable completed computation')

    def test_repair_without_minimal_validation_is_rejected(self):
        s,a=self.failed_interpret();s.tick();w=s.state['worker'];item=self.repair_proposal(a)
        del item['recovery']['validation']
        sd.atomic(Path(w['request']).with_name('proposal.json'),dict(contracts=[item],blocked=[]))
        self.jobs[w['job_id']]=dict(state='succeeded');s.tick()
        self.assertEqual(w['status'],'needs_attention');self.assertEqual(a['attempt'],1)

    def test_failed_minimal_test_is_rejected_even_with_fresh_hash(self):
        from recovery_policy import verify_recovery
        s,a=self.failed_interpret();item=self.repair_proposal(a)
        p=self.root/item['recovery']['validation']['path'];v=json.loads(p.read_text())
        v.update(passed=False,exit_code=1);sd.atomic(p,v)
        item['recovery']['validation']['sha256']=sd.file_hash(p)
        with self.assertRaisesRegex(ValueError,'did not pass'):
            verify_recovery(self.root,self.config['nodes'][0],a,item)

    def test_repair_rejects_full_reset_or_changed_reused_output(self):
        from recovery_policy import verify_recovery
        s,a=self.failed_interpret();item=self.repair_proposal(a);n=self.config['nodes'][0]
        item['recovery']['resume_phase']='run'
        with self.assertRaisesRegex(ValueError,'failed phase'):verify_recovery(self.root,n,a,item)
        item['recovery']['resume_phase']='interpret'
        (self.root/n['result_path']/'model_output.txt').write_text('corrupted')
        with self.assertRaisesRegex(ValueError,'hash mismatch'):verify_recovery(self.root,n,a,item)

    def test_repair_rejects_scientific_gate_change_and_budget_increase(self):
        from recovery_policy import verify_recovery
        s,a=self.failed_interpret();item=self.repair_proposal(a);n=self.config['nodes'][0]
        item['contract']['max_attempts']=99
        with self.assertRaisesRegex(ValueError,'budget'):verify_recovery(self.root,n,a,item)
        item['contract']['max_attempts']=2
        (self.root/'gate').write_text('changed endpoint')
        item['contract']['gates'][0]['sha256']=sd.file_hash(self.root/'gate')
        with self.assertRaisesRegex(ValueError,'non-code'):verify_recovery(self.root,n,a,item)

    def test_repairs_have_priority_over_unvisited_planning(self):
        s,a=self.failed_interpret();a['planner_visits']=99
        self.config['nodes'][1]['contract']=None;s.state['nodes']['B'].update(status='pending',attempt=0)
        self.save_config();s.tick()
        self.assertEqual(s.state['worker']['requested'],['A'])

    def test_planning_cannot_spend_reserved_repair_budget(self):
        self.setup_worker();self.config['progress_worker'].update(max_calls_per_day=12,repair_reserved_calls=3)
        self.save_config();s=self.supervisor();s.state['worker']=dict(status='complete',calls=[time.time()]*9,next_at=0)
        s.tick();self.assertIn('reserved for repair',s.state['worker']['reason'])

    def test_repair_can_use_reserved_calls(self):
        s,a=self.failed_interpret();s.state['worker']=dict(status='complete',calls=[time.time()]*9,next_at=0)
        s.tick();self.assertEqual(s.state['worker']['purpose'],'repair')

    def test_manual_dispatch_is_one_use_without_resetting_budget(self):
        self.setup_worker();self.config['progress_worker']['manual_dispatch']=dict(id='explicit-once',node_id='A',
                authority='fixture explicit user request',expires_at=time.time()+60)
        self.save_config();s=self.supervisor();s.state['worker']=dict(status='complete',calls=[time.time()]*2,next_at=0)
        s.tick();self.assertEqual(len(s.state['worker']['calls']),3)
        self.assertEqual(s.state['worker']['consumed_dispatches'],['explicit-once'])
        self.jobs[s.state['worker']['job_id']]=dict(state='failed');s.tick()
        s.state['worker']['next_at']=0;s.tick()
        self.assertEqual(s.state['worker']['reason'],'daily worker call budget reached')

    def test_worker_failure_diagnosis_survives_into_next_request(self):
        self.setup_worker();self.config['progress_worker'].update(max_calls_per_day=12)
        self.save_config();s=self.supervisor();s.tick();w=s.state['worker']
        self.jobs[w['job_id']]=dict(state='failed',reason='JSONDecodeError: Extra data')
        s.tick();record=s.state['nodes']['A']['worker_failure_record']
        self.assertTrue((self.root/record['path']).exists())
        w['next_at']=0;s.tick()
        request=json.loads(Path(w['request']).read_text())
        self.assertEqual(request['state']['A']['worker_failure_record'],record)
        self.assertEqual(w['purpose'],'repair')


if __name__ == '__main__':
    unittest.main()

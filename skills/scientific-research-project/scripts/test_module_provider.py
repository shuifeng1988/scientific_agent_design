"""Isolated routing/compatibility tests; no external Skill, model or real research."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import module_provider as mp
import research_workflow as rw
from test_research_workflow import build_project, fixture_review


class ProviderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def config(self, capability='evidence', host='claude', kind='subagent'):
        cfg = dict(schema_version=1, contract_version=mp.CONTRACT,
                   bindings={capability: 'fixture-provider'}, providers={
                       'fixture-provider': dict(kind=kind, version='fixture-1',
                           entrypoint='fixture-method', hosts=[host],
                           instructions='SYNTHETIC test provider only; retain the project contract.')})
        rw.atomic(self.root / mp.CONFIG, cfg)
        return cfg

    def handoff(self, capability='review', task_id=None):
        subject = None
        if capability == 'review':
            source = self.root / 'review_input.txt'; source.write_text('SYNTHETIC subject')
            subject = dict(stage='design', plan_version='fixture', author_invocation_id='fixture-author',
                           targets=[rw.descriptor(source, self.root)])
        req = mp.prepare(self.root, capability, 'codex', 'SYNTHETIC fixture objective', task_id,
                         run_id='R1', review_subject=subject)
        obj = mp.read_object(req)
        artifact = req.with_name('review.md')
        artifact.write_text('SYNTHETIC review fixture; no scientific validation.')
        output = dict(request_id=obj['request_id'], request_sha256=rw.sha(req),
                      provider_id=obj['route']['provider']['id'], status='ready_for_review',
                      summary='Fixture only', artifacts=[rw.descriptor(artifact, self.root)])
        if subject:
            review = req.with_name('scientific_review.json'); fixture_review(self.root, subject, review)
            output['artifacts'].append(rw.descriptor(review, self.root))
        path = req.with_name('output.json'); rw.atomic(path, output)
        return req, path, output

    def test_builtins_portable_and_core_only_package_is_self_contained(self):
        for host in ('codex', 'claude', 'another-host'):
            for capability in mp.catalog():
                route = mp.resolve(self.root, capability, host)
                self.assertEqual(route['provider']['id'], 'builtin.' + capability)
                self.assertTrue(all(Path(r['path']).is_file() for r in route['required_reads']))
        self.assertEqual(list(self.root.iterdir()), [])  # resolve is read-only

    def test_replacing_one_method_preserves_other_routes_and_contracts(self):
        original = mp.resolve(self.root, 'evidence', 'claude')
        execution = mp.resolve(self.root, 'execution', 'claude')
        self.config()
        route = mp.resolve(self.root, 'evidence', 'claude')
        self.assertEqual(route['provider']['kind'], 'subagent')
        self.assertEqual(route['output_contract'], original['output_contract'])
        self.assertEqual(route['required_reads'][:len(original['required_reads'])], original['required_reads'])
        self.assertEqual(mp.resolve(self.root, 'execution', 'claude')['provider'], execution['provider'])
        with self.assertRaisesRegex(ValueError, 'unavailable'):
            mp.resolve(self.root, 'evidence', 'codex')

    def test_bad_config_cannot_downgrade_or_silently_fallback(self):
        cfg = self.config()
        variants = []
        for key, value in [('contract_version', 'weaker-v0'), ('bindings', {'evidence': 'missing'}),
                           ('bindings', {'unknown-capability': 'fixture-provider'})]:
            c = copy.deepcopy(cfg); c[key] = value; variants.append(c)
        c = copy.deepcopy(cfg); c['providers']['fixture-provider']['entrypoint'] = 'scientific-evidence'; variants.append(c)
        c = copy.deepcopy(cfg); c['providers']['fixture-provider']['waive_qc'] = True; variants.append(c)
        for c in variants:
            rw.atomic(self.root / mp.CONFIG, c)
            with self.subTest(config=c), self.assertRaises(ValueError):
                mp.resolve(self.root, 'evidence', 'claude')

    def test_handoff_cannot_complete_or_publish_or_mutate_roots(self):
        build_project(self.root)
        baseline = {p: (self.root / p).read_bytes() for p in rw.ROOT_DOCS}
        req, out, value = self.handoff(task_id='Q01.01')
        self.assertTrue(req.is_relative_to(self.root / 'results/Q01/Q01.01/_evidence/providers'))
        result = mp.check_output(self.root, req, out)
        self.assertFalse(result['task_complete']); self.assertFalse(result['publication_authorized'])
        self.assertEqual(baseline, {p: (self.root / p).read_bytes() for p in rw.ROOT_DOCS})
        value['status'] = 'complete'; rw.atomic(out, value)
        with self.assertRaisesRegex(ValueError, 'cannot approve/complete'):
            mp.check_output(self.root, req, out)

    def test_changed_evidence_or_foreign_task_output_is_rejected(self):
        req, out, value = self.handoff()
        req.with_name('review.md').write_text('tampered')
        with self.assertRaises(ValueError): mp.check_output(self.root, req, out)
        foreign = self.root / 'other-result.md'; foreign.write_text('outside assigned path')
        value['artifacts'] = [rw.descriptor(foreign, self.root)]; rw.atomic(out, value)
        with self.assertRaisesRegex(ValueError, 'outside assigned'):
            mp.check_output(self.root, req, out)

    def test_wrong_identity_and_provider_changes_rejected(self):
        req, out, value = self.handoff()
        value['provider_id'] = 'someone-else'; rw.atomic(out, value)
        with self.assertRaisesRegex(ValueError, 'wrong provider'):
            mp.check_output(self.root, req, out)
        value['provider_id'] = 'builtin.review'; rw.atomic(out, value)
        self.config('review', 'codex', 'skill')
        with self.assertRaisesRegex(ValueError, 'provider or contract changed'):
            mp.check_output(self.root, req, out)

    def test_plan_drift_rejected_but_unrelated_status_progress_allowed(self):
        build_project(self.root)
        req, out, value = self.handoff(task_id='Q01.01')
        rw.atomic(self.root / '04_STATUS.md', 'new real runtime progress would be allowed')
        self.assertTrue(mp.check_output(self.root, req, out)['handoff_valid'])
        rw.atomic(self.root / '01_PLAN.md', 'changed scientific plan')
        with self.assertRaises(ValueError): mp.check_output(self.root, req, out)

    def test_unrelated_provider_replacement_does_not_block_this_handoff(self):
        req, out, value = self.handoff('review')
        self.config('evidence', 'claude', 'subagent')
        self.assertTrue(mp.check_output(self.root, req, out)['handoff_valid'])

    def test_evidence_provider_must_satisfy_existing_appraisal_gate(self):
        build_project(self.root)
        req, out, value = self.handoff('evidence')
        with self.assertRaisesRegex(ValueError, 'appraisal.json'):
            mp.check_output(self.root, req, out)
        appraisal = rw.read(self.root / 'provenance/appraisal.json')
        appraisal['status'] = 'ready_for_design_review'
        artifact = req.with_name('appraisal.json'); rw.atomic(artifact, appraisal)
        value['artifacts'].append(rw.descriptor(artifact, self.root)); rw.atomic(out, value)
        self.assertTrue(mp.check_output(self.root, req, out)['handoff_valid'])
        appraisal['searches'] = appraisal['searches'][:1]; rw.atomic(artifact, appraisal)
        value['artifacts'][-1] = rw.descriptor(artifact, self.root); rw.atomic(out, value)
        with self.assertRaisesRegex(ValueError, 'two search routes'):
            mp.check_output(self.root, req, out)

    def test_missing_consent_can_return_needs_user_without_fabricated_artifacts(self):
        req, out, value = self.handoff('intake')
        value.update(status='needs_user', artifacts=[], summary='What is the actual focal question?')
        rw.atomic(out, value)
        self.assertEqual(mp.check_output(self.root, req, out)['status'], 'needs_user')
        self.assertFalse((self.root / '00_PROJECT.md').exists())

    def test_execution_requires_registered_task_and_normalized_proposal(self):
        with self.assertRaisesRegex(ValueError, 'registered task'):
            mp.prepare(self.root, 'execution', 'codex', 'fixture')
        build_project(self.root)
        req, out, value = self.handoff('execution', 'Q01.01')
        artifact = req.with_name('proposal.json'); rw.atomic(artifact, {'contracts': [], 'blocked': []})
        value['artifacts'] = [rw.descriptor(artifact, self.root)]; rw.atomic(out, value)
        result = mp.check_output(self.root, req, out)
        self.assertFalse(result['task_complete'])
        rw.atomic(artifact, {'approved': True})
        value['artifacts'] = [rw.descriptor(artifact, self.root)]; rw.atomic(out, value)
        with self.assertRaises(ValueError): mp.check_output(self.root, req, out)

    def test_input_drift_expiry_and_output_limits_are_enforced(self):
        source = self.root / 'data.tsv'; source.write_text('original input')
        req, out, value = self.handoff('review')
        r = mp.read_object(req); r['inputs'] = [rw.descriptor(source, self.root)]
        def save():
            rw.atomic(req, r); value['request_sha256'] = rw.sha(req); rw.atomic(out, value)
        save(); source.write_text('changed')
        with self.assertRaises(ValueError): mp.check_output(self.root, req, out)
        r['inputs'] = []; r['created_at'] = 0; save()
        with self.assertRaisesRegex(ValueError, 'expired'): mp.check_output(self.root, req, out)
        import time
        r['created_at'] = time.time(); r['limits']['max_output_bytes'] = 1; save()
        with self.assertRaisesRegex(ValueError, 'byte limit'): mp.check_output(self.root, req, out)

    def test_local_provider_source_change_invalidates_selection(self):
        cfg = self.config(); entry = self.root / 'external_SKILL.md'; entry.write_text('version one')
        cfg['providers']['fixture-provider']['entrypoint'] = str(entry)
        rw.atomic(self.root / mp.CONFIG, cfg)
        before = mp.resolve(self.root, 'evidence', 'claude')
        entry.write_text('changed instructions')
        self.assertFalse(mp.same_selection(before, mp.resolve(self.root, 'evidence', 'claude')))
        entry.unlink()
        with self.assertRaisesRegex(ValueError, 'unavailable'): mp.resolve(self.root, 'evidence', 'claude')

    def test_normalized_stage_payload_and_run_required(self):
        build_project(self.root)
        with self.assertRaisesRegex(ValueError, 'run_id'): mp.prepare(self.root, 'interpretation', 'codex', 'fixture', 'Q01.01')
        for capability, name in [('design','design_proposal.json'),('interpretation','reflection.json'),
                                 ('reporting','report.json')]:
            req, out, value = self.handoff(capability, 'Q01.01')
            with self.assertRaisesRegex(ValueError, name): mp.check_output(self.root, req, out)
            path = req.with_name(name); rw.atomic(path, {})
            value['artifacts'] = [rw.descriptor(path, self.root)]; rw.atomic(out, value)
            with self.assertRaises((ValueError, KeyError)): mp.check_output(self.root, req, out)

    def test_cli_resolves_external_provider_without_invoking_it(self):
        self.config()
        before = set(self.root.rglob('*'))
        run = subprocess.run([sys.executable, '-B', str(Path(mp.__file__)), 'resolve',
                              '--root', str(self.root), '--capability', 'evidence', '--host', 'claude'],
                             text=True, capture_output=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout)['provider']['id'], 'fixture-provider')
        self.assertEqual(before, set(self.root.rglob('*')))

    def test_worker_routes_repair_and_preserves_legacy_proposal_interface(self):
        self.config('recovery', 'codex', 'skill')
        req = self.root / 'request.json'
        rw.atomic(req, {'nodes': [{'id': 'A'}], 'state': {'A': {'repairable': True}}})
        fake = self.root / 'fixture_codex.py'
        fake.write_text('#!' + sys.executable + '\nimport sys,pathlib\n'
                        'pathlib.Path(sys.argv[sys.argv.index("--output-last-message")+1]).write_text('
                        '\'{"contracts":[],"blocked":[{"id":"A","reason":"fixture unavailable",'
                        '"needs_user":false}]}\')\n')
        fake.chmod(0o700)
        run = subprocess.run([sys.executable, '-B', str(Path(mp.__file__).with_name('progress_worker.py')),
                              '--root', str(self.root), '--request', str(req), '--codex', str(fake)],
                             text=True, capture_output=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        selected = json.loads((self.root / 'worker_providers.json').read_text())
        self.assertEqual([r['capability'] for r in selected], ['recovery'])
        self.assertEqual(selected[0]['provider']['id'], 'fixture-provider')
        self.assertEqual(mp.read_object(self.root / 'proposal.json')['blocked'][0]['id'], 'A')

    def test_worker_rejects_provider_change_while_model_is_running(self):
        self.config('execution', 'codex', 'skill')
        req = self.root / 'request.json'; rw.atomic(req, {'nodes': [], 'state': {}})
        fake = self.root / 'fixture_codex.py'
        fake.write_text('#!' + sys.executable + '\nimport sys,pathlib,json\n'
            'root=pathlib.Path(sys.argv[sys.argv.index("-C")+1])\n'
            'p=root/"registry/providers.json"\n'
            'c=json.loads(p.read_text());c["providers"]["fixture-provider"]["version"]="changed"\n'
            'p.write_text(json.dumps(c))\n'
            'pathlib.Path(sys.argv[sys.argv.index("--output-last-message")+1]).write_text('
            '\'{"contracts":[],"blocked":[]}\')\n')
        fake.chmod(0o700)
        run = subprocess.run([sys.executable, '-B', str(Path(mp.__file__).with_name('progress_worker.py')),
                              '--root', str(self.root), '--request', str(req), '--codex', str(fake)],
                             text=True, capture_output=True)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn('changed during worker', run.stderr)
        self.assertTrue((self.root / 'proposal.raw.txt').is_file())
        self.assertFalse((self.root / 'proposal.json').exists())


if __name__ == '__main__':
    unittest.main()

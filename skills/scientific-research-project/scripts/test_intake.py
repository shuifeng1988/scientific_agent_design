"""Read-only intake guards; these do not certify online conversational quality."""
import tempfile
import unittest
from pathlib import Path

import supervisor_agent as sa
import research_workflow as rw
from test_research_workflow import build_project


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_empty_project_requires_dialogue_without_creating_files(self):
        out = sa.intake(self.root)
        self.assertFalse(out['interpretation_ready'])
        self.assertTrue(out['high_impact_questions'])
        self.assertEqual(list(self.root.iterdir()), [])

    def test_keyword_complete_template_is_not_consent(self):
        rw.atomic(self.root / '00_PROJECT.md',
                  'objective scientific question scope metric eligible deliverable hypothesis stopping')
        out = sa.intake(self.root)
        self.assertTrue(all(out['signals'].values()))
        self.assertFalse(out['interpretation_ready'])
        self.assertTrue(sa.choose_next(self.root)['needs_user_intake'])

    def test_frozen_words_do_not_bypass_dialogue(self):
        rw.atomic(self.root / '01_PLAN.md', 'PLAN-v1 Q00.01 frozen')
        self.assertFalse(sa.intake(self.root)['design_already_frozen'])

    def test_verified_existing_design_does_not_repeat_intake(self):
        build_project(self.root)
        out = sa.intake(self.root)
        self.assertTrue(out['interpretation_ready'])
        self.assertEqual(out['high_impact_questions'], [])

    def test_changed_design_cannot_appear_ready(self):
        build_project(self.root)
        rw.atomic(self.root / '00_PROJECT.md', 'Changed scientific question')
        out = sa.intake(self.root)
        self.assertFalse(out['interpretation_ready'])
        self.assertTrue(out['design_validation_error'])


if __name__ == '__main__':
    unittest.main()

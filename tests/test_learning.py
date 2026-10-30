"""Personal apprenticeship intent, grounded notes, and finite verbal attention."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sim'))
import learning
import skills


class TestLearning(unittest.TestCase):
    def setUp(self):
        self.p = {'id': 1, 'skills': {}}
        learning.migrate_person(self.p)

    def note(self, teacher=2, tech='fishing', day=10):
        learning.remember_work(self.p, teacher, tech, 8, 9, day)
        return self.p['experience']['mentors'][-1]

    def test_only_observed_method_is_recorded_without_granting_skill(self):
        self.note()
        self.assertEqual([n['tech'] for n in self.p['experience']['mentors']], ['fishing'])
        self.assertFalse(skills.knows(self.p, 'fishing'))
        self.assertFalse(skills.knows(self.p, 'stone_tools'))
        self.assertEqual(self.p['experience']['mentors'][0]['retry_day'], -1)

    def test_missing_prerequisite_does_not_block_seeking_observed_work(self):
        self.note()
        self.assertEqual(len(learning.candidate_notes(self.p, 10)), 1)
        self.assertEqual(learning.missing_step(self.p, 'fishing'), 'stone_tools')
        skills.expose(self.p, 'stone_tools', 10)
        self.assertEqual(learning.missing_step(self.p, 'fishing'), 'fishing')
        skills.expose(self.p, 'fishing', 10)
        self.assertIsNone(learning.missing_step(self.p, 'fishing'))
        self.assertEqual(learning.candidate_notes(self.p, 10), [])

    def test_seen_person_moves_only_existing_notes_without_refreshing_demonstration(self):
        self.note()
        learning.seen_person(self.p, 2, 20, 21, 39)
        n = self.p['experience']['mentors'][0]
        self.assertEqual((n['x'], n['y'], n['seen_day'], n['demonstrated_day']), (20, 21, 39, 10))
        self.assertEqual(len(learning.candidate_notes(self.p, 69)), 1)
        self.assertEqual(learning.candidate_notes(self.p, 70), [])
        learning.seen_person(self.p, 99, 1, 1, 40)
        self.assertEqual(len(self.p['experience']['mentors']), 1)

    def test_notes_are_bounded_and_upsert_preserves_distinct_teachers_methods(self):
        for teacher in range(2, 15):
            self.note(teacher=teacher, day=teacher)
        self.assertEqual(len(self.p['experience']['mentors']), 12)
        self.assertNotIn(2, [n['teacher'] for n in self.p['experience']['mentors']])
        learning.remember_work(self.p, 14, 'fishing', 30, 31, 20)
        self.assertEqual(len(self.p['experience']['mentors']), 12)
        self.assertEqual(self.p['experience']['mentors'][-1]['x'], 30)
        self.note(teacher=14, tech='fire', day=21)
        self.assertEqual(sum(n['teacher'] == 14 for n in self.p['experience']['mentors']), 2)

    def test_candidate_copies_cannot_mutate_personal_memory(self):
        self.note()
        candidates = learning.candidate_notes(self.p, 10)
        candidates[0]['x'] = 999
        candidates.clear()
        self.assertEqual(self.p['experience']['mentors'][0]['x'], 8)

    def test_intent_is_bounded_and_failure_cools_only_its_note(self):
        self.note()
        note = learning.candidate_notes(self.p, 10)[0]
        self.assertTrue(learning.start(self.p, note, 40))
        note['x'] = 999
        self.assertEqual(self.p['learning'], {'teacher': 2, 'tech': 'fishing', 'x': 8, 'y': 9,
                                             'started_part': 40, 'until_part': 48})
        learning.fail(self.p, 11)
        self.assertIsNone(self.p['learning'])
        self.assertEqual(learning.candidate_notes(self.p, 17), [])
        self.assertEqual(len(learning.candidate_notes(self.p, 18)), 1)
        learning.remember_work(self.p, 2, 'fishing', 9, 9, 12)
        self.assertEqual(learning.candidate_notes(self.p, 17), [])

    def test_interruption_is_not_a_failed_lesson(self):
        self.note()
        learning.start(self.p, learning.candidate_notes(self.p, 10)[0], 1)
        learning.interrupt(self.p)
        self.assertIsNone(self.p['learning'])
        self.assertEqual(self.p['experience']['mentors'][0]['retry_day'], -1)

    def test_verbal_budget_combines_unique_requested_and_incidental_learners(self):
        teacher = {'id': 2}
        for pid in range(10, 14):
            self.assertTrue(learning.can_instruct(teacher, pid, 20))
            self.assertTrue(learning.record_instruction(teacher, pid, 20))
        self.assertFalse(learning.can_instruct(teacher, 14, 20))
        self.assertFalse(learning.record_instruction(teacher, 14, 20))
        self.assertTrue(learning.record_instruction(teacher, 10, 20))
        self.assertEqual(teacher['teaching_ids'], [10, 11, 12, 13])
        self.assertTrue(learning.can_instruct(teacher, 14, 21))
        self.assertTrue(learning.record_instruction(teacher, 14, 21))
        self.assertEqual(teacher['teaching_ids'], [14])
        self.assertFalse(learning.can_instruct(teacher, 2, 21))

    def test_migration_preserves_skills_existing_memory_and_detached_defaults(self):
        old = {'id': 3, 'skills': {'fire': {'level': 1.}}, 'experience': {'sites': [{'kind': 'plants'}]}}
        learning.migrate_person(old)
        learning.migrate_person(old)
        learning.migrate_person(self.p)
        self.assertEqual(old['skills'], {'fire': {'level': 1.}})
        self.assertEqual(old['experience']['sites'], [{'kind': 'plants'}])
        self.assertEqual(json.loads(json.dumps(old)), old)
        self.assertIsNot(old['teaching_ids'], self.p['teaching_ids'])
        self.assertIsNot(old['experience']['mentors'], self.p['experience']['mentors'])
        self.assertEqual(old['experience']['mentors'], [])
        self.assertIsNone(old['learning'])
        self.assertIsNone(old['teaching'])
        self.assertIsNone(old['teaching_day'])

    def test_unknown_method_and_self_are_rejected_without_pollution(self):
        self.assertFalse(learning.remember_work(self.p, 2, 'telepathy', 1, 1, 0))
        self.assertFalse(learning.remember_work(self.p, 1, 'fire', 1, 1, 0))
        self.assertIsNone(learning.missing_step(self.p, 'telepathy'))
        self.assertFalse(learning.start(self.p, {'teacher': 2, 'tech': 'telepathy', 'x': 1, 'y': 1}, 0))
        self.assertEqual(self.p['experience']['mentors'], [])

    def test_multilevel_missing_step_uses_awareness_not_mastery(self):
        self.assertEqual(learning.missing_step(self.p, 'granary'), 'fire')
        skills.expose(self.p, 'fire', 0)
        self.assertFalse(skills.qualified(self.p, 'fire'))
        self.assertEqual(learning.missing_step(self.p, 'granary'), 'preservation')
        skills.expose(self.p, 'preservation', 1)
        self.assertEqual(learning.missing_step(self.p, 'granary'), 'agriculture')

    def test_failure_leaves_other_mentors_and_durable_skill_untouched(self):
        skills.invent(self.p, 'fire', 0)
        self.note(teacher=2)
        self.note(teacher=3)
        learning.start(self.p, learning.candidate_notes(self.p, 10)[0], 40)
        learning.fail(self.p, 10)
        self.assertEqual(self.p['experience']['mentors'][1]['retry_day'], -1)
        self.assertTrue(skills.qualified(self.p, 'fire'))
        self.assertEqual([n['teacher'] for n in learning.candidate_notes(self.p, 10)], [3])

    def test_capacity_probe_does_not_spend_or_reset_attention(self):
        teacher = {'id': 2, 'teaching_day': 10, 'teaching_ids': [3, 4, 5, 6]}
        before = json.loads(json.dumps(teacher))
        self.assertTrue(learning.can_instruct(teacher, 7, 11))
        self.assertEqual(teacher, before)

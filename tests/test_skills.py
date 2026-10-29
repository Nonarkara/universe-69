"""Personal competence, provenance and explicit legacy capability priors."""
import copy
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sim'))
import skills


class TestSkills(unittest.TestCase):
    def person(self, uid=7):
        return {'id': uid, 'b': -18 * 360}

    def test_registry_has_the_existing_fourteen_prerequisite_rows(self):
        rows = skills.TECH_LADDER
        self.assertEqual(len(rows), 14)
        self.assertEqual(len({row[0] for row in rows}), 14)
        names = set()
        for name, parent, chance, population in rows:
            self.assertTrue(parent is None or parent in names)
            self.assertGreater(chance, 0)
            self.assertGreater(population, 0)
            names.add(name)
        self.assertEqual(rows[2], ('fishing', 'stone_tools', .35, 6))

    def test_queries_are_read_only_and_missing_knowledge_is_not_global(self):
        p = self.person()
        p['tech'] = [row[0] for row in skills.TECH_LADDER]
        before = copy.deepcopy(p)
        for name in ('fire', 'fishing', 'unknown'):
            self.assertEqual(skills.level(p, name), 0.)
            self.assertFalse(skills.knows(p, name))
            self.assertFalse(skills.qualified(p, name))
            self.assertFalse(skills.can_teach(p, name))
        self.assertEqual(p, before)

    def test_levels_are_bounded(self):
        p = self.person()
        p['skills'] = {'fire': {'level': 4.}, 'stone_tools': {'level': -.5}}
        self.assertEqual(skills.level(p, 'fire'), 1.)
        self.assertEqual(skills.level(p, 'stone_tools'), 0.)

    def test_awareness_requires_the_entire_personal_prerequisite_chain(self):
        p = self.person()
        p['skills'] = {t: {'level': .25} for t in ('predator_hunt', 'fishing')}
        self.assertFalse(skills.knows(p, 'predator_hunt'))
        self.assertTrue(skills.expose(p, 'stone_tools', 0))
        self.assertTrue(skills.knows(p, 'predator_hunt'))
        self.assertFalse(skills.qualified(p, 'predator_hunt'))

    def test_qualification_requires_fully_competent_ancestors(self):
        p = self.person()
        p['skills'] = {'stone_tools': {'level': .25}, 'fishing': {'level': 1.}}
        self.assertTrue(skills.knows(p, 'fishing'))
        self.assertFalse(skills.qualified(p, 'fishing'))
        self.assertFalse(skills.can_teach(p, 'fishing'))
        self.assertTrue(skills.invent(p, 'stone_tools', 1))
        self.assertTrue(skills.qualified(p, 'fishing'))

    def test_qualification_checks_grandparents_not_only_the_immediate_parent(self):
        p = self.person()
        p['skills'] = {name: {'level': 1.} for name in ('fire', 'shelter', 'lore')}
        p['skills']['fire']['level'] = .25
        self.assertTrue(skills.knows(p, 'lore'))
        self.assertFalse(skills.qualified(p, 'lore'))
        self.assertFalse(skills.invent(p, 'writing', 1))

    def test_instruction_records_provenance_but_is_not_mastery(self):
        p = self.person()
        self.assertTrue(skills.expose(p, 'fire', 10, teacher=3, origin=2))
        self.assertEqual(p['skills']['fire'], {
            'level': .25, 'learned_day': 10, 'teacher': 3, 'origin': 2,
            'basis': 'instruction', 'practice_day': None, 'uses': 0})
        self.assertTrue(skills.knows(p, 'fire'))
        self.assertFalse(skills.qualified(p, 'fire'))
        self.assertFalse(skills.can_teach(p, 'fire'))

    def test_repeated_chatter_does_not_refresh_or_amplify_instruction(self):
        p = self.person()
        skills.expose(p, 'fire', 2, teacher=3, origin=1)
        before = copy.deepcopy(p)
        for day in (2, 3, 1000):
            self.assertFalse(skills.expose(p, 'fire', day, teacher=99, origin=98))
        self.assertEqual(p, before)

    def test_practice_preserves_the_instruction_source(self):
        p = self.person()
        skills.expose(p, 'fire', 2, teacher=3, origin=1, basis='demonstration')
        skills.practice(p, 'fire', 3)
        entry = p['skills']['fire']
        self.assertEqual((entry['teacher'], entry['origin'], entry['basis'], entry['learned_day']),
                         (3, 1, 'demonstration', 2))

    def test_instruction_can_build_awareness_but_not_skip_prerequisites(self):
        p = self.person()
        self.assertFalse(skills.expose(p, 'fishing', 0))
        self.assertNotIn('skills', p)
        self.assertTrue(skills.expose(p, 'stone_tools', 0))
        self.assertTrue(skills.expose(p, 'fishing', 1))
        self.assertTrue(skills.knows(p, 'fishing'))
        self.assertFalse(skills.qualified(p, 'fishing'))

    def test_invention_needs_qualified_personal_prerequisites(self):
        p = self.person()
        p['tech'] = ['stone_tools']
        self.assertFalse(skills.invent(p, 'fishing', 0))
        skills.expose(p, 'stone_tools', 0)
        self.assertFalse(skills.invent(p, 'fishing', 1))
        self.assertTrue(skills.invent(p, 'stone_tools', 2))
        self.assertTrue(skills.invent(p, 'fishing', 3))
        self.assertEqual(p['skills']['fishing'], {
            'level': 1., 'learned_day': 3, 'teacher': None, 'origin': 7,
            'basis': 'invention', 'practice_day': None, 'uses': 0})

    def test_existing_mastery_is_not_reinvented_or_relabelled(self):
        p = self.person()
        skills.invent(p, 'fire', 4)
        before = copy.deepcopy(p)
        self.assertFalse(skills.invent(p, 'fire', 5))
        self.assertEqual(p, before)

    def test_eight_real_daily_practices_reach_competence(self):
        p = self.person()
        skills.expose(p, 'fire', 0)
        for day in range(8):
            self.assertTrue(skills.practice(p, 'fire', day))
            self.assertEqual(skills.qualified(p, 'fire'), day == 7)
            self.assertFalse(skills.practice(p, 'fire', day))
        self.assertEqual(skills.level(p, 'fire'), 1.)
        self.assertEqual(p['skills']['fire']['uses'], 8)
        self.assertTrue(skills.can_teach(p, 'fire'))

    def test_real_use_at_the_cap_is_recorded_once_per_day(self):
        p = self.person()
        skills.invent(p, 'fire', 0)
        self.assertTrue(skills.practice(p, 'fire', 1))
        self.assertFalse(skills.practice(p, 'fire', 1))
        self.assertEqual(skills.level(p, 'fire'), 1.)
        self.assertEqual(p['skills']['fire']['uses'], 1)

    def test_failed_work_unknown_skill_and_missing_ancestors_do_not_practice(self):
        p = self.person()
        self.assertFalse(skills.practice(p, 'fire', 0))
        skills.expose(p, 'fire', 0)
        before = copy.deepcopy(p)
        self.assertFalse(skills.practice(p, 'fire', 1, worked=False))
        self.assertEqual(p, before)
        p['skills']['fishing'] = {'level': .25}
        self.assertFalse(skills.practice(p, 'fishing', 1))

    def test_practicing_a_skill_does_not_invent_prerequisite_practice(self):
        p = self.person()
        skills.invent(p, 'stone_tools', 0)
        skills.expose(p, 'fishing', 0)
        parent = copy.deepcopy(p['skills']['stone_tools'])
        self.assertTrue(skills.practice(p, 'fishing', 1))
        self.assertEqual(p['skills']['stone_tools'], parent)

    def test_late_practice_does_not_expire_durable_knowledge(self):
        p = self.person()
        skills.expose(p, 'fire', 0)
        self.assertTrue(skills.practice(p, 'fire', 1000))
        self.assertAlmostEqual(skills.level(p, 'fire'), .35)
        self.assertEqual(p['skills']['fire']['learned_day'], 0)

    def test_invention_preserves_actual_use_and_daily_deduplication(self):
        p = self.person()
        skills.expose(p, 'fire', 0)
        skills.practice(p, 'fire', 1)
        self.assertTrue(skills.invent(p, 'fire', 1))
        self.assertEqual(p['skills']['fire']['uses'], 1)
        self.assertEqual(p['skills']['fire']['practice_day'], 1)
        self.assertFalse(skills.practice(p, 'fire', 1))

    def test_legacy_capability_is_an_explicit_prior_not_teaching_evidence(self):
        p = self.person()
        history = [row[0] for row in skills.TECH_LADDER]
        skills.migrate_person(p, history, 0, legacy=True)
        self.assertEqual(set(p['skills']), set(history))
        for name in history:
            self.assertTrue(skills.qualified(p, name))
            self.assertFalse(skills.can_teach(p, name))
            self.assertEqual(p['skills'][name], {
                'level': 1., 'learned_day': None, 'teacher': None, 'origin': None,
                'basis': 'legacy_global_capability', 'practice_day': None, 'uses': 0})
        self.assertTrue(skills.practice(p, 'fire', 1))
        self.assertTrue(skills.can_teach(p, 'fire'))
        self.assertEqual(p['skills']['fire']['basis'], 'legacy_global_capability')

    def test_legacy_age_boundary_and_nonlegacy_newborns(self):
        cases = ((True, -12*360, True), (True, -12*360+1, False),
                 (True, 0, False), (False, -18*360, False))
        for legacy, born, expected in cases:
            p = {'id': 7, 'b': born}
            skills.migrate_person(p, ['fire'], 0, legacy=legacy)
            self.assertEqual(bool(p['skills']), expected)

    def test_missing_history_does_not_create_a_legacy_capability(self):
        p = self.person()
        skills.migrate_person(p, [], 0, legacy=True)
        self.assertEqual(p['skills'], {})

    def test_migration_only_initializes_a_missing_field(self):
        for existing in ({}, {'fire': {'level': .25}}, None):
            p = self.person()
            p['skills'] = copy.deepcopy(existing)
            before = copy.deepcopy(p)
            skills.migrate_person(p, ['fire', 'stone_tools'], 1000, legacy=True)
            self.assertEqual(p, before)
        p = self.person()
        skills.migrate_person(p, ['fire'], 0, legacy=True)
        before = copy.deepcopy(p)
        skills.migrate_person(p, ['fire', 'stone_tools'], 1000, legacy=True)
        self.assertEqual(p, before)

    def test_unknown_names_are_not_capabilities(self):
        p = self.person()
        self.assertFalse(skills.expose(p, 'unknown', 0))
        self.assertFalse(skills.invent(p, 'unknown', 0))
        skills.migrate_person(p, ['fire', 'fire', 'unknown'], 0, legacy=True)
        self.assertEqual(list(p['skills']), ['fire'])

    def test_personal_provenance_round_trips_without_mutable_aliases(self):
        p, q = self.person(), self.person(8)
        skills.expose(p, 'fire', 0, teacher=3, origin=2)
        skills.practice(p, 'fire', 1)
        skills.migrate_person(q, [], 0, legacy=False)
        self.assertEqual(q['skills'], {})
        encoded = json.dumps(p, sort_keys=True)
        restored = json.loads(encoded)
        skills.migrate_person(restored, ['fire'], 1000, legacy=True)
        self.assertEqual(json.dumps(restored, sort_keys=True), encoded)


if __name__ == '__main__':
    unittest.main()

"""Personal memories and finite attention for physically grounded instruction.

Callers establish actual witnessed work, sightings and completed lessons. These
helpers never inspect a world, infer a stranger's skills, or consume randomness.
All durations and bounds are illustrative model coefficients.
"""
from typing import Any, Dict, List, Optional

import skills

MENTOR_LIMIT = 12
LOCATION_DAYS = 30
RETRY_DAYS = 7
INTENT_PARTS = 8
VERBAL_LEARNERS = 4
_PREREQUISITES = {tech: parent for tech, parent, _, _ in skills.TECH_LADDER}


def migrate_person(p: Dict[str, Any]) -> None:
    """Add empty independent containers; never invent a person's history."""
    experience = p.setdefault('experience', {})
    experience.setdefault('mentors', [])
    for note in experience['mentors']:
        note.setdefault('retry_day', -1)
    p.setdefault('learning', None)
    p.setdefault('teaching', None)
    p.setdefault('teaching_day', None)
    p.setdefault('teaching_ids', [])


def remember_work(p: Dict[str, Any], teacher_id: int, tech: str,
                  x: int, y: int, day: int) -> bool:
    """Remember only the named actual demonstration, not its hidden ancestors."""
    if tech not in _PREREQUISITES or teacher_id == p.get('id') or not isinstance(teacher_id, int):
        return False
    migrate_person(p)
    notes = p['experience']['mentors']
    for note in notes:
        if note['teacher'] == teacher_id and note['tech'] == tech:
            if day >= note['demonstrated_day']:
                note['demonstrated_day'] = day
            if day >= note['seen_day']:
                note.update(x=x, y=y, seen_day=day)
            return True
    while len(notes) >= MENTOR_LIMIT:
        oldest = min(range(len(notes)), key=lambda i: (notes[i]['seen_day'], notes[i]['demonstrated_day'], i))
        notes.pop(oldest)
    notes.append({'teacher': teacher_id, 'tech': tech, 'x': x, 'y': y,
                  'demonstrated_day': day, 'seen_day': day, 'retry_day': -1})
    return True


def seen_person(p: Dict[str, Any], teacher_id: int, x: int, y: int, day: int) -> None:
    """A sighting updates whereabouts only; it cannot reveal another method."""
    for note in p.get('experience', {}).get('mentors', []):
        if note['teacher'] == teacher_id and day >= note['seen_day']:
            note.update(x=x, y=y, seen_day=day)


def candidate_notes(p: Dict[str, Any], day: int) -> List[Dict[str, Any]]:
    """Detached unknown-method notes with recent sightings and no retry hold."""
    return [dict(note) for note in p.get('experience', {}).get('mentors', [])
            if note['tech'] in _PREREQUISITES and not skills.knows(p, note['tech'])
            and 0 <= day-note['seen_day'] <= LOCATION_DAYS and note.get('retry_day', -1) <= day]


def missing_step(p: Dict[str, Any], desired: str) -> Optional[str]:
    """First unaware ancestor; prerequisite ignorance must not prevent asking."""
    if desired not in _PREREQUISITES or skills.knows(p, desired):
        return None
    parent = _PREREQUISITES[desired]
    if parent is not None and not skills.knows(p, parent):
        return missing_step(p, parent)
    return desired


def start(p: Dict[str, Any], note: Dict[str, Any], parts: int) -> bool:
    """Copy one bounded pursuit intent; caller decides whether to seek it."""
    if (note.get('tech') not in _PREREQUISITES or note.get('teacher') == p.get('id')
            or not isinstance(note.get('teacher'), int) or skills.knows(p, note['tech'])):
        return False
    p['learning'] = {key: note[key] for key in ('teacher', 'tech', 'x', 'y')}
    p['learning'].update(started_part=parts, until_part=parts+INTENT_PARTS)
    return True


def fail(p: Dict[str, Any], day: int) -> None:
    """Only an actual failed pursuit earns a retry delay on its own note."""
    intent = p.get('learning')
    if intent is not None:
        for note in p.get('experience', {}).get('mentors', []):
            if (note['teacher'], note['tech']) == (intent['teacher'], intent['tech']):
                note['retry_day'] = day+RETRY_DAYS
    interrupt(p)


def interrupt(p: Dict[str, Any]) -> None:
    """Bodily or other interruptions do not count as failed instruction."""
    p['learning'] = None


def can_instruct(teacher: Dict[str, Any], learner_id: int, day: int) -> bool:
    """Shared verbal attention budget; callers separately gate actual contact."""
    if not isinstance(learner_id, int) or learner_id == teacher.get('id'):
        return False
    ids = teacher.get('teaching_ids', []) if teacher.get('teaching_day') == day else []
    return learner_id in ids or len(set(ids)) < VERBAL_LEARNERS


def record_instruction(teacher: Dict[str, Any], learner_id: int, day: int) -> bool:
    """Record a completed verbal lesson once; demonstrations use no such slot."""
    if not can_instruct(teacher, learner_id, day):
        return False
    if teacher.get('teaching_day') != day:
        teacher['teaching_day'], teacher['teaching_ids'] = day, []
    if learner_id not in teacher['teaching_ids']:
        teacher['teaching_ids'].append(learner_id)
    return True

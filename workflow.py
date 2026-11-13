"""Lesson-specific workflow. Read this file before the execution adapter."""
from __future__ import annotations
import asyncio
import json
from pathlib import Path
from runtime import atomic_json, contained_path, in_process_tool

async def run(agent, data):
    cases = []
    if not data['cases'] or not 0 <= data['minimum_pass_rate'] <= 1:
        raise ValueError('A nonempty case suite and a valid threshold are required')
    for case in data['cases']:
        try:
            answer = await agent.ask('test_' + case['id'], 'Answer this SDK regression case.', case['question'], case['fixture'])
            cases.append({'id': case['id'], 'passed': case['required'].lower() in answer.lower(), 'execution_error': False})
        except Exception:
            cases.append({'id': case['id'], 'passed': False, 'execution_error': True})
    pass_rate = sum(case['passed'] for case in cases) / len(cases)
    return {'cases': cases, 'pass_rate': pass_rate, 'release_gate': pass_rate >= data['minimum_pass_rate'] and not any(c['execution_error'] for c in cases)}

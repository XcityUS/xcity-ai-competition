"""Evidence-reference checks only. Never infer planning quality from file presence."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads((ROOT / 'brief/design-depth.json').read_text())
MATRIX = POLICY['matrix']

def applies(package):
    p = Path(package).resolve()
    return p not in {(ROOT / x).resolve() for x in POLICY['legacy_submissions']} or (p / MATRIX).exists()

def assess(package, nodes):
    p = Path(package).resolve()
    result = {'automatic': {'status': 'not_required_legacy', 'errors': []},
              'content_review': {'status': 'not_assessed', 'questions': [x['question_en'] for x in POLICY['levels']]},
              'further_work': {'status': 'not_declared', 'items': []}, 'rows': []}
    if not applies(p):
        return result
    errors = result['automatic']['errors']
    try:
        doc = json.loads((p / MATRIX).read_text())
        if not isinstance(doc, dict) or doc.get('schema_version') != 1 or not isinstance(doc.get('rows'), list):
            raise ValueError('expected schema_version 1 and rows array')
        rows = doc['rows']
        required = [x['id'] for x in POLICY['levels']] + ['node:' + n for n in nodes]
        ids = [x.get('id') for x in rows if isinstance(x, dict)]
        if len(ids) != len(rows) or len(set(ids)) != len(ids) or set(ids) != set(required):
            errors.append('matrix rows must exactly cover four levels and every selected node, without duplicates')
        metric_doc = json.loads((p / 'metrics.json').read_text())
        metrics = {x.get('key') for x in metric_doc.get('metrics', []) if isinstance(x, dict)}
        def ref(rel):
            if not isinstance(rel, str) or not rel or Path(rel).is_absolute():
                return False
            target = (p / rel).resolve()
            return p in target.parents and target.is_file()
        for row in rows:
            if not isinstance(row, dict):
                continue
            label = str(row.get('id'))
            status = row.get('status')
            if status not in ('documented', 'partial'):
                errors.append(label + ': status must be documented or partial, never approved/passed')
            gaps = row.get('gaps', [])
            if not isinstance(gaps, list):
                errors.append(label + ': gaps must be an array'); gaps = []
            if status == 'partial' and not gaps:
                errors.append(label + ': partial needs an explicit gap and verification plan')
            for gap in gaps:
                if not isinstance(gap, dict) or any(not isinstance(gap.get(k), str) or not gap[k].strip() for k in ('missing', 'next_step', 'responsible')):
                    errors.append(label + ': each gap needs missing, next_step and responsible')
                elif any(gap[k].startswith(('Replace with', 'State how', 'Fill actual')) for k in ('missing', 'next_step', 'responsible')):
                    errors.append(label + ': replace scaffold gap prompts with actual information')
                else:
                    result['further_work']['items'].append(dict(level=label, **gap))
            for kind in ('drawings', 'geometry', 'metrics'):
                values = row.get(kind)
                if not isinstance(values, list):
                    errors.append(label + ': ' + kind + ' must be an array'); continue
                if not values and not gaps:
                    errors.append(label + ': ' + kind + ' needs evidence or a disclosed gap')
                for value in values:
                    if kind == 'metrics':
                        if not isinstance(value, str) or value not in metrics:
                            errors.append(label + ': unknown metric ' + str(value))
                    elif not ref(value):
                        errors.append(label + ': missing/unsafe ' + kind + ' reference ' + str(value))
            explanation = row.get('explanation', {})
            if not isinstance(explanation, dict) or not ref(explanation.get('path')):
                errors.append(label + ': explanation path is missing or unsafe')
            else:
                heading = explanation.get('heading')
                if not isinstance(heading, str) or not heading.startswith('## ') or not any(line.startswith(heading) for line in (p / explanation['path']).read_text().splitlines()):
                    errors.append(label + ': explanation heading does not exist')
            result['rows'].append({'id': label, 'entrant_status': status, 'content_status': 'not_assessed'})
    except (OSError, ValueError, TypeError, AttributeError) as e:
        errors.append('design-depth matrix cannot be read: ' + str(e))
    result['automatic']['status'] = 'failed' if errors else 'references_consistent'
    result['further_work']['status'] = 'declared' if result['further_work']['items'] else 'none_declared_not_verified'
    return result

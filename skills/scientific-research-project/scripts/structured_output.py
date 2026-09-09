"""Strict single-object decoding with a narrow, auditable punctuation repair."""
import json


def unique_keys(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError('duplicate JSON key: ' + key)
        obj[key] = value
    return obj


def reject_constant(value):
    raise ValueError('nonfinite JSON constant: ' + value)


def decode_object(raw, allow_extra_closer=False):
    text = raw.strip()
    decoder = json.JSONDecoder(object_pairs_hook=unique_keys, parse_constant=reject_constant)
    value, end = decoder.raw_decode(text)
    if not isinstance(value, dict):
        raise ValueError('one JSON object required')
    suffix = text[end:].strip()
    if suffix and not (allow_extra_closer and suffix == '}'):
        raise ValueError('ambiguous trailing data; no automatic repair')
    return value, {'repair': 'removed_one_extra_closing_brace' if suffix else 'none',
                   'removed_suffix': suffix}


def proposal_object(raw):
    value, audit = decode_object(raw, allow_extra_closer=True)
    if not {'contracts', 'blocked'} <= set(value) or set(value)-{'contracts','blocked','expansions'} or not all(isinstance(value[k], list) for k in value):
        raise ValueError('proposal requires contracts and blocked lists only')
    seen = set()
    parents = set()
    for expansion in value.get('expansions', []):
        if not isinstance(expansion,dict) or set(expansion) != {'parent_id','nodes'} or not isinstance(expansion['nodes'],list):
            raise ValueError('invalid expansion schema')
        if not isinstance(expansion['parent_id'],str) or expansion['parent_id'] in parents or not expansion['nodes']:
            raise ValueError('duplicate/empty expansion')
        parents.add(expansion['parent_id'])
    for group in ('contracts', 'blocked'):
        for item in value[group]:
            if not isinstance(item, dict) or not isinstance(item.get('id'), str) or not item['id']:
                raise ValueError('invalid proposal item ID')
            if item['id'] in seen:
                raise ValueError('duplicate/conflicting proposal node')
            seen.add(item['id'])
            if group == 'contracts' and not isinstance(item.get('contract'), dict):
                raise ValueError('contract object required')
            if group == 'blocked' and (not item.get('reason') or type(item.get('needs_user')) is not bool):
                raise ValueError('blocked reason and boolean needs_user required')
    return value, audit

"""Export synthetic behavior cases and summarize evidence-linked HUMAN judgments.

No model invocation and no automatic grading of scientific truth. Missing observations
stay pending. Keep rubric files out of the evaluated agent's accessible workspace.
"""
import argparse
import json
from pathlib import Path
import research_workflow as rw

CASES = Path(__file__).resolve().parents[1] / 'assets/evaluation'


def export(case_id, destination):
    rw.require(case_id in {p.name.removesuffix('.case.json') for p in CASES.glob('*.case.json')}, 'unknown case')
    destination = Path(destination)
    rw.require(not destination.exists(), 'evaluation destination must be new')
    destination.mkdir(parents=True)
    path=destination/'case.json';path.write_bytes((CASES/(case_id+'.case.json')).read_bytes())
    return dict(case=str(path),synthetic=True,rubric_exported=False)


def score(root, run_path, judgment_path=None):
    root=Path(root).resolve();run=rw.read(run_path)
    case=rw.read(rw.receipt(root,run['case']))
    canonical=CASES/(case['case_id']+'.case.json')
    rw.require(rw.sha(canonical)==run['case']['sha256'], 'case differs from benchmark input')
    output=rw.receipt(root,run['output'])
    for k in ('author_invocation_id','configuration'):rw.text(run.get(k), 'run.'+k)
    context=run.get('comparison_context',{})
    rw.require(set(context)=={'model','tools','budget','environment','input_sha256'}, 'comparison context incomplete')
    rw.require(context['input_sha256']==run['case']['sha256'], 'comparison input mismatch')
    metrics=run.get('observed_metrics',{})
    rw.require(set(metrics)=={'elapsed_seconds','input_tokens','output_tokens','cost'}, 'observed metrics required (null if unavailable)')
    for v in metrics.values():rw.require(v is None or (type(v) in (int,float) and v>=0), 'invalid observed metric')
    base=dict(case_id=case['case_id'],configuration=run['configuration'],comparison_context=context,
              observed_metrics=metrics,synthetic=True,quality_claim='human judgment on this observed response only')
    if judgment_path is None:return dict(**base,status='pending_human_review',score=None)
    j=rw.read(judgment_path)
    rw.require(j.get('run')==rw.descriptor(Path(run_path),root), 'judgment must bind exact run manifest')
    rw.require(j.get('output')==run['output'], 'judgment output mismatch')
    reviewer=rw.text(j.get('reviewer_id'),'human reviewer id')
    rw.require(j.get('human_review') is True and reviewer!=run['author_invocation_id'], 'separate human judgment required')
    rubric=rw.read(CASES/(case['case_id']+'.rubric.json'))['criteria'];grades=j.get('grades',{})
    rw.require(set(grades)=={c['id'] for c in rubric}, 'incomplete human rubric')
    points=0;critical=[]
    for c in rubric:
        g=grades[c['id']]
        rw.require(type(g.get('score')) is int and g['score'] in (0,1,2), 'score must be 0/1/2')
        rw.text(g.get('rationale'),'human rationale');rw.text(g.get('response_locator'),'response evidence locator')
        points+=g['score']
        if c['critical'] and g['score']<2:critical.append(c['id'])
    return dict(**base,status='needs_revision' if critical else 'reviewed',score=points/(2*len(rubric)),
                critical_failures=critical,reviewer_id=reviewer)


def compare(a,b):
    rw.require(a['case_id']==b['case_id'] and a['comparison_context']==b['comparison_context'],
               'comparison requires identical case/model/tools/budget/environment')
    rw.require(a['score'] is not None and b['score'] is not None, 'unreviewed responses cannot establish improvement')
    return dict(case_id=a['case_id'],score_difference=b['score']-a['score'],
                critical_failures={'a':a['critical_failures'],'b':b['critical_failures']},
                observed_metrics={'a':a['observed_metrics'],'b':b['observed_metrics']},
                limitation='One synthetic case, human-scored; repeat and add real domain tasks before generalizing.')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('mode',choices=('export','score','compare'))
    ap.add_argument('--case');ap.add_argument('--destination',type=Path);ap.add_argument('--root',type=Path)
    ap.add_argument('--run',type=Path);ap.add_argument('--judgment',type=Path);ap.add_argument('--a',type=Path);ap.add_argument('--b',type=Path)
    a=ap.parse_args()
    if a.mode=='export':out=export(a.case,a.destination)
    elif a.mode=='score':out=score(a.root,a.run,a.judgment)
    else:out=compare(rw.read(a.a),rw.read(a.b))
    print(json.dumps(out,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

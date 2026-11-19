"""Score explicit human responses against a frozen blind-review key; never infer missing ratings."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from statistics import median

CATEGORIES=('skin','eyes','lips','ears','brows_lashes','overall_realism')
MODES=('left','right','generate-motion')
DIRECTIONS=('left','right','up','down')
OPPOSITE=dict(left='right',right='left',up='down',down='up')
DEFECTS=('skin','eye_optics','lips','ears','brows_lashes','groom','gaze','blink',
         'lid_contact','attachment','seam','motion','other')
VARIANTS=('rose-brown','golden-hazel','olive-amber','neutral-deep','cool-grey')


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def response_template(key,key_hash):
    return dict(reviewer='',key_sha256=key_hash,independent_first_pass=None,
                directions=dict.fromkeys(key['directions']),
                appearance={case:dict.fromkeys(CATEGORIES) for case in key['appearance']},
                motion={case:dict(motion_naturalness=None) for case in key['motion']},
                severe_defects=None)


def score(key,responses,key_hash):
    if not isinstance(key.get('candidate_sha256'),str) or len(key['candidate_sha256'])!=64:
        raise ValueError('Review key must identify the frozen candidate')
    directions=key['directions'];appearance=key['appearance'];motion=key.get('motion',{})
    if set(directions.values())!=set(DIRECTIONS):
        raise ValueError('Review must test all four cardinal directions')
    if any(type(case.get('candidate')) is not bool for case in appearance.values()):
        raise ValueError('Each appearance case needs an explicit candidate flag')
    coverage={(case.get('variant'),case.get('output')) for case in appearance.values() if case['candidate']}
    required={(variant,output) for variant in VARIANTS for output in ('full','texture_only')}
    if not required.issubset(coverage):
        raise ValueError('Review must cover all five variants on full and texture-only outputs')
    references={case.get('reference') for case in appearance.values() if not case['candidate']}
    if not {'rc5','v22'}.issubset(references):
        raise ValueError('Missing rc.5 or immutable v22 comparison cases')
    if any(type(case.get('candidate')) is not bool or case.get('mode') not in MODES for case in motion.values()):
        raise ValueError('Motion cases need an explicit candidate flag and known mode')
    if {case['mode'] for case in motion.values() if case['candidate']}!=set(MODES):
        raise ValueError('Review must include all three candidate motion modes')
    if (set(directions)&set(appearance) or set(directions)&set(motion) or set(appearance)&set(motion)):
        raise ValueError('Review case identifiers overlap')
    reviewed_cases={**appearance,**motion}
    if not 3<=len(responses)<=5:raise ValueError('Need 3–5 completed independent reviews')
    observers=set();correct=0;total=0;confusion=Counter();severe={}
    ratings={case:{category:[] for category in CATEGORIES} for case in appearance}
    motion_ratings={case:[] for case in motion}
    per_direction={name:dict(correct=0,total=0) for name in DIRECTIONS}
    for response in responses:
        observer=response.get('reviewer','').strip()
        if not observer or observer.casefold() in observers:
            raise ValueError('Each review needs a distinct reviewer identifier')
        observers.add(observer.casefold())
        if response.get('independent_first_pass') is not True:
            raise ValueError('Reviewer must attest an independent blind first pass')
        if response.get('key_sha256')!=key_hash:
            raise ValueError('Response belongs to another review packet')
        if (set(response['directions'])!=set(directions) or set(response['appearance'])!=set(appearance)
                or set(response.get('motion',{}))!=set(motion)):
            raise ValueError('Incomplete or unexpected review cases')
        for case,expected in directions.items():
            answer=response['directions'][case]
            if answer not in (*DIRECTIONS,'unclear'):raise ValueError('Missing or invalid direction answer')
            correct+=answer==expected;total+=1
            per_direction[expected]['correct']+=answer==expected
            per_direction[expected]['total']+=1
            if answer==OPPOSITE[expected]:confusion[case]+=1
        for case in appearance:
            if set(response['appearance'][case])!=set(CATEGORIES):
                raise ValueError('Missing or unexpected appearance categories')
            for category,value in response['appearance'][case].items():
                if type(value) is not int or not 1<=value<=5:
                    raise ValueError('Every appearance rating must be an integer from 1 to 5')
                ratings[case][category].append(value)
        for case in motion:
            entry=response['motion'][case]
            if set(entry)!={'motion_naturalness'}:
                raise ValueError('Motion case needs a naturalness rating')
            value=entry['motion_naturalness']
            if type(value) is not int or not 1<=value<=5:
                raise ValueError('Every motion rating must be an integer from 1 to 5')
            motion_ratings[case].append(value)
        if not isinstance(response.get('severe_defects'),list):
            raise ValueError('Explicit severe-defect review required')
        for defect in response['severe_defects']:
            case=defect['case'];code=defect['code']
            if case not in reviewed_cases or code not in DEFECTS or not defect.get('notes','').strip():
                raise ValueError('Defect needs a known case, category and explanatory notes')
            if reviewed_cases[case]['candidate']:
                # One observer mentioning a problem on multiple variants counts once.
                severe.setdefault(code,set()).add(observer)
    medians={case:{category:median(values) for category,values in categories.items()}
             for case,categories in ratings.items()}
    low=[dict(case=case,category=category,median=value)
         for case,categories in medians.items() if appearance[case]['candidate']
         for category,value in categories.items() if value<4]
    motion_medians={case:median(values) for case,values in motion_ratings.items()}
    low.extend(dict(case=case,category='motion_naturalness',median=value)
               for case,value in motion_medians.items() if motion[case]['candidate'] and value<4)
    shared={code:sorted(names) for code,names in severe.items() if len(names)>=2}
    systematic=sorted(case for case,count in confusion.items() if count>=2)
    accuracy=correct/total
    passed=accuracy>=.95 and not low and not shared and not systematic
    return dict(candidate_sha256=key['candidate_sha256'],key_sha256=key_hash,
                reviewers=len(observers),cardinal_accuracy=accuracy,
                per_direction=per_direction,medians=medians,motion_medians=motion_medians,below_target=low,
                shared_severe_defects=shared,systematic_opposite_cases=systematic,
                independent_review_gate_passed=passed,
                qualification='Explicit human response scoring only. User identity approval, technical qualification and submission readiness are separate gates.')


def main(a):
    if a.out.exists():raise FileExistsError(a.out)
    key_hash=sha(a.key)
    key=json.loads(a.key.read_text(encoding='utf-8'))
    if a.template:
        report=response_template(key,key_hash)
    else:
        report=score(key,[json.loads(path.read_text(encoding='utf-8')) for path in a.responses],key_hash)
        report.update(recipe_sha256=sha(__file__),response_sha256={path.name:sha(path) for path in a.responses})
        if len(report['response_sha256'])!=len(a.responses):raise ValueError('Response filenames must be distinct')
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('RESULT '+str(a.out))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--key',type=Path,required=True)
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--responses',type=Path,nargs='+')
    mode.add_argument('--template',action='store_true')
    p.add_argument('--out',type=Path,required=True)
    main(p.parse_args())

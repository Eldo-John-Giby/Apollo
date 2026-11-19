import copy
from pathlib import Path
import sys

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from gnm_v22_review_gate import CATEGORIES,VARIANTS,MODES,score,response_template


def reviews():
    appearance={f'A{index}':dict(candidate=True,variant=variant,output=output)
                for index,(variant,output) in enumerate(
                    ((variant,output) for variant in VARIANTS for output in ('full','texture_only')),1)}
    appearance.update(R1=dict(candidate=False,reference='rc5'),R2=dict(candidate=False,reference='v22'))
    key=dict(candidate_sha256='a'*64,directions=dict(C1='left',C2='right',C3='up',C4='down'),
             appearance=appearance,
             motion={f'M{i}':dict(candidate=True,mode=mode) for i,mode in enumerate(MODES,1)})
    responses=[dict(reviewer=str(index),key_sha256='key',independent_first_pass=True,
                    directions=copy.deepcopy(key['directions']),
                    appearance={case:dict.fromkeys(CATEGORIES,4) for case in key['appearance']},
                    motion={case:dict(motion_naturalness=4) for case in key['motion']},
                    severe_defects=[]) for index in range(3)]
    return key,responses


def test_complete_human_responses_can_pass_without_claiming_identity_approval():
    key,responses=reviews()
    report=score(key,responses,'key')
    assert report['independent_review_gate_passed']
    assert report['cardinal_accuracy']==1
    assert 'User identity approval' in report['qualification']


@pytest.mark.parametrize('fault',['duplicate','missing','blank_rating','wrong_packet','not_blind','few'])
def test_missing_or_untrusted_review_evidence_cannot_pass(fault):
    key,responses=reviews()
    if fault=='duplicate':responses[1]['reviewer']=responses[0]['reviewer']
    if fault=='missing':responses[0]['directions'].pop('C4')
    if fault=='blank_rating':responses[0]['appearance']['A1']['skin']=None
    if fault=='wrong_packet':responses[0]['key_sha256']='other'
    if fault=='not_blind':responses[0]['independent_first_pass']=False
    if fault=='few':responses.pop()
    with pytest.raises(ValueError):score(key,responses,'key')


def test_shared_defects_and_low_candidate_category_fail_even_with_good_gaze():
    key,responses=reviews()
    for response in responses[:2]:
        response['appearance']['A1']['ears']=3
        response['severe_defects']=[dict(case='A1',code='lid_contact',notes='Visible clipping')]
    report=score(key,responses,'key')
    assert not report['independent_review_gate_passed']
    assert report['below_target']==[dict(case='A1',category='ears',median=3)]
    assert 'lid_contact' in report['shared_severe_defects']


def test_direction_confusion_fails_and_reference_ratings_do_not_hide_candidate_quality():
    key,responses=reviews()
    for response in responses:
        response['appearance']['R1']=dict.fromkeys(CATEGORIES,1)
    assert score(key,responses,'key')['independent_review_gate_passed']
    for response in responses[:2]:response['directions']['C1']='right'
    report=score(key,responses,'key')
    assert not report['independent_review_gate_passed']
    assert report['systematic_opposite_cases']==['C1']


def test_narrow_review_cannot_qualify_full_texture_variant_scope():
    key,responses=reviews()
    key['appearance'].pop('A10')
    with pytest.raises(ValueError,match='all five'):
        score(key,responses,'key')


def test_response_template_does_not_default_to_approval_or_no_defects():
    key,_=reviews()
    template=response_template(key,'key')
    assert template['severe_defects'] is None
    assert template['independent_first_pass'] is None
    assert all(value is None for value in template['directions'].values())
    assert all(value is None for case in template['appearance'].values() for value in case.values())
    assert all(case['motion_naturalness'] is None for case in template['motion'].values())
    assert 'motion_naturalness' not in template['appearance']['R2']


def test_three_modes_need_explicit_motion_reviews_and_low_ratings_fail():
    key,responses=reviews()
    key['motion'].pop('M3')
    with pytest.raises(ValueError,match='all three'):
        score(key,responses,'key')
    key,responses=reviews()
    responses[0]['motion']['M1']['motion_naturalness']=None
    with pytest.raises(ValueError,match='Every motion rating'):
        score(key,responses,'key')
    key,responses=reviews()
    for response in responses[:2]:
        response['motion']['M2']['motion_naturalness']=3
        response['severe_defects']=[dict(case='M2',code='blink',notes='Visible blink defect')]
    report=score(key,responses,'key')
    assert not report['independent_review_gate_passed']
    assert report['motion_medians']['M2']==3
    assert 'blink' in report['shared_severe_defects']

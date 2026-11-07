# Problem-statement audit — 7 November 2026

Basis: the user's consolidated Track 01 specification supplied after development
freeze. This audits repository evidence; it does not verify registration/account
state or award an official score.

## Technical requirements

| Requirement | Status | Evidence |
| --- | --- | --- |
| Textured MPFB face with left/right eye bones | Covered | Packed frozen scene, source character, explicit mapping and attribution |
| Physical-center spherical rotation and synchronous binocular fixation | Covered | Evaluated geometry/convergence checks, 1000 random poses |
| move(h,v), reset(), render() | Covered | Standalone wrapper; direct Blender invocation and extracted-archive reconstruction |
| Camera 40 cm, target 35 cm, +/-5 cm bounds, constant lighting | Covered | Calibrated scene audit and projected geometry checks |
| Normalized inputs | Covered | Finite input validation, clamping and tests |
| Ten clockwise 1024x1024 PNGs, top first | Covered | Actual archived renders, schema/sequence/image validation |
| World rotations, pupil projections, camera matrix | Covered | Actual metadata; independent projection and pixel-mask checks |
| Left/Right/Up/Down/Reset visibly correct | Covered | Both detectors, enlarged comparison, visibility masks and exact reset |
| Required scene/wrapper/renders/metadata/README layout | Covered inside development ZIP | One apollo-development/ root with the required children |
| Contact sheet OR 1–2 minute track demo | Covered by contact sheet | Included in archive and milestone directory |
| Reproducible README and Docker files | Covered to measured scope | Native/secondary qualification; Docker build, tests and one pose |

All V1–V17 checks pass on the frozen inputs. They are our internal checks, not
the organizer's published evaluator. The slides do not state exact Calibration
or Automation measurement/deduction rules. No numerical competition score can
be inferred reliably from category weights alone.

## Event/submission readiness

| Requirement | Status / remaining action |
| --- | --- |
| CollegeName_TeamName.zip | Pending actual registered team name; current ZIP is explicitly a development archive |
| Conventional delivery layout | ZIP children are correct; final archive/root must use the required team name. Repo currently stores the complete scene/output layout inside the milestone ZIP, not at repo root |
| Public or shared GitHub access | Pushed to GitHub; intended evaluator access still needs confirmation |
| General demo video, maximum 3 minutes | Pending final video and accessible link; GIF/contact sheet are not that video |
| Named PPT/PDF | Pending CollegeName_TeamName_Submission_ppt deck/export and team details |
| Required presentation contents | Still need final deck: theme/title/team, problem, architecture, stack, innovation, results, limitations |
| Up to four members, one college, one theme | User/team confirmation required; not inferable from code |
| Registration before 8 November 11:59 PM | Not confirmed in this session; user must complete/confirm |
| Final submission form before 18 November 11:59 PM | Later human delivery; not performed |
| Link accessibility and final naming audit | Pending final delivery artifacts |

An optional unpacked delivery directory in the repo would remove evaluator
ambiguity. The official-looking team ZIP must not be produced with an invented
registration name. Development freeze does not mean submission readiness.

## Supplied clarifications versus older local transcription

- Frame 3 formula gives v=-0.309016994..., and the archived metadata is correct.
- User-supplied registration URL: https://forms.gle/oGBXsydqbhE3HS2o9 . The older
  screenshot transcription retained an uncertain URL; use this clarification.
- New supplied details specify top-four prize sharing and MAGPIE test wording;
  older docs say distribution unknown / MAGIC. These do not affect the code.
- General video remains required even though a contact sheet satisfies the
  track-specific alternative. A 1–2 minute video fits the stated 3-minute cap;
  the separate 5-minute mention remains an organizer question.
- Team ZIP plus GitHub, video, deck and form are complementary deliverables.
- Event dates are supplied as tentative. Registration/submission status and any
  organizer updates must be confirmed separately.

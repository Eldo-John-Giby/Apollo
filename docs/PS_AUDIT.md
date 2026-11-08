# Problem-statement audit — 7 November 2026

Basis: the user's consolidated Track 01 specification supplied after development
freeze. This audits repository evidence; it does not verify registration/account
state or award an official score.

## Technical requirements

| Requirement | Status | Evidence |
| --- | --- | --- |
| Textured MPFB face with left/right eye bones | Covered | Packed qualified upgrade scene, source character, explicit mapping and attribution |
| Physical-center spherical rotation and synchronous binocular fixation | Covered | Evaluated geometry/convergence checks, 1009 independently checked poses |
| move(h,v), reset(), render() | Covered | Standalone wrapper; direct Blender invocation and extracted-archive reconstruction |
| Camera 40 cm, target 35 cm, +/-5 cm bounds, constant lighting | Covered | Calibrated scene audit and projected geometry checks |
| Normalized inputs | Covered | Finite input validation, clamping and tests |
| Ten clockwise 1024x1024 PNGs, top first | Covered | Actual archived renders, schema/sequence/image validation |
| World rotations, pupil projections, camera matrix | Covered | Actual metadata; independent projection and pixel-mask checks |
| Left/Right/Up/Down/Reset visibly correct | Covered | Both detectors, enlarged comparison, visibility masks and exact reset |
| Required scene/wrapper/renders/metadata/README layout | Covered in technical release | Conventional delivery/apollo children plus apollo-competition ZIP |
| Contact sheet OR 1–2 minute track demo | Covered | Contact sheet and actual 105-second narrated demo |
| Reproducible README and Docker files | Covered to measured scope | Native/Linux all V1–V17; full applicable 5.2 secondary suites |

All native V1–V17 checks pass on the selected upgrade inputs. They are our internal checks, not
the organizer's published evaluator. The slides do not state exact Calibration
or Automation measurement/deduction rules. No numerical competition score can
be inferred reliably from category weights alone.

## Event/submission readiness

| Requirement | Status / remaining action |
| --- | --- |
| CollegeName_TeamName.zip | Pending actual registered team name; technical ZIP remains apollo-competition.zip until supplied |
| Conventional delivery layout | Complete delivery/apollo/{scene.blend,wrapper/eyes.py,renders,metadata.json,README.md}; event archive/root still needs actual team name |
| Public or shared GitHub access | Technical source and final release are on competition-upgrade; GitHub reports the repo is PRIVATE (7 Nov). Evaluator sharing remains team-owned and unconfirmed |
| General demo video, maximum 3 minutes | 105.05-second MP4 complete, full decode and representative visual review pass; accessible hosted link remains team-owned |
| Named PPT/PDF | Editable ten-slide Apollo_Submission_ppt.pptx complete and reviewed; registered filename and team details remain required |
| Required presentation contents | Deck covers theme/title, problem, architecture, stack, innovation, results and limitations; actual team/member identity must replace technical-prototype identity |
| Up to four members, one college, one theme | User/team confirmation required; not inferable from code |
| Registration before 8 November 11:59 PM | Not confirmed in this session; user must complete/confirm |
| Final submission form before 18 November 11:59 PM | Later human delivery; not performed |
| Link accessibility and final naming audit | Local artifacts reviewed and hash-bound; evaluator account/link access still unconfirmed |

The technical release contains the executable unpacked layout and development
ZIP. No archive, deck or identity is presented as the registered team's final
submission. The exact event filename and sharing checks must use real team data.

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

## Current automation scope — 8 November 2026

The user explicitly prohibits creating or regenerating videos and presentations.
This overrides earlier implementation plans for new media. Historical media stay
archived. The event requirements above still describe organizer requirements;
they are not waived or marked complete for the new realism candidate. Any future
media preparation and event upload are outside the current automated work.

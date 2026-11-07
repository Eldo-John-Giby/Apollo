// Editable evidence deck. Run with Node and @oai/artifact-tool installed.
import fs from 'node:fs/promises';
import path from 'node:path';
import {Presentation,PresentationFile} from '@oai/artifact-tool';

const root=path.resolve(process.argv[2]??'.');
const output=path.resolve(process.argv[3]??path.join(root,'out/upgrade/presentation'));
const u=path.join(root,'out/upgrade');
await fs.mkdir(output,{recursive:true});
async function report(file){try{return JSON.parse(await fs.readFile(path.join(u,file),'utf8'));}catch{return null;}}
const qualification=await report('candidate/verification_report.json');
const dataset=await report('dataset-256/analysis.json');
const independent=await report('candidate/verification/independent_geometry.json');
const visibility=await report('dataset-visibility/report.json')??await report('corner-visibility/report.json');
const identity=await report('identity.json');
const p=Presentation.create({slideSize:{width:1280,height:720}});
const ink='#142B3B',muted='#526571',accent='#087F8C',paper='#F4F6F5';
function text(s,value,x,y,w,h,size=24,color=ink,bold=false){
  const t=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
  t.text=value;t.text.insets=0;t.text.style={fontFamily:'Arial',fontSize:size,color,bold};return t;
}
function slide(title,kicker,notes){
  const s=p.slides.add();s.background.fill=paper;
  text(s,kicker.toUpperCase(),64,34,1120,26,17,accent,true);
  text(s,title,64,83,1152,84,36,ink,true);
  text(s,'APOLLO  /  TRACK 01',64,672,650,24,17,muted);
  text(s,String(p.slides.items.length).padStart(2,'0'),1155,672,60,24,17,muted);
  s.speakerNotes.text=notes;return s;
}
async function pic(s,file,x,y,w,h,alt,crop){
  const bytes=await fs.readFile(path.join(u,file));
  s.images.add({blob:bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),contentType:file.endsWith('.jpg')?'image/jpeg':'image/png',alt,fit:'contain',crop,position:{left:x,top:y,width:w,height:h}});
}
function para(s,heading,body,x,y,w){text(s,heading,x,y,w,40,27,ink,true);text(s,body,x,y+52,w,145,23,muted);}

let s=slide('Calibrated gaze, reproducible pixels','Samsung XR Hackathon 2026',
  'Theme ID: Track 01 — Synthetic Eye Movement & Virtual Camera Rendering. Technical prototype, not an official score. Asset provenance: assets/ATTRIBUTION.md. Team identity must be supplied by the team; no registration claim is made.');
text(s,'APOLLO',64,200,555,90,64,ink,true);
text(s,'Synthetic Eye Movement &\nVirtual Camera Rendering',64,310,555,110,32,ink);
text(s,identity?.team??'Technical prototype',64,482,555,40,23,accent,true);
text(s,identity?.members?.join('  •  ')??'College and member identity: maintained by the team',64,534,555,85,19,muted);
await pic(s,'candidate/renders/frame_00.png',670,176,540,465,'Actual top-gaze render from the candidate scene');

s=slide('A gaze label needs a physical eye model','Problem',
  'Requirements source: docs/problem_statement.md and user-supplied consolidated problem statement. No claim of demonstrated gaze-estimator accuracy or capture-cost savings.');
para(s,'Capturing extreme gaze','XR training needs gaze-labelled images. Real-eye capture at extreme angles is slow, sensitive and difficult to calibrate.',64,204,520);
para(s,'Planar motion is insufficient','Moving a pupil across a flat surface cannot reproduce rotation around an eye center or binocular convergence.',670,204,520);
text(s,'Our scope: a textured rig, metric fixation, deterministic articulation,\nand a directly executable render package.',64,484,1130,115,30,accent,true);

s=slide('One articulation API, two ways to operate it','Solution architecture',
  'Editable native architecture diagram. Public wrapper remains standalone; optional panel invokes that wrapper. Independent oracle imports no production geometry. See wrapper/eyes.py, tools/live_controls.py and tools/reference_geometry.py.');
const nodes=[['Normalized input','h, v ∈ [−1, +1]'],['Public wrapper','move / reset / render'],['Blender scene','Eye bones + packed textures'],['Output','10 PNGs + metadata']];
for(let i=0;i<4;i++){
  const x=64+i*299;
  s.shapes.add({geometry:'rect',position:{left:x,top:230,width:255,height:145},fill:'#E3EBEB',line:{fill:accent,width:1}});
  text(s,nodes[i][0],x+18,250,219,43,24,ink,true);
  text(s,nodes[i][1],x+18,304,219,60,20,muted);
  if(i<3)s.shapes.add({geometry:'rightArrow',position:{left:x+263,top:286,width:27,height:23},fill:accent,line:{fill:'none',width:0}});
}
para(s,'Optional live controls','Blender sidebar uses the same API. No alternate gaze solver or background handlers.',64,444,525);
para(s,'Independent verification','NumPy reference → deformed mesh measurements → rendered pupil and mask checks.',670,444,525);

s=slide('Metric constraints are explicit and testable','Calibration',
  'World subject faces −Y; +Z up. Camera at (0,−0.4,0), target (0.05h,−0.35,0.05v). IPD measured from rig, not inferred from rendered pixels. Anatomical L is image right. Metadata camera_matrix is intrinsic 3×3; world Euler XYZ rotations are radians.');
const rows=[['Camera','40 cm from eye midpoint'],['Fixation','35 cm forward; ±5 cm horizontally / vertically'],['Motion','True 3D rotation around each eye center'],['Image','1024 × 1024 PNG; constant lighting'],['Sequence','10 clockwise poses; start at top']];
for(let i=0;i<rows.length;i++){text(s,rows[i][0],64,201+i*82,240,50,26,accent,true);text(s,rows[i][1],330,201+i*82,865,60,26,ink);}

s=slide('Direction and sequence are checked in the pixels','Required movement',
  'Actual ten-frame renders; theta=2πk/10, h=sin theta, v=cos theta. Frame 3 v is negative. Official schema remains unchanged. Five direction/reset checks additionally use masks, blind ellipse detection and template displacement. See candidate/verification_report.json.');
await pic(s,'candidate/contact_sheet.png',64,188,1148,410,'Ten-frame clockwise sweep with recorded inputs');
text(s,'Left · Right · Up · Down · Reset     |     Shared target, separate eye-center rotations',64,610,1140,37,22,accent,true);

s=slide('Correctness is challenged with deliberate faults','Independent evidence',
  'Sources: candidate/verification/independent_geometry.json, candidate/verification_report.json and dataset-visibility/report.json. Thresholds are project acceptance gates, not official Samsung scoring methods. Fault injection runs in a disposable process.');
const passCount=qualification?Object.values(qualification.checks).filter(x=>x.status==='PASS').length:null;
const metrics=[['1009','evaluated geometry poses'],['14','injected geometry / resource faults'],[visibility?.passed?String(visibility.poses):'Pending','mask-tested dataset poses']];
for(let i=0;i<3;i++){const x=64+i*395;text(s,metrics[i][0],x,207,350,105,72,accent,true);text(s,metrics[i][1],x,328,350,85,24,ink);}
text(s,qualification?`${passCount}/17 local checks pass on the primary report`:'Full runtime qualification is still running',64,472,1120,55,30,ink,true);
text(s,'Independent Rodrigues math + actual deformed pupil surfaces.\nAdversarial occlusion is rendered and must fail the visibility gate.',64,548,1120,83,24,muted);

s=slide('A seeded dataset extends the ten-frame protocol','Research capability',
  'Sources: dataset-256/dataset.json, dataset-256/analysis.json and dataset-visibility/report.json. One identity, lighting, camera and pupil size; no machine-learning benchmark. Dataset schema is apollo.dataset/1, separate from the required ten-frame metadata.');
text(s,dataset?.passed?`${dataset.frames} rendered frames`:'256-frame generation in progress',64,192,620,55,36,accent,true);
text(s,'Nine anchor poses + seeded random square coverage.\n\nPer-image hashes and atomic progress enable safe resume. Changed inputs or images reject reuse.',64,284,520,214,25,ink);
text(s,dataset?.passed?`Maximum independent guided-pixel error:\n${dataset.max_pixel_oracle_error_px.toFixed(3)} px`:'Every completed image receives independent checks.',64,540,520,80,24,muted);
try{await pic(s,'dataset-256/coverage.png',680,186,520,446,'Measured normalized gaze coverage');}catch{await pic(s,'dataset-smoke/coverage.png',680,186,520,446,'Nine-anchor smoke coverage; full dataset pending');}

s=slide('Interactive controls call the exact same wrapper','Operator experience',
  'Actual screenshot from the existing live Blender scene, preserving unsaved edits. This viewport uses the earlier look; final-quality renders use the selected candidate. Interactive five-direction/reset and pose-render checks supplement background API/operator parity.');
await pic(s,'ui/sidebar.jpg',64,180,440,467,'Crop of the observed Blender Apollo sidebar; original screenshot retained', {left:990/1536,top:97/864,right:285/1536,bottom:428/864});
para(s,'One API for both workflows','Move and reset the eyes.\nRender the current pose.\nGenerate the official ten-frame sweep.',600,214,590);
text(s,'The optional sidebar adds convenience.\nEvaluators run wrapper/eyes.py directly.',600,505,590,120,28,accent);

s=slide('Reproducible delivery is part of the product','Stack and deployment',
  'Stack: Blender 4.5 LTS/Python bpy, MPFB/MakeHuman CC0 source assets, NumPy geometry, OpenCV/Pillow verification, pytest, Docker Linux. Secondary runtime 5.2 is separately checked. Each artifact report records actual versions and hashes; cross-version byte identity is not claimed.');
para(s,'Standalone package','scene.blend · wrapper/eyes.py · renders/\nmetadata.json · README.md\nContact sheet and packed textures included.',64,205,530);
para(s,'Repeatable execution','Native Blender and Docker workflows.\nClean configuration, different working directory, extracted archive reproduction.',670,205,530);
text(s,'Blender + Python / bpy + NumPy + OpenCV + pytest + Docker',64,465,1130,85,29,accent,true);
text(s,'Reports bind scene, wrapper, images, verification sources and diagnostic evidence.',64,575,1130,65,23,muted);

s=slide('A measured prototype, with clear limits','Results and limitations',
  'No official evaluation score or jury result is claimed. Registration, event submission, final identity and upload links are maintained by the team. Human visual preference remains a human judgement. Technical artifact status is in docs/UPGRADE_PROGRESS.md and final release receipts.');
para(s,'Demonstrated capabilities','Calibrated binocular articulation, ten-frame automation, independent geometry/pixel checks, dataset generation and shared-API live controls.',64,208,520);
para(s,'Model limits','One face identity and fixed 4 mm pupils. Static lids and lighting. Simplified eye surfaces; no refractive cornea, blink or trained estimator.',670,208,520);
text(s,'Our benchmark is reproducibility and geometric/image correctness.\nThe official score belongs to the evaluators.',64,495,1130,115,31,accent,true);

for(let i=0;i<p.slides.items.length;i++){
  const blob=await p.export({slide:p.slides.items[i],format:'png',scale:1});
  await fs.writeFile(path.join(output,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await blob.arrayBuffer()));
}
await (await PresentationFile.exportPptx(p)).save(path.join(output,'apollo-draft.pptx'));
await fs.writeFile(path.join(output,'deck-provenance.json'),JSON.stringify({artifactTool:true,slides:p.slides.items.length,qualificationAvailable:!!qualification,datasetAvailable:!!dataset,independentAvailable:!!independent,identityAvailable:!!identity},null,2));
console.log(`Wrote ${p.slides.items.length} editable slides to ${output}`);

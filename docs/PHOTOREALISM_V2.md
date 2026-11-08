# Photorealism v2 execution

Branch photorealism-v2; preserved baseline is apollo-v0.3.0-rc.1.
No release pipeline, videos or presentations are authorized for this phase.

Implemented: clean review recipe, named collections, hidden render-only helper
meshes in viewport, camera workspace, exact V1/V2 preflight, source/scene/recipe
hash receipts, preserved calibrated eye meshes. The viewport rectangles were
render-hidden stock eye/lash geometry left visible in the old workspace.

MCP connection was restored by opening an isolated review scene and starting the
installed addon server. Current visible scene is an adult female anatomy
EXPERIMENT, not an accepted finished candidate. Inspection found original macro
age 0.3 (child/adult blend) and gender 1; prototype uses age 0.5, gender 0, then
aligns paired orbital surface anchors to the protected original eye positions.
No eye vertices, eye centers or camera calibration are intentionally changed.

Baseline actual nine-pose RGB/mask capture is running under out/photorealism-v2.
Compatible young_asian_female skin is installed; its MHMAT explicitly declares
CC0 September 2020, Data Collection AB / Joel Palmius / Jonas Hauquier. No new
skin has been incorporated yet. Read assets/ATTRIBUTION.md for source ecosystem.

Remaining: validate/bake female anatomy and mouth closure, refit lid/brow/lash
attachments, adopt and document female skin/maps, refine eyes, construct the
pulled-back bun groom, lighting, CPU benchmarking and targeted final checks.
Do not describe this scaffold/prototype as completed photorealism.

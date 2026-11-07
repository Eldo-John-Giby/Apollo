# Apollo: Gaze Tracking for Samsung XR

## What is Apollo?

Apollo is a tool that helps create realistic eye movements and gaze direction for Samsung XR headsets. Think of it like a sophisticated puppeteer for digital eyes - it makes sure virtual characters look at the right things in the right way.

**The simple version:** Apollo takes a 3D character model and calculates where their eyes should look, then generates pictures (images) that prove the eyes are working correctly. It's used to make sure XR headsets can track gaze accurately for things like:
- Where a person is looking
- Whether the eyes are tracking properly
- Making sure the eyes look natural and not "glitchy"

## What's Inside the Project?

Apollo contains everything needed to build, test, and verify gaze tracking:

### 1. **The Eye System**
- Two eyes that can look in different directions (left, right, up, down)
- Special "pupil" that detects and measures eye position
- Can switch between two modes:
  - **Radial mode**: Enhanced eye appearance (default)
  - **Flat mode**: Original, simpler eye appearance

### 2. **Testing Suite**
- 60 different tests (labeled V1 through V17) that check if everything works
- Each test checks something specific:
  - V1-V6: Basic eye setup, size, pivots, convergence
  - V7-V10: Pupil detection, movement, direction checks
  - V11-V14: Call sequences, repeatability, pupil visibility
  - V15-V17: Texture integrity, annotation checks, rotation limits

### 3. **Build Commands** (like steps in a recipe)

| Command | What it does |
|---------|--------------|
| `test` | Runs all 60 tests to check the eye system |
| `doctor` | Checks if the environment is set up correctly (like a health check) |
| `sync` | Synchronizes core files |
| `inspect` | Examines the character model |
| `scene` | Builds the base 3D scene |
| `production-scene` | Builds the final scene for production |
| `sweep` | Runs a framing protocol (checks eye positions) |
| `framing` | Experiments with different camera angles |
| `validate` | Validates metadata (information about the renders) |
| `sheet` | Generates a contact sheet (contact sheet is like a photo collage) |
| `prepare` | Prepares candidate artifacts |
| `demo` | Generates demonstration artifacts |
| `verify` | Verifies everything works with provenance checks |
| `bundle` | Packs everything into a ZIP file (requires a team name) |
| `all` | Runs the complete pipeline from start to finish |

### 4. **Development Milestones** (Major achievements)

The project has reached 5 major milestones, like checkpoints in a video game:

- **M0**: Basic setup working - character model loaded, initial renders created
- **M1**: Direction testing passed - eyes can look left, right, up, down, and reset correctly
- **M2**: Full baseline established - all tests V1-V15 and V17 pass; can regenerate results identically
- **M3**: Visual improvements - made eyes look better without breaking the tests
- **M5**: Development freeze - final polished version ready; all tests pass with evidence preserved

## Key Achievements (What Makes This Special)

### **All 17 Tests Pass**
After lots of work, every single one of the 17 validation checks (V1-V17) passes. This means the eye tracking is reliable and reproducible.

### **Three Blender Versions Supported**
The project works with:
- **Blender 4.5.15 LTS**: Primary version (pinned for exact results)
- **Blender 5.2.3 LTS**: Secondary version (portable, for verification)
- Both versions have been tested and verified

### **Performance Numbers**
- A single eye render takes about 23.653 seconds on average (with 32 samples)
- Higher quality (128 samples) takes about 113.58 seconds but looks slightly better
- The project balances quality and speed carefully

### **Evidence and Documentation**
Everything documented with:
- Before/after comparisons
- Measurement records
- SHA-256 hash verification (like digital fingerprints to ensure nothing changed)
- 60 Python tests that act as a safety net

## How to Get Started (Simple Steps)

### Step 1: Install Dependirements
```
pip install -r requirements.txt
```
This installs the Python tools needed.

### Step 2: Set Up Blender (Required)
You need Blender installed (version 4.5 LTS recommended). Think of Blender as the 3D software that actually creates the images.

### Step 3: Run the Full Pipeline
```
python tasks.py all
```
This runs the complete workflow - it tests, builds, verifies, and generates all the output files.

### Step 4: Explore the Results
After running the pipeline, you'll find:
- **out/production/**: Final verified outputs
- **milestones/dev-freeze-2026-11-07/**: The final frozen milestone with all evidence
- Various reports and logs showing what passed and what didn't

## What the Outputs Look Like

### **Ten 1024x1024 PNG Images**
Ten high-resolution pictures (1024x1024 pixels) showing the eye in different directions, taken clockwise around a circle.

### **Contact Sheet**
A single image that combines all ten PNGs into a grid - like a photo album page.

### **GIF Animation**
A looping animation showing the eyes moving through different directions.

### **Verification Reports**
Documents that prove all 17 tests passed, with measurements and hash values.

### **MANIFEST.json**
A special file that contains "digital fingerprints" (SHA-256 hashes) for every important file. This ensures that if anyone tries to change something, it can be detected.

## Important Notes for Non-Technical Users

### **This is Development Evidence, Not a Finished Product**
- The outputs are for verification and testing purposes
- They prove the eye tracking works correctly
- Actual XR submission would require additional steps not included here

### **Blender is Required**
- You need Blender 4.5.15 LTS installed
- There's also a secondary Blender 5.2.3 LTS for verification
- These are professional 3D creation tools

### **Everything is Documented**
- All measurements are recorded
- All tests results are logged
- All file hashes are tracked
- This ensures nothing changes secretly

### **Two Eye Modes Available**
- **Radial** (default): Enhanced, more detailed eye appearance
- **Flat** (optional): Original, simpler appearance - like switching between a detailed painting and a sketch

## Project Structure (High-Level Overview)

```
Apollo/
├── tasks.py          # The main recipe runner (15 different steps)
├── requirements.txt  # Python packages needed
├── tools/            # Helper scripts for various tasks
├── wrapper/          # Eye rendering functions
├── apollo_core/      # Core pipeline logic
├── assets/           # Character models and source files
├── docs/             # Documentation and reports
├── milestones/       # Major achievement checkpoints
├── tests/            # The 60 validation tests
├── build/            # Blender scripts
├── out/              # Generated outputs and reports
├── Dockerfile        # Container build definition (for advanced users)
└── FILEMAP.md        # Map of all the code files
```

## Summary

Apollo is a systematic way to ensure that XR headsets can accurately track where a user is looking. It:

1. **Sets up** a 3D character with eyes
2. **Tests** extensively (60 tests, 17 validation checks)
3. **Verifies** everything works correctly
4. **Documents** all results with measurements and hashes
5. **Preserves** evidence for review

The project has reached a mature state where all 17 validation checks pass consistently, and all results can be reproduced exactly - which is crucial for regulatory and quality assurance purposes in XR development.

**The development freeze from November 7, 2026** represents a polished, documented state of the project where all evidence is preserved and ready for review.

# dexdump

`dexdump` is a lightweight toolchain for dumping in-memory DEX files from Android apps with root access.  
It consists of 3 components: a minimal AOSP patch, a command line utility to trigger dumps, and a Python script to repair dumped DEX files.

---

## ✨ Features

- 🔧 **AOSP Patch**: Modifies `DexFile::Init()` to dump in-memory DEX when triggered.
- ⚙️ **`dexdump`**: Triggers the dump process by placing a flag file with correct ownership.
- 🛠️ **`fix_dex.py`**: Repairs broken DEX files by recalculating SHA-1 and Adler32 checksums.

---

## 📦 Components

### 1. AOSP Patch (`dexdump.patch`)
This patch injects logic into the ART runtime (`DexFile::Init`) to dump the in-memory DEX when a trigger file is found:

- Trigger path: `/data/data/<package_name>/files/dump.flag`
- Output: `/data/data/<package_name>/files/dump_<pid>_<ptr>_<timestamp>.dex`

**How to apply:**
```bash
# Navigate to the ART module
cd ~/aosp/android-15.0.0_r36/art

# Apply the patch
git apply /path/to/dexdump.patch
```

Then rebuild AOSP as usual.

### 2. dexdump.go
A Go-based command-line utility that creates the trigger file with correct UID/GID ownership based on the target app.

**Usage**
```bash
adb push dexdump /data/local/tmp/
adb shell su -c "/data/local/tmp/dexdump com.example.targetapp"
```

This will:

* Create /data/data/com.example.targetapp/files/ if missing
* Touch dump.flag
* Set UID/GID ownership to match the target app

**Build**
```bash
GOOS=android GOARCH=arm64 go build -o dexdump dexdump.go
```

### 3. fix_dex.py
A Python script to repair DEX files dumped from memory (which often have invalid checksums).

**Usage**
```bash
python fix_dex.py -f path/to/dump_*.dex
```

* By default, the original file will be deleted and replaced with the fixed one.
* Use -k to keep the original file.

---

## 🛡 Requirements

* Rooted Android device or emulator
* AOSP build environment
* Go for building the binary
* Python 3.0+ for fix_dex.py
package main

import (
	"fmt"
	"log"
	"os"
	"path/filepath"
	"syscall"
)

func main() {
	if len(os.Args) != 2 {
		log.Fatalf("Usage: %s <package_name>\n", os.Args[0])
	}
	pkgName := os.Args[1]
	basePath := filepath.Join("/data/data", pkgName)
	filesPath := filepath.Join(basePath, "files")
	dumpFlagPath := filepath.Join(filesPath, "dump.flag")

	// Step 1: Get UID/GID of the package owner
	var stat syscall.Stat_t
	err := syscall.Stat(basePath, &stat)
	if err != nil {
		log.Fatalf("Failed to stat %s: %v", basePath, err)
	}
	uid := int(stat.Uid)
	gid := int(stat.Gid)

	// Step 2: Create /data/data/<pkg>/files if not exists
	if _, err := os.Stat(filesPath); os.IsNotExist(err) {
		err := os.Mkdir(filesPath, 0755)
		if err != nil {
			log.Fatalf("Failed to create %s: %v", filesPath, err)
		}
	}

	// Step 3: Create dump.flag
	f, err := os.OpenFile(dumpFlagPath, os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Fatalf("Failed to create %s: %v", dumpFlagPath, err)
	}
	f.Close()

	// Step 4: chown files/ and dump.flag
	err = os.Chown(filesPath, uid, gid)
	if err != nil {
		log.Fatalf("Failed to chown %s: %v", filesPath, err)
	}
	err = os.Chown(dumpFlagPath, uid, gid)
	if err != nil {
		log.Fatalf("Failed to chown %s: %v", dumpFlagPath, err)
	}

	fmt.Printf("Successfully created %s and set ownership to UID:%d GID:%d\n", dumpFlagPath, uid, gid)
}

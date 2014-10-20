package main

import (
	"fmt"
	"strings"
	"testing"
)

func TestReadFile(t *testing.T) {
	file, err := Open("testcases/lines.txt")
	if err != nil {
		t.Errorf("Could not read test.txt\n")
	}
	lines := file.Lines()
	if len(lines) != 7 {
		t.Errorf("Expected testcases/lines.txt to have 7 lines, got %d\n", len(lines))
	}
	fmt.Println("ok: line count")
}

func TestReadFile2(t *testing.T) {
	file, err := Open("testcases/lines.txt")
	if err != nil {
		t.Errorf("Could not read test.txt\n")
	}
	lines := file.ContentLines()
	if len(lines) != 4 {
		t.Errorf("Expected testcases/lines.txt to have 4 lines with content, got %d\n", len(lines))
	}
	fmt.Println("ok: content count")
}

func TestNoNewline(t *testing.T) {
	file, err := Open("testcases/nonewline.txt")
	if err != nil {
		t.Errorf("Could not read nonewline.txt\n")
	}
	lines := file.Lines()
	lastline := lines[len(lines)-1]
	// Confirm that there is no newline at the end
	if strings.TrimSpace(lastline) != lastline {
		t.Errorf("Should not be a newline at the end of testcases/nonewline.txt!\n")
	}
	fmt.Println("ok: lines without newline")
}

func TestGetKey(t *testing.T) {
	file, err := Open("testcases/keyvalues.txt")
	if err != nil {
		t.Errorf("Could not read keyvalues.txt\n")
	}
	lineIndex, line := file.Get("y")
	if lineIndex != 6 {
		t.Errorf("Expected to find the y key at line 6 (counting from 0)\n")
	}
	if key := line.GetKey(); key != "y" {
		t.Errorf("Expected key to be \"y\", got %s\n", key)
	}
	if unmatched, _ := line.unmatched(); !unmatched {
		t.Errorf("Expected there to be an unmatched bracket at line 6.\n")
	}
	fmt.Println("ok: key in file")
}

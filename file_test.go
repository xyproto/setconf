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
	fmt.Println("Linecount ok")
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
	fmt.Println("Lines without newline ok")
}

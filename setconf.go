package main

import (
	"fmt"
	"strings"
	"errors"
)

const (
	VERSION = "0.5.4"
)

var (
	ASSIGNMENTS = []string{"==", "=>", "=", ":=", "::", ":"}
)

// Checks if a string exists in a list of strings
func stringin(s string, checkStrings []string) bool {
	for _, checkString := range checkStrings {
		if checkString == s {
			return true
		}
	}
	return false
}

// Checks if a substring exists in a string
func in(subs string, s string) bool {
	return strings.Contains(s, subs)
}

func splitNtimes(s string, delim string, ntimes int) []string {
	return strings.SplitN(s, delim, ntimes + 1)
}

func firstpart(line string, includingAssignment bool) (string, error) {
	stripline := strings.TrimSpace(line)
	if stripline == "" {
		return stripline, errors.New("no first part in given line")
	}
	if (stripline[0] == '#') || (stringin(stripline[0:2], []string{"//", "/*"})) {
		return stripline, errors.New("comment")
	}
	assignment := ""
	found := []string{}
	for _, ass := range ASSIGNMENTS {
		if in(ass, line) {
			found = append(found, ass)
		}
	}
	if len(found) == 1 {
		// Only one assignment found
		assignment = found[0]
	} else if len(found) > 1 {
		// If several assignments are found, use the first one
		firstpos := len(line)
		firstassignment := ""
		for _, ass := range found {
			pos := strings.Index(line, ass)
			if pos < firstpos {
				firstpos = pos
				firstassignment = ass
			}
		}
		assignment = firstassignment
	}
	if assignment != "" {
		if includingAssignment {
			return splitNtimes(line, assignment, 1)[0] + assignment, nil
		} else {
			return splitNtimes(line, assignment, 1)[0], nil
		}
	}
	// No assignments found
	return "", errors.New("no assignments found")
}

func changeline(line, newvalue string) string {
	first, err := firstpart(line, true)
	if err != nil {
		return line
	}
	// Fix, DRY and Go-style
	if in("= ", line) || in(": ", line) || in("> ", line) {
		return first + " " + newvalue
	} else if in("=\t", line) || in(":\t", line) || in(">\t", line) {
		return first + "\t" + newvalue
	} else {
		return first + newvalue
	}
}

func testChangeline() bool {
	passes := true
    passes = passes && changeline("rabbits = DUMB", "cool") == "rabbits = cool"
    passes = passes && changeline("for ever and ever : never", "and ever") == "for ever and ever : and ever"
    passes = passes && changeline("     for  ever  and  Ever   :=    beaver", "TURTLE") == "     for  ever  and  Ever   := TURTLE"
    passes = passes && changeline("CC=g++", "baffled") == "CC=baffled"
    passes = passes && changeline("CC =\t\tg++", "baffled") == "CC =\tbaffled"
    passes = passes && changeline("cabal ==1.2.3", "1.2.4") == "cabal ==1.2.4"
    passes = passes && changeline("TMPROOT=${TMPDIR:=/tmp}", "/nice/pants") == "TMPROOT=/nice/pants"
    passes = passes && changeline("    # ost = 2", "3") == "    # ost = 2"
    passes = passes && changeline(" // ost = 2", "3") == " // ost = 2"
    passes = passes && changeline("  ost = 2", "3") == "  ost = 3"
    passes = passes && changeline("   /* ost = 2 */", "3") == "   /* ost = 2 */"
    passes = passes && changeline("æøå =>\t123", "256") == "æøå =>\t256"
    fmt.Printf("Changeline passes: %v\n", passes)
    return passes
}

func change(lines, key, value string) {
	// TODO
}

func main() {
	fmt.Printf("result %v\n", testChangeline())
}

package main

import (
	"fmt"
	"testing"
)

func TestKeyValue(t *testing.T) {
	s := "x = 2"
	if ok, assignment := New(s).getAssignment(); ok && assignment != "=" {
		t.Errorf("Assignment should be =, but got %s!", assignment)
	}
	s = "x := 2"
	if ok, assignment := New(s).getAssignment(); ok && assignment != ":=" {
		t.Errorf("Assignment should be :=, but got %s!", assignment)
	}
	l := New(s)
	if l.GetKey() != "x" {
		t.Errorf("Key should be x, but is %s!", l.GetKey())
	}
	if l.GetValue() != "2" {
		t.Errorf("Value should be 2, but is %s!", l.GetValue())
	}
	l.SetKey("y")
	l.SetValue("7")
	if l.GetKey() != "y" {
		t.Errorf("Key should be y, but is %s!", l.GetKey())
	}
	if l.GetValue() != "7" {
		t.Errorf("Value should be 7, but is %s!", l.GetValue())
	}
	fmt.Println("key/value ok")
}

func TestComments(t *testing.T) {
	data := "# something-important: 999"
	l := New(data)
	if l.GetKey() != "something-important" {
		t.Errorf("Key should be something-important, but is %s!" + l.GetKey())
	}
	if l.GetValue() != "999" {
		t.Errorf("Key should be 999, but is %s!", l.GetValue())
	}
	if !l.IsCommented() {
		t.Errorf("Comment not detected for %s (%s)!", l.String(), data)
	}
	marker := l.Uncomment()
	if l.IsCommented() {
		t.Errorf("Comment not uncommented for %s (%s)!", l.String(), data)
	}
	l.ToggleComment(marker)
	if !l.IsCommented() {
		t.Errorf("Comment not toggled on again for %s (%s)!", l.String(), data)
	}
	if l.String() != data {
		t.Errorf("Could not rebuild line! %s != %s", l.String(), data)
	}
	fmt.Println("Comments ok")
}

func TestComment2(t *testing.T) {
	data := "    # ost = 2"
	l := New(data)
	if !l.IsCommented() {
		t.Errorf("Comment not detected! %s (%s)", l.String(), data)
	}
	fmt.Println("Ignoring comments ok")
}

// Change the value in a given line
func changeline(orig, newval string) string {
	shouldTrimKey := false
	shouldTrimValue := false
	minimumOneSpaceAfterKey := true    // only if trim is enabled
	minimumOneSpaceBeforeValue := true // only if trim is enabled
	ignoreLinesWithComments := true
	uncommentLines := false

	l := New(orig)
	//fmt.Println("COMMENTED?", l.IsCommented())
	if ignoreLinesWithComments && l.IsCommented() {
		return l.String()
	}
	l.SetValue(newval)
	if shouldTrimKey {
		l.TrimKey(minimumOneSpaceAfterKey)
	}
	if shouldTrimValue {
		l.TrimValue(minimumOneSpaceBeforeValue)
	}
	if uncommentLines {
		l.Uncomment()
	}
	return l.String()
}

func TestChangeline(t *testing.T) {
	changeline_testdata := [][]string{
		[]string{"rabbits = DUMB", "cool", "rabbits = cool"},
		[]string{"for ever and ever : never", "and ever", "for ever and ever : and ever"},
		[]string{"     for  ever  and  Ever   :=    beaver", "TURTLE", "     for  ever  and  Ever   :=    TURTLE"},
		[]string{"CC=g++", "baffled", "CC=baffled"},
		[]string{"CC =\t\tg++", "baffled", "CC =\t\tbaffled"},
		[]string{"cabal ==1.2.3", "1.2.4", "cabal ==1.2.4"},
		[]string{"TMPROOT=${TMPDIR:=/tmp}", "/nice/pants", "TMPROOT=/nice/pants"},
		[]string{"    # ost = 2", "3", "    # ost = 2"},
		[]string{" // ost = 2", "3", " // ost = 2"},
		[]string{"  ost = 2", "3", "  ost = 3"},
		[]string{"   /* ost = 2 */", "3", "   /* ost = 2 */"},
		[]string{"æøå =>\t123", "256", "æøå =>\t256"},
	}

	for index, testdata := range changeline_testdata {
		orig := testdata[0]
		newval := testdata[1]
		changed := testdata[2]

		if result := changeline(orig, newval); result != changed {
			t.Errorf("Could not change from:\n\t%s\n\tto\n\t%s\n\twith new value\n\t%s\n\tgot\n\t%s\n", orig, changed, newval, result)
			break
		} else {
			fmt.Printf("%.2d ok: %s\n", index, changed)
		}
	}
	fmt.Println("Changeline ok")
}

func TestUnmatched(t *testing.T) {
	s := "// this was a fine day and also x=2 { blabla"
	l := New(s)
	missing, missingString := l.unmatched()
	curly := "}"
	if (!missing) || (missingString != curly) {
		t.Errorf("Could not catch that the missing string was a \"%s\", got: %s.\n", curly, missingString)
	}
	fmt.Println("Matching curly brace ok")
}

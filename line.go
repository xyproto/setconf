package main

import (
	"log"
	"strings"
)

// Need to be given a line and be able to identify:
//    assignment operator, if present (and handle := not just =)
//    key, if present
//    value, if present
//    comments, if present
//    open parantheses or quotes, if present

var (
	assignments     = []string{"==", "=>", ":=", "=", "::", ":"}
	defineprefixes  = []string{"#define"}
	commentprefixes = []string{"//", "/*", "#", "--", "\" ", "rem ", "*"} // it's unlikely that lines that are not commented out starts with *
	matchingPairs   = map[string]string{
		"{": "}",
		"(": ")",
		"[": "]",
	}
	multilineCommentStart = []string{"/*", "(*"}
	multilineCommentEnd   = []string{"*/", "*)"}
	newlines              = []string{"\n", "\r", "\r\n"}
)

const (
	blank = " "
)

type Line struct {
	data string

	// These are stored internally, to be able to rebuild the line
	keyWithWhitespace   string
	assignment          string
	valueWithWhitespace string

	// Should the whitespace be trimmed from the key?
	trimKey bool
	// Should the whitespace be trimmed from the value?
	trimValue bool

	// Should there be a minimum of one space after the key, before the assignment?
	minimumOneSpaceAfterKey bool
	// Should there be a minimum of one space before the value, after the assignment?
	minimumOneSpaceBeforeValue bool
}

func New(data string) *Line {
	if has(data, newlines) {
		log.Fatalln("Line must not contain a newline! " + data)
	}
	l := new(Line)
	l.data = data

	// Gather the needed data to be able to rebuild the string later.
	// If one or more of the parts are blank, the rebuilding should still work.
	if ok, val := l.getKeyWithWhitespace(); ok {
		l.keyWithWhitespace = val
	}
	if ok, assignment := l.getAssignment(); ok {
		l.assignment = assignment
	}
	if ok, val := l.getValueWithWhitespace(); ok {
		l.valueWithWhitespace = val
	}

	return l
}

// Should the whitespace be trimmed from the key?
// Should one whitespace character be kept between the key and the assignment?
// (will use " " if no whitespace were present)
func (line *Line) TrimKey(minimumOneSpace bool) {
	line.trimKey = true
	line.minimumOneSpaceAfterKey = minimumOneSpace
}

// Should the whitespace be trimmed from the value?
// Should a minimum of one whitespace character be kept between the assignment and the value?
// (will use " " if no whitespace were present)
func (line *Line) TrimValue(minimumOneSpace bool) {
	line.trimValue = true
	line.minimumOneSpaceBeforeValue = minimumOneSpace
}

func (line *Line) getAssignment() (bool, string) {
	// To hold the positions of the assignments in the string
	apos := make(map[int]string)
	var assignment string
	// Go through the assignments in reverse order, to catch the shortest first
	// and then the longest, since the position can be overwritten in the apos map.
	for i := len(assignments) - 1; i >= 0; i-- {
		assignment = assignments[i]
		if pos := strings.Index(line.data, assignment); pos != -1 {
			apos[pos] = assignment
		}
	}
	// If one were found, find the first one on the line
	if len(apos) >= 0 {
		// find the first position
		first := len(line.data)
		for key, _ := range apos {
			if key < first {
				first = key
			}
		}
		return true, apos[first]
	}
	// If not, check if the line starts with "#define" or similar
	// TODO: Might need to handle this differently, add a test related to "#define".
	return prefix(line.data, defineprefixes)
}

func (line *Line) hasAssignment() bool {
	ok, _ := line.getAssignment()
	return ok
}

// Check if there are unmatched (, [ or { in the line.
// Also check for unmatched double or single quotes.
// Returns true and the missing right side string if the line is unbalanced.
// Does not return the number of missing right side strings, there may be several.
func (line *Line) unmatched() (bool, string) {
	for left, right := range matchingPairs {
		// Check if the line has an unmatched parenthesis or bracket
		if strings.Count(line.data, left) > strings.Count(line.data, right) {
			return true, right
		}
	}
	// Check for unmatched quotes
	if strings.Count(line.data, "'")%2 != 0 { // odd number of single quotes
		return true, "'"
	}
	if strings.Count(line.data, "\"")%2 != 0 { // odd number of double quotes
		return true, "\""
	}
	return false, ""
}

// Only checks the start of the line.
func (line *Line) startsMultilineComment() bool {
	return hasPrefix(line.data, multilineCommentStart)
}

// Only checks the end of the line.
func (line *Line) endsMultilineComment() bool {
	return hasSuffix(line.data, multilineCommentEnd)
}

func (line *Line) getKeyWithWhitespace() (bool, string) {
	ok, assignment := line.getAssignment()
	if !ok {
		return false, ""
	}
	// pos can not be -1 here, because we know it exists
	pos := strings.Index(line.data, assignment)

	return true, line.data[:pos]
}

func (line *Line) GetKey() string {
	unpolishedKey := line.keyWithWhitespace
	if hasComment, commentPrefix := prefix(unpolishedKey, commentprefixes); hasComment {
		return strings.TrimSpace(removePrefix(unpolishedKey, commentPrefix))
	}
	return strings.TrimSpace(line.keyWithWhitespace)
}

func (line *Line) getValueWithWhitespace() (bool, string) {
	ok, assignment := line.getAssignment()
	if !ok {
		return false, ""
	}
	// pos can not be -1 here, because we know it exists
	pos := strings.Index(line.data, assignment)

	return true, line.data[pos+len(assignment):]
}

func (line *Line) GetValue() string {
	return strings.TrimSpace(line.valueWithWhitespace)
}

func (line *Line) SetKey(newkey string) {
	line.keyWithWhitespace = strings.Replace(line.keyWithWhitespace, line.GetKey(), newkey, 1)
}

func (line *Line) SetValue(newvalue string) {
	line.valueWithWhitespace = strings.Replace(line.valueWithWhitespace, line.GetValue(), newvalue, 1)
}

func (line *Line) CommentMarker() (bool, string) {
	return prefix(line.keyWithWhitespace, commentprefixes)
}

func (line *Line) IsCommented() bool {
	hasComment, _ := line.CommentMarker()
	return hasComment
}

func (line *Line) ToggleComment(commentMarker string) {
	if line.IsCommented() {
		line.keyWithWhitespace = removePrefix(line.keyWithWhitespace, commentMarker)
	} else {
		line.keyWithWhitespace = commentMarker + line.keyWithWhitespace
		// if not commentMarker is in the list of comment prefixes, add it
		if !in(commentprefixes, commentMarker) {
			commentprefixes = append(commentprefixes, commentMarker)
		}
	}
}

// Uncomment known types of single line comments.
// Return the string that was removed, or a blank string if no comment was removed.
func (line *Line) Uncomment() string {
	hasComment, commentMarker := line.CommentMarker()
	if !hasComment {
		return ""
	}
	line.ToggleComment(commentMarker)
	return commentMarker
}

// Rebuild the line
func (line *Line) String() string {
	key := line.keyWithWhitespace
	// Trim all the space away from the key, if trimKey is set
	if line.trimKey {
		oneWhitespace := ""
		// Add one character of the same type of whitespace as is already present,
		// or a single space character, if minimumOneSpaceAfterKey is set.
		if line.minimumOneSpaceAfterKey {
			oneWhitespace = lastWhitespace(key)
			if oneWhitespace == "" {
				oneWhitespace = blank // a single space
			}
		}
		// Keep last in this block
		key = strings.TrimSpace(key) + oneWhitespace
	}
	// Trim all the space away from the value, if trimValue is set
	value := line.valueWithWhitespace
	if line.trimValue {
		oneWhitespace := ""
		// Add one character of the same type of whitespace as is already present,
		// or a single space character, if minimumOneSpaceBeforeValue is set.
		if line.minimumOneSpaceBeforeValue {
			oneWhitespace = firstWhitespace(value)
			if oneWhitespace == "" {
				oneWhitespace = blank // a single space
			}
		}
		// Keep last in this block
		value = oneWhitespace + strings.TrimSpace(value)
	}
	return key + line.assignment + value
}

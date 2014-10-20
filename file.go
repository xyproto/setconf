package main

import (
	"bytes"
	"errors"
	"io/ioutil"
	"strings"
)

type File struct {
	// The entire contents
	data []byte
	// The filename, if any
	filename string
}

// Open a file, return a *File with the data and filename
func Open(filename string) (*File, error) {
	b, err := ioutil.ReadFile(filename)
	return &File{b, filename}, err
}

// Intialize a new *File manually
func NewFile(data string) *File {
	return &File{[]byte(data), ""}
}

// Create a new blank bytes.Buffer
func blankBuffer() (buf bytes.Buffer) {
	return // buf
}

// Get the lines as a slice of strings
func (f *File) Strings() (lines []string) {
	const newlinesAsSeparateLines = false
	var (
		lineBuilder bytes.Buffer
		lineIndex   int
	)
	for _, r := range f.data {
		if in(Newlines, string(r)) {
			if !newlinesAsSeparateLines {
				// Add the newline at the end of the line
				lineBuilder.Write([]byte{r})
			}
			// Store this line, if it has any contents
			lines = append(lines, lineBuilder.String())
			if newlinesAsSeparateLines {
				// Store the newline
				lines = append(lines, string(r))
			}
			// Prepare for the next line
			lineIndex++
			lineBuilder = blankBuffer() //*bytes.NewBuffer([]byte{})
		} else {
			lineBuilder.Write([]byte{r})
		}
	}
	// Store the final line, if lineBuilder has changed since last append
	if lineBuilder.String() != "" {
		lines = append(lines, lineBuilder.String())
	}
	return // lines
}

// Get the lines as pointers to Line structs
func (f *File) Lines() (lines []*Line) {
	var (
		lineBuilder bytes.Buffer
		lineIndex   int
	)
	for _, r := range f.data {
		if in(Newlines, string(r)) {
			// Add the newline at the end of the line
			lineBuilder.Write([]byte{r})
			// Store this line, if it has any contents
			lines = append(lines, New(lineBuilder.String()))
			// Prepare for the next line
			lineIndex++
			lineBuilder = blankBuffer() //*bytes.NewBuffer([]byte{})
		} else {
			lineBuilder.Write([]byte{r})
		}
	}
	// Store the final line, if lineBuilder has changed since last append
	if lineBuilder.String() != "" {
		lines = append(lines, New(lineBuilder.String()))
	}
	return // lines
}

// Only return lines that has contents
func (f *File) ContentLines() []string {
	return filterS(nonempty, mapS(strings.TrimSpace, f.Strings()))
}

// Set the filename if the contents were initialized without reading from a file
func (f *File) SetFilename(filename string) {
	f.filename = filename
}

// Write the contents to f.filename
func (f *File) Write() error {
	if f.filename == "" {
		return errors.New("Set a filename with SetFilename before writing")
	}
	return ioutil.WriteFile(f.filename, f.data, 0666)
}

// Find the line that starts declaring a specific key
// lineIndex is -1 if not found
// returns trimmed line contents in line!
func (f *File) Get(key string) (int, *Line) {
	for lineNumber, line := range f.Lines() {
		if line.GetKey() == key {
			return lineNumber, line
		}
	}
	return -1, New("")
}

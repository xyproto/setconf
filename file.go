package main

import "io/ioutil"

type File struct {
	data string
}

func NewFile(data string) *File {
	return &File{data}
}

func Open(filename string) (*File, error) {
	b, err := ioutil.ReadFile(filename)
	return &File{string(b)}, err
}

func (f *File) Lines() (lines []string) {
	var (
		lineBuilder string
		lineIndex   int
	)
	for _, r := range f.data {
		if in(Newlines, string(r)) {
			// Add the newline at the end of the line
			lineBuilder += string(r)
			// Store this line
			lines = append(lines, lineBuilder)
			// Prepare for the next line
			lineIndex++
			lineBuilder = ""
		} else {
			lineBuilder += string(r)
		}
	}
	// Store the final line, if lineBuilder has changed since last append
	if lineBuilder != "" {
		lines = append(lines, lineBuilder)
	}
	return // lines
}

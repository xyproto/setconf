package main

import (
	"errors"
	"io/ioutil"
)

func createIfMissing(filename string) error {
	// If the file can not be read
	if _, err := ioutil.ReadFile(filename); err != nil {
		// Create the file, return the error
		return ioutil.WriteFile(filename, []byte{}, 0666)
	}
	return errors.New("File " + filename + " already exists")
}

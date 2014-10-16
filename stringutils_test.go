package main

import "testing"

func TestSuffix(t *testing.T) {
	const result = "hei på   "
	s := "hei på deg  "
	s2 := removeSuffix(s, "deg")
	if s2 != result {
		t.Errorf("Expected %s got %s.\n", result, s2)
	}
}

package main

import (
	"log"
	"strings"
	"unicode"
)

// Check if a given string contains one of the given strings.
// Returns true if it was found, together with the string that was found.
func contains(data string, xs []string) (bool, string) {
	for _, x := range xs {
		if strings.Contains(data, x) {
			return true, x
		}
	}
	return false, ""
}

// Check if a given string contains one of the given strings
func has(data string, xs []string) bool {
	ok, _ := contains(data, xs)
	return ok
}

// Check if a given string contains one of the given strings.
// Returns the string that was found, or "".
func get(data string, xs []string) string {
	_, s := contains(data, xs)
	return s
}

// Check if the string (disregarding whitespace) starts with one of the given strings
func prefix(data string, xs []string) (bool, string) {
	for _, x := range xs {
		if strings.HasPrefix(strings.TrimSpace(data), x) {
			return true, x
		}
	}
	return false, ""
}

// Check if the string (disregarding whitespace) starts with one of the given strings
func hasPrefix(data string, xs []string) bool {
	ok, _ := prefix(data, xs)
	return ok
}

// Given a string and a list of strings, return the first string that is at
// the beginning of the given string, disregarding whitespace.
func getPrefix(data string, xs []string) string {
	_, s := prefix(data, xs)
	return s
}

// Given a string and a prefix, remove the first occurence of the prefix.
// Returns the new string if it works out.
// The string must have len(s) > 0!
func removePrefix(s, p string) string {
	if strings.Contains(s, p) {
		return strings.Replace(s, p, "", 1)
	}
	log.Fatalln("Prefix not found in string!")
	return s
}

// Check if the string (disregarding whitespace) starts with one of the given strings
func suffix(data string, xs []string) (bool, string) {
	for _, x := range xs {
		if strings.HasSuffix(strings.TrimSpace(data), x) {
			return true, x
		}
	}
	return false, ""
}

// Check if the string (disregarding whitespace) starts with one of the given strings
func hasSuffix(data string, xs []string) bool {
	ok, _ := suffix(data, xs)
	return ok
}

// Given a string and a list of strings, return the first string that is at
// the beginning of the given string, disregarding whitespace.
func getSuffix(data string, xs []string) string {
	_, s := suffix(data, xs)
	return s
}

// Given a string and a prefix, remove the first occurence of the prefix.
// Returns the new string if it works out.
// The string must have len(s) > 0!
func removeSuffix(s, p string) string {
	lastpos := strings.LastIndex(s, p)
	if lastpos == -1 {
		log.Fatalln("Suffix not found in string!")
		return s
	}
	return s[:lastpos] + s[lastpos+len(p):]
}

// For a given list of strings, check if the given string is one of them
func in(xs []string, x string) bool {
	for _, e := range xs {
		if e == x {
			return true
		}
	}
	return false
}

// Return the last rune of a string
func lastRune(s string) (last rune) {
	if len(s) == 0 {
		log.Fatalln("Can't find last rune of an empty string")
	}
	// To make sure to get the last Rune, not only the last byte
	for _, letter := range s {
		last = letter
	}
	return // last
}

// Return the first rune of a string
func firstRune(s string) (first rune) {
	// To make sure to get the first Rune, not only the first byte
	for _, letter := range s {
		return letter
	}
	log.Fatalln("Can't find first rune of an empty string")
	return // first
}

// Return the last whitespace character in a string, or blank
func lastWhitespace(s string) string {
	oneWhitespace := ""
	if len(s) > 0 {
		last := lastRune(s)
		if unicode.IsSpace(last) {
			oneWhitespace = string(last)
		}
	}
	return oneWhitespace
}

// Return the first whitespace character in a string, or blank
func firstWhitespace(s string) string {
	oneWhitespace := ""
	if len(s) > 0 {
		first := firstRune(s)
		if unicode.IsSpace(first) {
			oneWhitespace = string(first)
		}
	}
	return oneWhitespace
}

package main

import "fmt"

func main() {
	l := New("x := 2")
	fmt.Println(l.GetKey())
}

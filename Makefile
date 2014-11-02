CPPFLAGS=-std=c++11 -g -Wall

all: {{ targets|join:" " }}

tester.o: tester.cpp
	g++ -c $(CPPFLAGS) $^ -o $@

custom_tests.o: custom_tests.cpp
	g++ -c $(CPPFLAGS) $^ -o $@

%: %.cpp tester.o custom_tests.o
	g++ -pipe $(CPPFLAGS) $^ -o $@

%o: %.cpp tester.o custom_tests.o
	g++ -pipe $(CPPFLAGS) $^ -o $@

clean:
	rm {{ targets|join:" " }} *.o



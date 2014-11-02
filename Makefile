
all: {{ targets|join:" " }}

tester.o: tester.cpp
	g++ -c -std=c++11 -g -O2 $^ -o $@

custom_tests.o: custom_tests.cpp
	g++ -c -std=c++11 -g -O2 $^ -o $@

%: %.cpp tester.o custom_tests.o
	g++ -pipe -std=c++11 -g $^ -o $@

%o: %.cpp tester.o custom_tests.o
	g++ -pipe -std=c++11 -O2 -g $^ -o $@

clean:
	rm {{ targets|join:" " }} *.o



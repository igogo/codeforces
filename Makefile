
all: A B C D E

tester.o: tester.cpp
	g++ -c -std=c++11 -g -O2 $^ -o $@

custom_tests.o: custom_tests.cpp
	g++ -c -std=c++11 -g -O2 $^ -o $@

%: %.cpp tester.o custom_tests.o
	g++ -pipe -std=c++11 -g $^ -o $@

%o: %.cpp tester.o custom_tests.o
	g++ -pipe -std=c++11 -O3 -g $^ -o $@

clean:
	rm A B C D E F *.o



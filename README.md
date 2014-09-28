# Codeforces Testing Environment

Simple workplace to perform autotesting for contests on [Codeforces](http://codeforces.com).
By default a project for QtCreator is created to simplify coding.

# How to Use
1. Run `grabtests.py <contest_url>`.
2. Copy the last printed line and run it.

That's it, now you can write your code and test it against standard tests.
To switch between problems, open the source file and press Ctrl+T to select an appropriate target.
You can add add custom tests to `custom_tests.cpp`.

If you don't want to use QtCreator, you still can run tests using a command like `make && ./A`.

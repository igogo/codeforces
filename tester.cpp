#include <dirent.h>
#include <cstdio>
#include <ctime>
#include <cstring>
#include <string>
#include <vector>
#include <iostream>
#include <algorithm>
#include <sstream>
#include <fstream>
#include <map>
#include <unistd.h>

const char *tests_dir = "tests/";
const char *diff_cmd = "diff -Z -b";

using namespace std;

vector<string> get_inputs(string problem)
{
    string path = string(tests_dir) + problem;
    vector<string> result;
    DIR *dir = opendir(path.c_str());
    if (!dir)
        return result;
    dirent *file;
    while ((file = readdir(dir)) != NULL) {
        if (file->d_name[0] == 'i')
            result.push_back(string(file->d_name));
    }
    sort(result.begin(), result.end());
    closedir(dir);
    return result;
}

int call_diff(string file1, string file2)
{
    ostringstream ss;
    ss << diff_cmd << " " << file1 << " " << file2 << " >/dev/null";
    string cmd = ss.str();
    int ret = system(cmd.c_str());
    if (ret < 0) {
        cerr << "!! Error in calling diff! Testing result is invalid!\n";
        return 0;
    }
    return WEXITSTATUS(ret);
}

vector<string> get_head(string file, int maxnlines)
{
    vector<string> result;
    const int BUFLEN = 1024 * 1024;
    static char buf[BUFLEN];
    FILE *f = fopen(file.c_str(), "r");
    if (!f) {
        cerr << "!! Failed to open a file '" << file << "'\n";
        return result;
    }
    bool truncated = true;
    for (int i = 0; i < maxnlines; i++) {
        if (fgets(buf, BUFLEN, f) == NULL) {
            truncated = false;
            break;
        }
        int len = strlen(buf);
        while (isspace(buf[len-1]))
            len--;
        buf[len] = 0;
        result.push_back(string(buf));
    }
    if (truncated) {
        result.push_back("...");
    }
    else {
        while (!result.empty() && result.back().empty())
            result.pop_back();
    }
    fclose(f);
    return result;
}

void run(void (*solve)(), string ipath, string tempopath, string opath, double* elapsed_ms)
{
    cin.clear();
    cout.clear();
    if (freopen(ipath.c_str(), "r", stdin) == NULL)
        cerr << "!! ERROR REOPENING ipath \n";
    if (freopen(tempopath.c_str(), "w", stdout) == NULL)
        cerr << "!! ERROR REOPENING tempopath \n";

    clock_t c_start = std::clock();
    solve();
    clock_t c_end = std::clock();
    *elapsed_ms = 1000.0 * (c_end - c_start) / CLOCKS_PER_SEC;

    freopen("/dev/tty", "a", stdout);
    freopen("/dev/tty", "r", stdin);
}

void diff_files(int tstnum, string ipath, string tempopath, string opath, double elapsed_ms)
{
    int diff_result = call_diff(opath, tempopath);
    if (diff_result == 0) {
        cerr << "Test " << tstnum << "  OK\n";
        cerr << "Elapsed: " << elapsed_ms << "ms\n";
    }
    else {
        cerr << "\n";
        cerr << "Test " << tstnum << "  FAILED\n";
        cerr << "Elapsed: " << elapsed_ms << "ms\n";
        cerr << "Input:\n";
        vector<string> ihead = get_head(ipath, 30);
        for (int i = 0; i < ihead.size(); i++)
            cerr << "  " << ihead[i] << "\n";
        cerr << "Expected:\n";
        vector<string> ohead = get_head(opath, 30);
        for (int i = 0; i < ohead.size(); i++)
            cerr << "  " << ohead[i] << "\n";
        cerr << "Received:\n";
        vector<string> temphead = get_head(tempopath, 30);
        for (int i = 0; i < temphead.size(); i++)
            cerr << "  " << temphead[i] << "\n";
    }
}

void test_file(void (*solve)(), string problem, string file)
{
    string path = string(tests_dir) + problem + string("/");
    string ipath = path + file;
    string opath = path + file.replace(0, 1, "o");
    string tempopath = string(tests_dir) + "output.txt";

    double elapsed_ms;
    run(solve, ipath, tempopath, opath, &elapsed_ms);
    diff_files(atoi(file.substr(1).c_str()), ipath, tempopath, opath, elapsed_ms);
}

void test_custom(void (*solve)(), int tstnum, string input, string output)
{
    string ipath = string(tests_dir) + "input.txt";
    string opath = string(tests_dir) + "right_answer.txt";
    string tempopath = string(tests_dir) + "output.txt";

    ofstream geninput(ipath);
    geninput << input;
    geninput.close();

    ofstream genrightans(opath);
    genrightans << output;
    genrightans.close();

    double elapsed_ms;
    run(solve, ipath, tempopath, opath, &elapsed_ms);
    diff_files(tstnum, ipath, tempopath, opath, elapsed_ms);
}

vector<pair<string, string> > get_custom_tests(string problem);

void perform_testing(void (*solve)(), string problem, int itest)
{
    vector<string> inputs = get_inputs(problem);
    vector<pair<string, string> > custom_tests = get_custom_tests(problem);
    if (itest == -1) {
        for (int i = 0; i < inputs.size(); i++)
            test_file(solve, problem, inputs[i]);
        for (int i = 0; i < custom_tests.size(); i++)
            test_custom(solve, inputs.size() + i, custom_tests[i].first, custom_tests[i].second);
    }
    else {
        if (itest < inputs.size())
            test_file(solve, problem, inputs[itest]);
        itest -= inputs.size();
        if (itest < custom_tests.size())
            test_custom(solve, inputs.size() + itest, custom_tests[itest].first, custom_tests[itest].second);
    }
}

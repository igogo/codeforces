#!/usr/bin/env python
'''
Usage:
Run this program in one of following ways
./grabtests.py http://codeforces.ru/contest/356/problem/A
./grabtests.py http://codeforces.ru/contest/356
./grabtests.py gym/356 (oops this needs cookies and thus doesn't work)
./grabtests.py 356
'''

# FIXME: this doesn't work with gym because the login is required for that...

import BeautifulSoup
import urllib2
import sys, re, os

codeforces_url = 'http://codeforces.ru'
tests_dir = 'tests'

def parse_arg(arg):
    if arg.startswith(codeforces_url):
        cut_url = re.sub(r'^' + re.escape(codeforces_url), '', arg.strip())
        cut_problem = re.sub(r'/problem/[A-Z][0-9]?$', '', cut_url)
        return cut_problem
    if arg.isdigit():
        return '/contest/' + arg
    if re.search(r'\d+$', arg) and not arg.startswith(codeforces_url):
        return '/' + arg
    raise Exception('Failed to parse arg \'' + arg + '\'\n')

def get_most_recent_contest_url():
    soup = BeautifulSoup.BeautifulSoup(urllib2.urlopen(codeforces_url + '/contests').read())
    for contest in soup.findAll(lambda tag: 'data-contestid' in dict(tag.attrs)):
        links = [a['href'] for a in contest.findAll('a') if re.search(r'/contest/[0-9]+$', a['href'])]
        if len(links) == 1:
            return links[0]
    raise Exception('couldn\'t find last contest')

def get_problems(addr):
    url = codeforces_url + addr
    print '=== downloading ' + url + ' ==='
    soup = BeautifulSoup.BeautifulSoup(urllib2.urlopen(url).read())
    problemsbox = soup.findAll('table', 'problems')
    assert len(problemsbox) == 1, 'couldn\'t locate a list of links to problems'
    problemsbox = problemsbox[0]
    problems = sorted(set(a['href'] for a in problemsbox.findAll('a') if '/problem/' in a['href']))
    assert len(problems) >= 1, 'couldn\'t locate any problems'
    print 'Found', len(problems), 'problems'
    return problems

def html2plaintext(tag):
    result = ''
    for c in tag.contents:
        if isinstance(c, BeautifulSoup.NavigableString):
            result += str(c)
        if isinstance(c, BeautifulSoup.Tag):
            if c.name == 'br':
                result += '\n'
            else:
                raise Exception('unknown tag inside test case found: ' + c.name)
    return result

def download(problem):
    print '=== problem ' + extract_letter(problem) + ' ==='
    soup = BeautifulSoup.BeautifulSoup(urllib2.urlopen(codeforces_url + problem).read())
    tests = soup.findAll('div', 'sample-test')
    assert len(tests) == 1, 'sample-tests div was expected to be single'
    tests = tests[0]
    inputs = [i.pre for i in tests.findAll('div', 'input')]
    outputs = [o.pre for o in tests.findAll('div', 'output')]
    assert len(inputs) == len(outputs) >= 1, 'error in parsing inputs and outputs'
    print 'Found', len(inputs), 'tests'
    results = []
    for i, o in zip(inputs, outputs):
        results.append((html2plaintext(i), html2plaintext(o)))
    return results

def save(letter, tests):
    directory = os.path.join(tests_dir, letter)
    try:
        os.makedirs(directory)
    except OSError:
        for f in os.listdir(directory):
            os.remove(os.path.join(directory, f))
    for itest, (inp, out) in enumerate(tests):
        finame = os.path.join(directory, 'i%02d' % itest)
        with open(finame, 'w') as fi:
            fi.write(inp)
        foname = os.path.join(directory, 'o%02d' % itest)
        with open(foname, 'w') as fo:
            fo.write(out)

def extract_letter(problem):
    m = re.search(r'/([A-Z][0-9]?)$', problem.strip())
    if m:
        return m.group(1)
    else:
        raise Exception('failed to extract problem letter from its address')

if __name__ == '__main__':
    if len(sys.argv) > 2:
        raise Exception('Supply URL or contest number')
    if len(sys.argv) == 2:
        addr = parse_arg(sys.argv[1])
    else:
        addr = get_most_recent_contest_url()
    for problem in get_problems(addr):
        tests = download(problem)
        save(extract_letter(problem), tests)

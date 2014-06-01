#!/usr/bin/env python
'''
Usage:
Run this program in one of following ways
./grabtests.py http://codeforces.com/contest/356/problem/A
./grabtests.py http://codeforces.com/contest/356
./grabtests.py gym/356 (oops this needs cookies and thus doesn't work)
./grabtests.py 356
'''

# FIXME: this doesn't work with gym because the login is required for that...

import BeautifulSoup
import urllib2, socket
import sys, re, os
from htmlentitydefs import entitydefs
import argparse

codeforces_domain = 'codeforces.com'
tests_dir = 'tests'

def get_contest_from_arg(arg):
    m = re.match(r'(http://)?(codeforces\.com|codeforces\.ru)/(?P<contest>\w*/\d*)/.*', arg)
    if m:
        return '/' + m.group('contest')
    if arg.isdigit():
        return '/contest/' + arg
    if re.search(r'\d+$', arg):
        return '/' + arg
    raise Exception('Failed to parse arg \'' + arg + '\'\n')

def download(path):
    ''' codeforces.com sometimes resolves to ipv6 address which doesn't work, so we'll force manually '''
    host = socket.gethostbyname(codeforces_domain)
    request = urllib2.Request('http://' + host + path, headers={'Host': codeforces_domain})
    return urllib2.urlopen(request).read()

def get_most_recent_contest_url():
    soup = BeautifulSoup.BeautifulSoup(download('/contests'))
    for contest in soup.findAll(lambda tag: 'data-contestid' in dict(tag.attrs)):
        links = [a['href'] for a in contest.findAll('a') if re.search(r'/contest/[0-9]+$', a['href'])]
        if len(links) == 1:
            return links[0]
    raise Exception('couldn\'t find last contest')

def get_problems(path):
    print '=== downloading ' + path + ' ==='
    soup = BeautifulSoup.BeautifulSoup(download(path))
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
            result += replace_html_specials(str(c))
        if isinstance(c, BeautifulSoup.Tag):
            if c.name == 'br':
                result += '\n'
            else:
                raise Exception('unknown tag inside test case found: ' + c.name)
    return result

def replace_html_specials(s):
    return re.sub(r'&(\w+);', lambda x: entitydefs[x.group(1)], s)

def download_problem(problem):
    print '=== problem ' + extract_letter(problem) + ' ==='
    soup = BeautifulSoup.BeautifulSoup(download(problem))
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
    parser = argparse.ArgumentParser(description='Download pretests from codeforces website',
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('contest', type=str, nargs='?',
                        help=('which contest to download\n'
                              'examples:\n'
                              '\t416\n'
                              '\tcontest/416\n'
                              '\thttp://codeforces.com/contest/416/problem/A\n'
                              'by default, the last contest is downloaded')
                       )
    args = parser.parse_args()
    if args.contest is not None:
        addr = get_contest_from_arg(args.contest)
    else:
        addr = get_most_recent_contest_url()
    for problem in get_problems(addr):
        tests = download_problem(problem)
        save(extract_letter(problem), tests)

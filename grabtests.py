#!/usr/bin/env python

from htmlentitydefs import entitydefs
import argparse
import BeautifulSoup
import os
import re
import socket
import urllib2

import path


codeforces_domain = 'codeforces.com'
tests_dir = 'tests'


def extract_contest_id(url):
    m = re.match(r'(http://)?(codeforces\.com|codeforces\.ru)/(?P<contest>\w*/\d*)(?:/|$)', url)
    if m:
        return '/' + m.group('contest')


def get_contest_from_arg(arg):
    if arg.startswith("http://"):
        contest_id = extract_contest_id(arg)
        if contest_id is not None:
            return contest_id
        else:
            raise Exception("Failed to parse url: %s" % arg)
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


def copy_substitute(src, dst, **substitutions):
    with open(src) as stream:
        data = stream.read()
    for key, value in substitutions.iteritems():
        data = data.replace("$$" + key + "$$", value)
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    with open(dst, "w") as stream:
        stream.write(data)


def save(contest_dir, letter, tests, solution_template):
    test_directory = path.path(contest_dir) / tests_dir / letter
    if test_directory.exists():
        print("Tests for %s already exist, skip" % letter)
    else:
        test_directory.makedirs()

        for itest, (inp, out) in enumerate(tests):
            finame = test_directory / ('i%02d' % itest)
            with open(finame, 'w') as fi:
                fi.write(inp)
            foname = test_directory / ('o%02d' % itest)
            with open(foname, 'w') as fo:
                fo.write(out)

    solution_fpath = contest_dir / (letter + ".cpp")
    if solution_fpath.exists():
        print("Solution file for %s already exist, skip" % letter)
    else:
        with open(solution_fpath, "w") as stream:
            stream.write(solution_template.replace("$$PROBLEM_LETTER$$", letter))


def extract_letter(problem):
    m = re.search(r'/([A-Z][0-9]?)$', problem.strip())
    if m:
        return m.group(1)
    else:
        raise RuntimeError('failed to extract problem letter from its address')


def main(contest, base_dir, force):
    if contest is not None:
        contest_id = get_contest_from_arg(contest)
    else:
        contest_id = get_most_recent_contest_url()

    # run this ASAP to verify whether contest_id is valid
    problems = get_problems(contest_id)
    problem_letters = [x.split("/")[-1] for x in problems]

    script_dir = path.path(__file__).dirname().abspath()
    contest_slug = contest_id.strip("/").replace("/", "_")
    contest_dir = path.path(base_dir) / contest_slug
    contest_dir.makedirs_p()
    print "Saving to", contest_dir

    with open(script_dir / "template.cpp") as stream:
        solution_template = stream.read()

    for problem in problems:
        try:
            tests = download_problem(problem)
        except Exception, e:
            print "Exception (%s) raised during test downloding for problem '%s'" % (e, problem)
            if force:
                print "Going to use empty tests"
                tests = []
            else:
                print "Exiting. Use --force to ignore errors"
                return

        save(contest_dir, extract_letter(problem), tests, solution_template)

    for qtfile in (script_dir / "qtcreator").glob("CONTEST*"):
        copy_substitute(
            qtfile,
            contest_dir / qtfile.basename().replace("CONTEST", contest_slug),
            ROOT_DIR=contest_dir,
        )

    for aux_file in "Makefile", "tester.cpp", "custom_tests.cpp":
        copy_substitute(
            script_dir / aux_file,
            contest_dir,
            PROBLEM_LETTERS=" ".join(problem_letters),
        )

    print
    print "ALL DONE"
    print "Run to open qtcreator:"
    print "cd %s && qtcreator %s.creator" % (contest_dir, contest_slug)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Download pretests from codeforces website',
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "--force",
        action="store_true",
        help="ignore any exception occured during test downloading")
    parser.add_argument(
        "--base-dir",
        default=str(path.path(__file__).dirname().abspath().parent / "contests"),
        help="path to dir with contests (default: %(default)s)")
    parser.add_argument(
        'contest',
        help=('which contest to download\n'
              'examples:\n'
              '\t416\n'
              '\tcontest/416\n'
              '\thttp://codeforces.com/contest/416/problem/A\n'
              'by default, the last contest is downloaded')
    )
    main(**vars(parser.parse_args()))


#!/usr/bin/env python3

"""This is a Diaspora* client written using `diaspy` API.

The story that led to it's creation is quite funny because
it's about the author who misconfigured X.org and had to 
post something using CLI.


SYNTAX:
    diaspyc [global options ...] [MODE [mode options ...]]


Global options:

    -V, --verbose               - be more verbose
    -h, --help                  - display this help
    -v, --version               - display version information

Login options (global):

    -H, --handle HANDLE         - Diaspora* handle (overrides config)
        --save-auth N           - store auth data for N seconds (not implemented)


post:
    -s, --send STR              - send post (conflicts: --read, --reshare)
    -i, --image PATH            - attach image to post
    -r, --read                  - read post with given ID (conflicts: --send)
    -a, --also-comments         - in addition to post content, print its comments (requires: --read)
    -R, --reshare               - reshare post of given ID (conflicts: --send)
    -c, --comment STR           - send comment to post (conflicts: --send)
    -l, --like                  - send like post (conflicts: --send)
    -I, --id ID                 - supplies post id (required by --read, --reshare, --comment, --like)


notifs (short for 'notifications'):
    -l, --last                  - check your unread notifications
    -r, --read                  - mark listed notifications as read (by default notifications are not marked)
    -p, --page N                - print N-th page of notifications
    -P, --per-page N            - print N notifications per page
"""

__version__ = '0.0.10'

import getpass
import sys
import diaspy
import clap


formater = clap.formater.Formater(sys.argv[1:])
formater.format()

post = clap.parser.Parser()
post.add(short='s', long='send', argument=str)
post.add(short='r', long='read', requires=['--id'], conflicts=['--send'])
post.add(short='a', long='also-comments', requires=['--read'])
post.add(short='C', long='comment', requires=['--id'], conflicts=['--send'])
post.add(short='R', long='reshare', requires=['--id'], conflicts=['--send'])
post.add(short='l', long='like', requires=['--id'], conflicts=['--send'])
post.add(short='I', long='id', argument=int, conflicts=['--send'])

notifications = clap.parser.Parser()
notifications.add(short='l', long='last', conflicts=['--page'])
notifications.add(short='r', long='read')
notifications.add(short='p', long='page', argument=int, conflicts=['--last'])
notifications.add(short='P', long='per-page', argument=int, requires=['--page'])

stream = clap.parser.Parser()

options = clap.modes.Parser(list(formater))
options.addMode('post', post)
options.addMode('notifs', notifications)
options.addMode('stream', stream)
options.addOption(short='h', long='help')
options.addOption(short='v', long='version')
options.addOption(short='C', long='component', argument=str)
options.addOption(short='V', long='verbose')
options.addOption(short='H', long='handle', argument=diaspy.people.sephandle)
options.addOption(long='schema', argument=str, requires=['--handle'])
options.addOption(long='save-auth', argument=int)


def fatal(message):
    """Prints fatal message and exits.
    """
    print('diaspyc: fatal: {0}'.format(message))

try:
    options.define()
    options.check()
    fail = False
except clap.errors.UnrecognizedModeError as e:
    fatal('unrecognized mode: {0}'.format(e))
    fail = True
except clap.errors.UnrecognizedOptionError as e:
    fatal('unrecognized option: {0}'.format(e))
    fail = True
except clap.errors.RequiredOptionNotFoundError as e:
    fatal('required option was not found: {0}'.format(e))
    fail = True
except clap.errors.NeededOptionNotFoundError as e:
    fatal('at least one of needed options must be passed: {0}'.format(e))
    fail = True
except clap.errors.MissingArgumentError as e:
    fatal('missing argument for option: {0}'.format(e))
    fail = True
except (clap.errors.InvalidArgumentTypeError, diaspy.errors.UserError) as e:
    fatal('invalid argument for option: {0}'.format(e))
    fail = True
except clap.errors.ConflictingOptionsError as e:
    fatal('conflicting options: {0}'.format(e))
    fail = True
finally:
    if fail: exit(1)
    else: options.parse()


if '--version' in options:
    if '--verbose' in options: v = 'diaspyc version: {0} (diaspy backend: {1})'.format(__version__, diaspy.__version__)
    else: v = __version__
    if '--component' in options:
        component = options.get('--component')
        if component == 'diaspyc':
            v = __version__
        elif component in ['diaspy', 'backend']:
            component = 'diaspy'
            v = diaspy.__version__
        elif component == 'clap':
            v = clap.__version__
        else: v = 'diaspyc: fatal: there is no \'{0}\' component'.format(component)
        if '--verbose' in options and 'fatal:' not in v:
            v = '{0} version: {1}'.format(component, v)
    print(v)
    exit(0)


if '--help' in options:
    print(__doc__)
    exit(0)

if not str(options): exit(0)

if '--handle' in options: pod, username = options.get('--handle')
else: pod, username = '', ''
try:
    schema = 'https'
    if '--schema' in options: schema = options.get('--schema')
    if not pod: pod = input('Diaspora* pod: ')
    if not username: username = input('Username for {0}: '.format(pod))
    password = getpass.getpass('Password for {0}@{1}: '.format(username, pod))
    connection = diaspy.connection.Connection(pod=pod, username=username, password=password, schema=schema)
    connection.login()
except (KeyboardInterrupt, EOFError):
    fail = True
    print()
finally:
    if fail:
        exit(0)
    if '--save-auth' in options:
        print('diaspyc: fail: --save-auth not implemented')

message = ''
if str(options) == 'post':
    if '--send' in options:
        if '--image' in options: photo = options.get('--image')
        else: photo = ''
        text = ' '.join(options.arguments)
        if text or photo: message = repr(diaspy.streams.Activity(connection).post(text=text, photo=photo))
        else: message = 'diaspyc: fail: nothing to post'
    if '--read' in options:
        id = options.get('--id')
        post = diaspy.models.Post(connection, id)
        print(repr(post))
        if '--also-comments' in options and len(post.comments):
            print('Comments for this post:')
            for c in post.comments: print(repr(c))
    if '--reshare' in options:
        id = options.get('--id')
        post = diaspy.models.Post(connection, id)
        post.reshare()
        if '--verbose' in options: message = 'diaspyc: you reshared {0}\'s post'.format(post.author('name'))
    if '--comment' in options:
        id = options.get('--id')
        post = diaspy.models.Post(connection, id)
        post.comment(options.get('--comment'))
        if '--verbose' in options: message = 'diaspyc: you commented on {0}\'s post'.format(post.author('name'))
    if '--like' in options:
        id = options.get('--id')
        post = diaspy.models.Post(connection, id)
        post.like()
        if '--verbose' in options: message = 'diaspyc: you liked {0}\'s post'.format(post.author('name'))
elif str(options) == 'notifs':
    notifications = diaspy.notifications.Notifications(connection)
    if '--page' in options:
        page = options.get('--page')
        if '--per-page' in options: per_page = options.get('--per-page')
        else: per_page = 5
        notifs = notifications.get(per_page=per_page, page=page)
    elif '--last' in options:
        notifs = notifications.last()
    else:
        notifs = []
    for n in notifs:
        text = repr(n)
        about = n.about()
        if type(about) == int: about = '[{0}]'.format(about)
        else: about = ''
        print('{0} {1}'.format(text, about))
        if '--read' in options: n.mark(read=True)
else:
    message = 'diaspyc: fail: \'{0}\' mode not implemented'.format(str(options))
if message: print(message)

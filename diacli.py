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



This is free software published under GNU GPL v3 license or any later version of this license.

Copyright Marek Marecki (c) 2013"""

__version__ = '0.0.12'

import getpass
import sys
import diaspy
import clap


formater = clap.formater.Formater(sys.argv[1:])
formater.format()

post = clap.parser.Parser()
post.add(short='s', long='send', arguments=[str])
post.add(short='r', long='read', requires=['--id'], conflicts=['--send'])
post.add(short='a', long='also-comments', requires=['--read'])
post.add(short='C', long='comment', requires=['--id'], conflicts=['--send'])
post.add(short='R', long='reshare', requires=['--id'], conflicts=['--send'])
post.add(short='l', long='like', requires=['--id'], conflicts=['--send'])
post.add(short='I', long='id', arguments=[int], conflicts=['--send'])

notifications = clap.parser.Parser()
notifications.add(short='l', long='last', conflicts=['--page'])
notifications.add(short='r', long='read')
notifications.add(short='p', long='page', arguments=[int], conflicts=['--last'])
notifications.add(short='P', long='per-page', arguments=[int], requires=['--page'])

stream = clap.parser.Parser()

config = clap.parser.Parser()

options = clap.modes.Parser(list(formater))
options.addMode('post', post)
options.addMode('notifs', notifications)
options.addMode('stream', stream)
options.addOption(short='h', long='help')
options.addOption(short='v', long='version')
options.addOption(short='C', long='component', arguments=[str])
options.addOption(short='V', long='verbose')
options.addOption(short='H', long='handle', arguments=[diaspy.people.sephandle])
options.addOption(long='schema', arguments=[str], requires=['--handle'])
options.addOption(long='save-auth', arguments=[int])


def fatal(message):
    """Prints fatal message and exits.
    """
    print('diaspyc: fatal: {0}'.format(message))

try:
    #   define mode to work with
    options.define()
    #   check options for errors
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
    """Print version information.
    By default it is version of the interface (if --verbose then backend
    version is added).

    It is possible to specify component which you version you wnat to get.
    Currently, available components are:
    *   ui:             versionof this interface,
    *   backend/diaspy: version of diaspy backend used,
    *   clap:           version of library used to create user interface,
    """
    if '--verbose' in options: v = 'diaspyc version: {0} (diaspy backend: {1})'.format(__version__, diaspy.__version__)
    else: v = __version__
    if '--component' in options:
        component = options.get('--component')
        if component == 'ui':
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
    """Prints help and exits.
    """
    print(__doc__)
    exit(0)

if not str(options):
    #   if no mode is given finish execution
    exit(0)

if '--handle' in options:
    #   if handle is given split it into pod and username and
    #   set these fileds accordingly
    pod, username = options.get('--handle')

    #   default shcema is https
    schema = 'https'
    if '--schema' in options:
        #   if schema is passed on the command line
        #   the default value will be overwritten by it
        schema = options.get('--schema')
    #   create pod URL from given schema and pod
    pod = '{0}://{1}'.format(schema, pod)
else:
    #   if handle was not given set username and pod to empty strings
    #   so it will be detected that the user must give them
    pod, username = '', ''
try:
    if not pod: pod = input('Diaspora* pod: ')
    if not username: username = input('Username for {0}: '.format(pod))
    password = getpass.getpass('Password for {0}@{1}: '.format(username, pod))
    #   we create connection which will be used later...
    connection = diaspy.connection.Connection(pod=pod, username=username, password=password)
    #   ...and login into a pod
    connection.login()
except (KeyboardInterrupt, EOFError):
    #   if user cancels the login, exit cleanly
    fail = True
    print()
finally:
    if fail:
        #   this denotes that user cancelled the operation
        exit(0)
    if '--save-auth' in options:
        #   save authorization data for later use
        print('diaspyc: fail: --save-auth not implemented')

message = ''
if str(options) == 'post':
    """Post has a handful of sub-modes each of which is enabled by one
    *streering option*.
    """
    if '--send' in options:
        #   User wants to send post to a pod.
        #   This is equivalent to posting something through the web UI.
        if '--image' in options:
            #   if --image is given the photo from the path will
            #   be posted
            photo = options.get('--image')
        else: photo = ''
        #   user can enetr text as a single string encapsulated in '' but to prevent mistakes diacli
        #   will join every string passed as an argument and post it all
        text = options.get('--send')
        text = text.replace('\\n', '\n')
        if text or photo:
            #   if text or photo is given it will be posted
            message = repr(diaspy.streams.Activity(connection).post(text=text, photo=photo))
        else: message = 'diaspyc: fatal: nothing to post'
    if '--read' in options:
        #   we need to get id of post which user wants to read
        id = options.get('--id')
        #   and create an object representing this post
        post = diaspy.models.Post(connection, id)
        print(repr(post))   #   this will print the post
        if '--also-comments' in options and len(post.comments):
            #   print comments if --also-comments was passed and there is at least
            #   one comment to print
            print('\n**Comments for this post:**\n')
            for c in post.comments: print('**{0}\n'.format(repr(c)))
    if '--reshare' in options:
        #   reshare post of given id
        id = options.get('--id')
        post = diaspy.models.Post(connection, id)
        post.reshare()
        if '--verbose' in options: message = 'diaspyc: you reshared {0}\'s post'.format(post.author('name'))
    if '--comment' in options:
        #   comment on post with given id
        id = options.get('--id')
        post = diaspy.models.Post(connection, id)
        post.comment(options.get('--comment'))
        if '--verbose' in options: message = 'diaspyc: you commented on {0}\'s post'.format(post.author('name'))
    if '--like' in options:
        #   like post with given id
        id = options.get('--id')
        post = diaspy.models.Post(connection, id)
        post.like()
        if '--verbose' in options: message = 'diaspyc: you liked {0}\'s post'.format(post.author('name'))
elif str(options) == 'notifs':
    #   this mode allows user to check his/hers notifications
    #
    #   Firts, we create object representing user's notifications.
    notifications = diaspy.notifications.Notifications(connection)
    if '--page' in options:
        #   if user wants to read specific page of his/hers notifications
        #   get the page number
        page = options.get('--page')
        if '--per-page' in options:
            #   set number of notifications per page according to the value
            #   specified on the command line...
            per_page = options.get('--per-page')
        else:
            #   ...or set the default value
            per_page = 5
        #   get notifications which match given criteria
        notifs = notifications.get(per_page=per_page, page=page)
    elif '--last' in options:
        #   if user wants to just view his/hers --last notifications
        notifs = notifications.last()
    else:
        #   if none of the above is True no notifications will be printed
        notifs = []
    for n in notifs:
        #   print every notification found
        text = repr(n)
        about = n.about()
        #   if the notification is about some post add information about id
        #   of the post being mentioned
        if type(about) == int: about = '[{0}]'.format(about)
        else: about = ''
        print('{0} {1}'.format(text, about))
        if '--read' in options:
            #   if --read switch is present notifications will be marked as read
            n.mark(read=True)
else:
    #   default message for not implememted modes
    message = 'diaspyc: fatal: \'{0}\' mode not implemented'.format(str(options))
if message: print(message)

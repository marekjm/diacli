### `diacli` - Diaspora\* Command Line Interface


`diacli` is the program that let's you communicate with Diaspora\* from the command line. 
Originally developed when author's GUI (X.org and GNOME, I'm looking at you) crashed and refused to come to life again.


#### Dependencies

`diacli` has only three dependencies:

*   `python` - Python interpreter version 3.x,
*   `diaspy` - unofficial Python API for Diaspora\*,
*   `clap` - library used to build the user interface.

You will of cource need a Diaspora\* account.


**Python**

Python can be downloaded from [*http://python.org/*](http://python.org/). 
Users of any flavor of Linux can use their package manager to get Python if it's not already 
installed on their system. 


**`diaspy`**

`diaspy` can be installed using `pip` or [obtained from GitHub](https://github.com/marekjm/diaspora-api). 
If you want to use the bleeding edge version of API the GitHub method is suggested. 
After fetching from GitHub install using `setup.py` script.


**`clap`**

`clap` can only be found [on GitHub](https://github.com/marekjm/clap). 
Use version 0.12.1 or later. CLAP is now mostly stable so you can also use the
most recent code from `master` or `devel` and you should be good to go.
You will have to manually install the code in your `site-packages` by executing
`make local-install` in cloned CLAP repository.

----

#### Installation

Move `diacli.py` to `~/.local/bin` (or any place when executables are placed on your system -- 
`~/.local/bin` just don't require you to go root), 
rename it to `diacli` (`mv diacli.py diacli`) and make it executable (`chmod +x diacli`).

    git clone https://github.com/marekjm/diacli.git
    cd diacli
    cp ./diacli.py ~/.local/bin
    cd ~/.local/bin
    mv ./diacli.py ./diacli
    chmod +x ./diacli

If you are OK with the `~/.local/bin` default installation directory you can just do:

    git clone https://github.com/marekjm/diacli.git
    cd diacli
    make install

And you are all set.

##### Configuration

You can manage your configuration using `config` mode.

Configuration is read from:

    ~/.diacli/conf.json

Keys that have some meaning are:

*   `handle`:   your handle,

----

#### Bugs

Please, make note that `diaspy` and Diaspora\* are both alpha software and 
`clap` is somewhere between late alpha and early beta. 
If you'll encounter any bugs, please report them to the developers.


**`diaspy`** 

Find user [Javafant](https://pod.geraspora.de/people/2802abdf566f83b2) or 
[marekjm](https://pod.orkz.net/people/fd4ac447f2d267fa) an tell them what's wrong with `diaspy`. 
Also, you can create an issue on GitHub or notify them somehow else.


**`clap`** 

Find `clap` [on GitHub](https://github.com/marekjm/clap) and tell the author what's wrong.


**Python**

Python bugs can be reported on [Python issue tracker](http://bugs.python.org).


__Diaspora\*__

Diaspora\*: first post the issue using `#bug` or `#question` tags. Maybe the solution is out there. 
Alternatively, find Diaspora\* on GitHub and report there.

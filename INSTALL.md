# Installation

    sudo apt-get install nginx python-pip
    sudo pip install virtualenv virtualenvwrapper

Add to .bashrc:

    export WORKON_HOME=$HOME/.virtualenvs
    source /usr/local/bin/virtualenvwrapper.sh

Enter another terminal or reenter shell by typing `/bin/sh`

    mkvirtualenv horarispompeu

Move to horarispompeu git repo and type:

    pip install -r requirements.txt

To install phantom and casperjs (for auto logins):

    cd
    wget https://phantomjs.googlecode.com/files/phantomjs-1.9.2-linux-x86_64.tar.bz2
    tar -xvf phantomjs-1.9.2-linux-x86_64.tar.bz2
    cd phantomjs-1.9.2-linux-x86_64/
    sudo ln -sf `pwd`/bin/phantomjs /usr/local/bin/phantomjs
    cd ..
    git clone git://github.com/n1k0/casperjs.git
    cd casperjs/
    sudo ln -sf `pwd`/bin/casperjs /usr/local/bin/casperjs

Now, every time you want to execute project related stuff run:

    workon horarispompeu

When you want to exit the virtual environment, simply time:

    deactivate

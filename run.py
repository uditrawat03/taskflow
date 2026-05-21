# run.py
# TaskFlow AI — Project root entry point.
#
# Always run this file to start the app:
#   python run.py                          # interactive mode
#   python run.py add "Review PR #high"   # one-shot mode
#   python run.py --help                   # show all commands
#
# This file must stay at the project root so that Python can find
# the taskflow/ package in the same directory.

from taskflow.main import main

if __name__ == "__main__":
    main()
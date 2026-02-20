import sys
from srcs.managing.manager import Manager


if __name__ == "__main__":
    manager = Manager(sys.argv)
    manager.execute()

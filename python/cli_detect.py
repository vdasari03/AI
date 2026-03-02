import sys
import json
from shell_integration import detect_commands


def main():
    if len(sys.argv) < 2:
        print(json.dumps([]))
        return
    text = " ".join(sys.argv[1:])
    cmds = detect_commands(text)
    print(json.dumps(cmds))


if __name__ == "__main__":
    main()

from subprocess import PIPE, run


class shell:

    def __init__(self, command=None):
        self.command = command

    def run(self):
        print(self.command)
        result = run(self.command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
        return str(result.stdout).strip()

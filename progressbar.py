import threading
import time

class ProgressBar():
    """
    A helper class for continually displaying a dynamic progress bar.
    """

    def __init__(self, progress_max=-1):
        """
        Initialize the progress bar.
        Parameters:
        progress_max - the progress at which point the percentage is 100
        """

        self.spinner_set = ['|', '/', '-', '\\']
        self.spinner_index = 0

        self.current_progress = 0
        self.progress_max = -1 if progress_max <= 0 else progress_max
        self.indeterminate = (self.progress_max <= 0)

        self.full_bar_length = 40
        self.full_bar = '#' * self.full_bar_length

        self.message = ''

    def update(self):
        """
        Redraw the progress bar.
        """

        spinner_character = self.spinner_set[self.spinner_index]
        self.spinner_index = (self.spinner_index + 1) % len(self.spinner_set)

        if not self.indeterminate:
            progress_factor = self.current_progress / self.progress_max
            bar_portion_length = int(progress_factor * self.full_bar_length)
            bar_portion = self.full_bar[:bar_portion_length]
        else:
            bar_portion = ' ' * self.full_bar_length
            i = self.current_progress
            bar_portion = bar_portion[:i] + '#' + bar_portion[(i + 1):]
            self.current_progress = (i + 1) % self.full_bar_length
            progress_factor = 0

        print("\033[2K\033[1G{spc} {pct:>3}% [{0:<{bw}}] {msg}".format(
            bar_portion,
            spc=spinner_character,
            pct=int(progress_factor * 100),
            bw=self.full_bar_length,
            msg=self.message
        ), end='', flush=True)


    def progress(self, prog, message=''):
        """
        Increase the progress.
        Parameters:
        prog    - the new progress amount
        message - an optional message to display after the progress bar
        """

        self.current_progress = prog
        self.message = message

    def stop(self, message=''):
        """
        Stop the progress bar.
        Will output a filled progress bar.
        """

        # Redraw the bar with a percentage of 100%.
        self.message = message
        self.progress_max = 1
        self.current_progress = self.progress_max
        self.spinner_set = ['_'] * len(self.spinner_set)
        self.update()
        print()

class ProgressBarThread(threading.Thread):
    def __init__(self, progress_max=-1):
        super().__init__()

        self.progress_bar = ProgressBar(progress_max)
        self.timeout = 0.1
        self.running = True

    def run(self):
        while self.running:
            self.progress_bar.update()
            time.sleep(self.timeout)

    def progress(self, prog, message=''):
        self.progress_bar.progress(prog, message)

    def stop(self, message=''):
        self.running = False

        time.sleep(self.timeout * 1.5)

        self.progress_bar.stop(message)
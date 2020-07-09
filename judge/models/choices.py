import pytz

# Create your models here.

status_choices = [
    ('AC', 'Accepted'),
    ('WA', 'Wrong Answer'),
    ('TLE', 'Time Limit Exceeded'),
    ('MLE', 'Memory Limit Exceeded'),
    ('OLE', 'Output Limit Exceeded'),
    ('IR', 'Invalid Return'),
    ('IE', 'Internal Error'),
    ('AB', 'Aborted'),
    ('G', 'Grading'),
    ('MD', 'Missing Data'),
]

language_choices = [
    ('python3', "Python3"),
    ('java8', "Java 8"),
    ('cpp17', "C++17"),
    ('haskell', "Haskell"),
    ('brainfuck', "Brainfuck"),
    ('c18', "C18"),
    ('java11', "Java 11"),
    ('scratch', "Scratch"),
    ('text', "Text"),
]

timezone_choices = [(i, i) for i in pytz.common_timezones]

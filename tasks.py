from invoke import task


@task
def black(c):
    c.run('black -l 88 pyRoute13 tests')

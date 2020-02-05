from invoke import task


@task
def black(c):
    c.run("black -l 88 pyRoute13 tests")


@task
def test(c):
    c.run(
        "nosetests --exe -v --nocapture --with-coverage --cover-erase --cover-package=environment,core,agents,generators"
    )


@task
def simple(c):
    c.run('python pyRoute13/simple_simulator.py')


@task
def full(c):
    c.run('python pyRoute13/full_simulator.py')

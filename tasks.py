from invoke import task


@task
def update(c):
    c.run('pip freeze > requirements.txt')

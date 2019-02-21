import docker
import datetime
import os
import crython

clean_images_expr = os.getenv('CLEAN_IMAGES_EXPR', '@daily')
clean_containers_expr = os.getenv('CLEAN_CONTAINERS_EXPR', '@daily')
container_expired_sec = int(os.getenv('CONTAINER_EXPIRED_SEC', 86400))  # or 24 h


@crython.job(expr=clean_images_expr)
def clean_images():
    client = docker.from_env()

    result = client.images.prune({"dangling": False})
    print(result)

@crython.job(expr=clean_containers_expr)
def clean_containers():
    client = docker.from_env()

    # blacklist_images: list = ['openjdk:7']

    non_running_statuses: list = [
        'created',
        # 'restarting',
        'removing',
        'paused',
        'exited',
        'dead',
    ]

    containers_all = client.containers.list(all=True)

    # def filter_whitelisted(c) -> bool:
    #     try:
    #         return not set(c.image.tags) & set(blacklist_images)
    #     except:
    #         return True

    def filter_non_running(c) -> bool:
        return c.status in non_running_statuses

    def filter_old(c) -> bool:
        run_time = datetime.datetime.strptime(c.attrs['Created'][0:18], '%Y-%m-%dT%H:%M:%S')
        return run_time < datetime.datetime.now() - datetime.timedelta(seconds=container_expired_sec)

    containers_to_rem = list(filter(lambda x: all(f(x) for f in (filter_non_running, filter_old)), containers_all))

    for c in containers_to_rem:
        c.remove()
        print('Removed container {}'.format(c.name))


if __name__ == '__main__':
    crython.start()
    print("Starting autoclean containers with '{}', images with '{}' ...".format(clean_containers_expr,
                                                                                 clean_images_expr))
    crython.join()  ## This will block

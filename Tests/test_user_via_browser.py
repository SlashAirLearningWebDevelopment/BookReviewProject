import pytest
import subprocess
import time
import socket
import random

def wait_for_port(port, host='localhost', timeout=5.0, only_once=False):
    """Wait until a port starts accepting TCP connections.
    Args:
        port (int): Port number.
        host (str): Host address on which the port should exist.
        timeout (float): In seconds. How long to wait before raising errors.
    Raises:
        TimeoutError: The port isn't accepting connection after time specified in `timeout`.
    """
    start_time = time.perf_counter()
    while True:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                break
            if only_once:
                raise TimeoutError(f"Waited once for port {port} on host {host}")
        except OSError as ex:
            time.sleep(0.01)
            if time.perf_counter() - start_time >= timeout:
                raise TimeoutError(f'Waited too long for the port {port} on host {host} to start accepting '
                                   'connections.') from ex

@pytest.fixture(scope="package")
def server_port():
    return random.randint(3000,9000)

@pytest.fixture(scope="package")
def run_server_fixture(server_port):
    port = server_port
    # before starting server make sure its not already running.
    try:
        wait_for_port(port, only_once=True)
    except TimeoutError:
        # this is expected as server should not be runing at this point
        pass
    else:
        # its running now stop it before starting
        print(subprocess.check_output(f"freeport {port}", shell=True))


    try:
        wait_for_port(port, only_once=True)
    except TimeoutError:
        pass
    else:
        raise Exception("Server already running")


    print(f"Starting server at host 0.0.0.0:{port}")
    process = subprocess.Popen([
        "python",
        "manage.py",
        "run_server",
        "--host=0.0.0.0",
        f"--port={port}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    wait_for_port(port)
    yield
    print("Terminating server")
    process.kill()

class TestLoginViaBrowser():

    def test_landing_page_title(self, page, run_server_fixture, server_port):
        page.goto(f"http://localhost:{server_port}")
        assert page.title() == "BookReview"

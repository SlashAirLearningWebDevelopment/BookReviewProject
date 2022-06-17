import pytest
import subprocess
import time
import socket
import random
import string
from users import login, register

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

@pytest.fixture(scope="module")
def random_username():
    return ''.join(random.choices(string.ascii_lowercase, k = 5))

@pytest.fixture(scope="module")
def random_password():
    return ''.join(random.choices(string.ascii_lowercase, k = 5))


@pytest.fixture(scope="function")
def new_username():
    return ''.join(random.choices(string.ascii_lowercase, k = 5))

@pytest.fixture(scope="function")
def new_password():
    return ''.join(random.choices(string.ascii_lowercase, k = 5))


@pytest.fixture(scope="package")
def server_port():
    return random.randint(3000,9000)

@pytest.fixture(scope="package")
def server_url(server_port):
    return f"http://localhost:{server_port}"

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


    def test_landing_page_title(self, page, run_server_fixture, server_url):
        page.goto(server_url)
        assert page.title() == "BookReview"

    def test_register_page_redirects_to_login(self, page, run_server_fixture, server_url, new_username, new_password):
        # got to register page
        page.goto(f"{server_url}")
        page.fill("#username", new_username)
        page.fill("#password1", new_password)
        page.fill("#password2", new_password)
        page.fill("#dateOfBirth", "2020-01-02")
        page.click('#submit')

        page.wait_for_load_state("networkidle")

        # test page has been redirected
        assert("/user/login" in page.url)


    def test_register_page_adds_user(self, page, run_server_fixture, server_url, new_username, new_password):
        # got to register page
        page.goto(f"{server_url}")
        page.fill("#username", new_username)
        page.fill("#password1", new_password)
        page.fill("#password2", new_password)
        page.fill("#dateOfBirth", "2020-01-02")
        page.click('#submit')

        page.wait_for_load_state("networkidle")

        # test page has been redirected
        assert("/user/login" in page.url)

        # now test login will return that user
        try:
            returned_user = login(new_username, new_password)
            assert returned_user == {"username": new_username, "password": new_password, "dateOfBirth": "02/01/2020"}
        except Exception as e:
            assert False, f"User was not registered hence login failed with {e.__class__}"

    def test_landing_page_redirects_to_registered_if_not_logged_in(self, page, run_server_fixture, server_url):
        page.goto(server_url)
        pass

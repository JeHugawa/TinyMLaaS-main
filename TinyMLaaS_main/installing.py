# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/Bridge/installing.ipynb.

# %% auto 0
__all__ = ['DOCKERHUB_USER', 'install_inference', 'arduino_installer', 'upload_rpi']

# %% ../nbs/Bridge/installing.ipynb 1
import docker
import getpass

# uncomment this when using with MCU
# from .device import get_device_port

DOCKERHUB_USER = "ohtuprojtinymlaas"

# %% ../nbs/Bridge/installing.ipynb 3
def install_inference(device: dict, model: str):
    """Select the appropriate installer for the device
    and call that installer"""
    installers = {
        "RPI": upload_rpi,
        "Arduino IDE": arduino_installer
    }
    installer = device["installer"]
    try:
        installers[installer](device, model)
    except KeyError:
        return False
    except ValueError:
        return False
    finally:
        return True


def arduino_installer(device: dict, compiled_model: str):
    """Install the wanted model to a Arduino
    """

    port = get_device_port(device["serial"])
    with open("arduino/template/target_model.cpp", "w") as file:
        file.write(compiled_model)
    client = docker.from_env()
    try:
        res = client.images.build(path="arduino/", tag="nano33ble")
        print(res)
    except docker.errors.BuildError as e:
        print("Error while building", e)
    try:
        res = client.containers.run(
            image="nano33ble",
            command=f"upload -p {port} --fqbn arduino:mbed_nano:nano33ble template",
            devices=[f"{port}:{port}:rw"]
        )
        print(res)
    except Exception as e:
        print(e)


def upload_rpi():
    """Uploads compiled person detection uf2 file to device. 
    The device must be in the USB Mass Storage Mode and `device_path` should be the absolute path 
    at which the device is mounted at.
    """
    
    # This can actually get mounted elsewhere, perhaps you could find the path by looking for the files that exist in that directory
    device_path = f"/media/{getpass.getuser()}/RPI-RP2"
    docker_img = f"{DOCKERHUB_USER}/pico"
    subprocess.run([f"docker pull {docker_img}"], shell=True)
    # this mounts the device_path inside the container and copies the uf2 file from the container to device_path
    cmd = f"docker run --rm -v {device_path}:/opt/mount --entrypoint cp {docker_img} person_detection_screen_int8.uf2 /opt/mount/app.uf2"
    subprocess.run([cmd], shell=True)


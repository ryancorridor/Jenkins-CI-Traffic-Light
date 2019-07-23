# Jenkins-CI-Traffic-Light
> An Arduino driven project that controls lights to signal the status of a Jenkins job.

[![Build Status][build-shield]]()
[![Contributors][contributors-shield]]()
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

## About The Project
This project was made during an internal hackathon I competed in as an intern at Zix. It is a visualizer for Jenkins builds that is designed to be utilized by development and DevOPs teams. The LED indicators will change color, reflecting the current status of the build. If the status changes an optional email notification can be sent to a individual or a mailing list, enabling it to be a useful tool for entire teams.

<p align="center"><img  src='img/trafficlight.gif' alt='')></p>


### Built With
Jenkins-CI-Traffic-Light was built with the following libraries and resources

* [Arduino Uno](https://store.arduino.cc/usa/arduino-uno-rev3)
* [Python 3.7](https://www.python.org/downloads/)
* [PyFirmata](https://pypi.org/project/pyFirmata/)

## Hardware Installation

Required resources

* Arduino Uno
* Red, Yellow, and Green LED
* Breadboard
* Jumper Wires
* 330Ω Resistors

The setup is entirely up to the installer, but I have a photo of my setup incase you would like to mirror it.
<p align="center"><img src='img/topdown.jpg' alt='' height=75% width=75%/></p>

## Software Installation

Windows, OS X & Linux:

```sh
git clone https://github.com/ryancorridor/Jenkins-CI-Traffic-Light.git
```


To actually configure the script to get it running properly, the process is actually not that long. After cloning the repository all you will need to install the one dependency, **PyFirmata**, and make the Python script executable.

```sh
pip install pyfirmata
chmod +x trafficlight.py
```

There are some further changes that need to be made directly in the script before it can be run. For security reasons I have stripped out any Jenkins servers I used for development and left sample variables instead.

This code block can be found near the top of the script. Change the ```<insert_blank>``` strings with your specific values. If you are confused about what values to put for *board_serial_port* or *pin_number* refer to the [PyFirmata documentation](https://pyfirmata.readthedocs.io/en/latest/). 

(e.g. ```'<insert_board_serial_port_here>'``` -> ```/dev/cu.usbmodemFD131```)

```python
board = Arduino('<insert_board_serial_port_here>')

LEDS = {
    "red": board.get_pin('d:<insert_pin_number_here>:o'),
    "yellow": board.get_pin('d:<insert_pin_number_here>:o'),
    "green": board.get_pin('d:<insert_pin_number_here>:o')
}
JENKINS_SERVERS = {
    '<insert_server_name_here>': '<insert_server_url_here>',
}

EMAIL_RELAY = '<insert_email_relay_here>'
EMAIL_SENDER = '<insert_email_sender_here>'
```


## Usage example
To use the CLI to browse Jenkins builds:

```sh
./trafficlight.py
```

If you know what parameters you need:

```sh
./trafficlight.py server job build [-e EMAIL]
```
**Email is an optional feature. If you wish to not have it enabled, just do not include it in your arguments*

## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

Ryan Hall - [@ryancorridor](https://twitter.com/ryancorridor) - ryan.hall.tx@gmail.com

Project Link: [https://github.com/ryancorridor/bullwinkle](https://github.com/ryancorridor/bullwinkle)

<!-- MARKDOWN LINKS & IMAGES -->
[build-shield]: https://img.shields.io/badge/build-passing-brightgreen.svg?style=flat-square
[contributors-shield]: https://img.shields.io/badge/contributors-1-orange.svg?style=flat-square
[license-shield]: https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square
[license-url]: https://choosealicense.com/licenses/mit
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=flat-square&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/ryan-hall-tx

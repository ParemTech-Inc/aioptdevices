<a id="readme-top"></a>

<!-- PROJECT SHIELDS -->

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://paremtech.com">
    <img src=".github/assets/Paremtech logo white.png" alt="Logo" width="500">
  </a>

  <h3 align="center">aioptdevices</h3>

  <p align="center">
    Easily fetch your PTDevice information from the PTDevices servers with the aioptdevices package.
    <br />
</div>


<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-this-project">About This Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About This Project

This package allows polling the PTDevices servers for device data via the token API. See [Token API Docs](https://support.paremtech.com/portal/en/kb/articles/api-options#Token_API). It was developed for use in the PTDevices Home Assistant Integration but can be used for other projects. It offers both a command line tool and a library.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started
### Prerequisites

- Have Python 3.12 or later installed.
- Have a PTDevices account and an API token.
  You can request a free API token by creating a support ticket at [https://support.paremtech.com/portal/en/newticket](https://support.paremtech.com/portal/en/newticket). To help streamline the process, be sure to include the email address associated with your PTDevices account.

### Installation

#### PyPi
```shell
python3 -m pip install aioptdevices
```

#### Manual Setup
1. Clone the repository.
    ```shell
    git clone https://github.com/ParemTech-Inc/aioptdevices.git
     ```
2. Install Python Packages and setup the environment.

    **Linux venv Setup**
    ```shell
    bash ./setup.sh
    source venv/bin/activate
    ```
    **Windows venv Setup**
    ```shell
    .\setup.ps1
    .\venv\Scripts\activate
    ```
    **Installing Globally**
    
    Linux and Windows
    ```shell
    python3 -m pip install .
    ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage
### As a Command Line Tool
Make sure to set up and activate the venv or install the package globally before trying to use it, refer to [Manual setup step 2](#manual-setup). If you installed the package from PyPi, you can go straight to [Command usage](#command-usage).

#### Command usage

```
usage: aioptdevices [-h] [-U URL] [-D] deviceID authToken

positional arguments:
  deviceID
  authToken

options:
  -h, --help         show this help message and exit
  -U URL, --url URL
  -D, --debug
```

### As a Library
See the [examples](examples) folder for usage as a library.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->
## Contributing

If you have an idea to improve this package, please fork the repo and create a pull request. Or, you can simply open an issue.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Create ./tests/secret.py with
```py
"""Secret Parameters."""

TOKEN: str = "Your API Token"
DEVICE_ID: str = "Your Device ID"
```
5. Run pytest and verify that all tests pass
6. Push to the Branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the GNU GPL-3.0 License. See [LICENSE](LICENSE) for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Matthew Gibson - [@frogman85978](https://github.com/frogman85978) - matthew.gibzon@gmail.com

ParemTech Inc. - [@ParemTech-Inc](https://github.com/ParemTech-Inc) - info@paremtech.com

Project Link: [https://github.com/ParemTech-Inc/aioptdevices](https://github.com/ParemTech-Inc/aioptdevices)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* Othneil Drew ([@othneildrew](https://github.com/othneildrew)) creator of the [Best-README-Template](https://github.com/othneildrew/Best-README-Template)
* Robert Svensson ([@Kane610](https://github.com/Kane610)) creator of the [aiounifi package](https://github.com/Kane610/aiounifi)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->


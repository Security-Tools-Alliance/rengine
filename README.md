<p align="center">
<img src=".github/images/banner-rengine-ng.png" alt=""/>
</p>

<p align="center"><a href="https://github.com/Security-Tools-Alliance/rengine-ng/releases" target="_blank"><img src="https://img.shields.io/badge/version-v2.0.5-informational?&logo=none" alt="reNgine-ng Latest Version" /></a>&nbsp;<a href="https://www.gnu.org/licenses/gpl-3.0" target="_blank"><img src="https://img.shields.io/badge/License-GPLv3-red.svg?&logo=none" alt="License" /></a>&nbsp;<a href="#" target="_blank"><img src="https://img.shields.io/badge/first--timers--only-friendly-blue.svg?&logo=none" alt="" /></a>&nbsp;</p>

<p align="center">
  <img src="https://img.shields.io/badge/Cycom-2024-blue.svg?logo=none" alt="" /></a>
  <a href="https://www.youtube.com/watch?v=Xk_YH83IQgg" target="_blank"><img src="https://img.shields.io/badge/BlackHat--Arsenal--Asia-2023-blue.svg?logo=none" alt="" /></a>&nbsp;
  <a href="https://www.youtube.com/watch?v=Xk_YH83IQgg" target="_blank"><img src="https://img.shields.io/badge/BlackHat--Arsenal--USA-2022-blue.svg?logo=none" alt="" /></a>&nbsp;
  <a href="https://www.youtube.com/watch?v=Xk_YH83IQgg" target="_blank"><img src="https://img.shields.io/badge/Open--Source--Summit-2022-blue.svg?logo=none" alt="" /></a>&nbsp;
  <a href="https://cyberweek.ae/2021/hitb-armory/" target="_blank"><img src="https://img.shields.io/badge/HITB--Armory-2021-blue.svg?logo=none" alt="" /></a>&nbsp;
  <a href="https://www.youtube.com/watch?v=7uvP6MaQOX0" target="_blank"><img src="https://img.shields.io/badge/BlackHat--Arsenal--USA-2021-blue.svg?logo=none" alt="" /></a>&nbsp;
  <a href="https://drive.google.com/file/d/1Bh8lbf-Dztt5ViHJVACyrXMiglyICPQ2/view?usp=sharing" target="_blank"><img src="https://img.shields.io/badge/Defcon--Demolabs--29-2021-blue.svg?logo=none" alt="" /></a>&nbsp;
  <a href="https://www.youtube.com/watch?v=A1oNOIc0h5A" target="_blank"><img src="https://img.shields.io/badge/BlackHat--Arsenal--Europe-2020-blue.svg?&logo=none" alt="" /></a>&nbsp;
</p>

<p align="center">
<a href="https://github.com/Security-Tools-Alliance/rengine-ng/actions/workflows/codeql-analysis.yml" target="_blank"><img src="https://github.com/Security-Tools-Alliance/rengine-ng/actions/workflows/codeql-analysis.yml/badge.svg" alt="" /></a>&nbsp;<a href="https://github.com/Security-Tools-Alliance/rengine-ng/actions/workflows/build.yml" target="_blank"><img src="https://github.com/Security-Tools-Alliance/rengine-ng/actions/workflows/build.yml/badge.svg" alt="" /></a>&nbsp;
</p>

<p align="center">
<a href="https://discord.gg/KE5QGTqJpS" target="_blank"><img src="https://img.shields.io/discord/1227920361564143766" alt="" /></a>&nbsp;
</p>

<p align="center">
<a href="https://opensourcesecurityindex.io/" target="_blank" rel="noopener">
<img style="width: 282px; height: 56px" src="https://opensourcesecurityindex.io/badge.svg" alt="Open Source Security Index - Fastest Growing Open Source Security Projects" width="282" height="56" /> </a>
</p>

# reNgine-ng (Next Generation)

## Why reNgine-ng?

reNgine-ng is a (detached) fork of [reNgine](https://github.com/yogeshojha/rengine).

## What is reNgine-ng?

reNgine-ng is your go-to web application reconnaissance suite that's designed to simplify and streamline the reconnaissance process for security professionals, penetration testers, and bug bounty hunters. With its highly configurable engines, data correlation capabilities, continuous monitoring, database-backed reconnaissance data, and an intuitive user interface, reNgine-ng redefines how you gather critical information about your target web applications.

Traditional reconnaissance tools often fall short in terms of configurability and efficiency. reNgine-ng addresses these shortcomings and emerges as a excellent alternative to existing commercial tools.

reNgine-ng was created to address the limitations of traditional reconnaissance tools and provide a better alternative, even surpassing some commercial offerings. Whether you're a bug bounty hunter, a penetration tester, or a corporate security team, reNgine-ng is your go-to solution for automating and enhancing your information-gathering efforts.

reNgine-ng 2.0 is out now, you can [watch reNgine-ng 2.0 release trailer here!](https://youtu.be/VwkOWqiWW5g)

reNgine-ng 2.0 would not have been possible without [@ocervell](https://github.com/ocervell) valuable contributions. [@ocervell](https://github.com/ocervell) did majority of the refactoring if not all and also added a ton of features. Together, we wish to shape the future of web application reconnaissance, and it's developers like [@ocervell](https://github.com/ocervell) and a [ton of other developers and hackers from our community](https://github.com/Security-Tools-Alliance/rengine-ng/graphs/contributors) who inspire and drive us forward.

Thank you, [@ocervell](https://github.com/ocervell), for your outstanding work and unwavering commitment to reNgine-ng.

Checkout our contributors here: [Contributors](https://github.com/Security-Tools-Alliance/rengine-ng/graphs/contributors)

![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png)

### Documentation

You can find detailed documentation in the repository [Wiki](https://github.com/Security-Tools-Alliance/rengine-ng/wiki)

![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png)

### Table of Contents

* [Workflow](#workflow)
* [Quick Installation](#quick-installation)
* [Updating](#quick-installation)
* [What's new in reNgine-ng 2.0](#changelog)
* [Screenshots](#screenshots)
* [Contributing](#contributing)

![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png)

### Workflow

<img src=".github/images/workflow.png">

![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png)

### Quick Installation

**Note:** Only Ubuntu/VPS

1. Clone this repo

    ```bash
    git clone https://github.com/Security-Tools-Alliance/rengine-ng && cd rengine-ng
    ```

1. Edit the `.env` file, **please make sure to change the password for postgresql `POSTGRES_PASSWORD`!**

    ```bash
    nano .env
    ```

1. **Optional, only for non-interactive install**: In the `.env` file, **please make sure to change the super admin values!**

    ```bash
    DJANGO_SUPERUSER_USERNAME=yourUsername
    DJANGO_SUPERUSER_EMAIL=YourMail@example.com
    DJANGO_SUPERUSER_PASSWORD=yourStrongPassword
    ```
    If you need to carry out a non-interactive installation, you can setup the login, email and password of the web interface admin directly from the .env file (instead of manually setting them from prompts during the installation process). This option can be interesting for automated installation (via ansible, vagrant, etc.).

    `DJANGO_SUPERUSER_USERNAME`: web interface admin username (used to login to the web interface).

    `DJANGO_SUPERUSER_EMAIL`: web interface admin email.

    `DJANGO_SUPERUSER_PASSWORD`: web interface admin password (used to login to the web interface).

1. In the dotenv file, you may also modify the Scaling Configurations

    ```bash
    MAX_CONCURRENCY=30
    MIN_CONCURRENCY=10
    ```

    MAX_CONCURRENCY: This parameter specifies the maximum number of reNgine-ng's concurrent Celery worker processes that can be spawned. In this case, it's set to 80, meaning that the application can utilize up to 80 concurrent worker processes to execute tasks concurrently. This is useful for handling a high volume of scans or when you want to scale up processing power during periods of high demand. If you have more CPU cores, you will need to increase this for maximized performance.

    MIN_CONCURRENCY: On the other hand, MIN_CONCURRENCY specifies the minimum number of concurrent worker processes that should be maintained, even during periods of lower demand. In this example, it's set to 10, which means that even when there are fewer tasks to process, at least 10 worker processes will be kept running. This helps ensure that the application can respond promptly to incoming tasks without the overhead of repeatedly starting and stopping worker processes.

    These settings allow for dynamic scaling of Celery workers, ensuring that the application efficiently manages its workload by adjusting the number of concurrent workers based on the workload's size and complexity.

    Here is the ideal value for `MIN_CONCURRENCY` and `MAX_CONCURRENCY` depending on the number of RAM your machine has:

    * 4GB: `MAX_CONCURRENCY=10`
    * 8GB: `MAX_CONCURRENCY=30`
    * 16GB: `MAX_CONCURRENCY=50`

    This is just an ideal value which developers have tested and tried out and works! But feel free to play around with the values.
    Maximum number of scans is determined by various factors, your network bandwidth, RAM, number of CPUs available. etc

1. Run the installation script, Please keep an eye for any prompt, you will also be asked for username and password for reNgine-ng.

    ```bash
    sudo ./install.sh
    ```

    Or for a non-interactive installation, use `-n` argument (make sure you've modified the `.env` file before launching the installation).

    ```bash
    sudo ./install.sh -n
    ```

    If `install.sh` does not have execution permissions, please grant it execution permissions: `chmod +x install.sh`

Detailed installation instructions can be found at [https://github.com/Security-Tools-Alliance/rengine-ng/wiki/Installation#-quick-installation](https://github.com/Security-Tools-Alliance/rengine-ng/wiki/Installation#-quick-installation)

### Updating

1. Updating is as simple as running the following command:

    ```bash
    cd rengine-ng && sudo ./update.sh
    ```

    If `update.sh` does not have execution permissions, please grant it execution permissions: `sudo chmod +x update.sh`
  
    **NOTE:** if you're updating from 1.3.6 and you're getting a 'password authentication failed' error, consider uninstalling 1.3.6 first, then install 2.x.x as you'd normally do.

Detailed update instructions: <https://github.com/Security-Tools-Alliance/rengine-ng/wiki/Installation#-quick-update>

### Changelog

[Please find the latest release notes and changelog here.](https://github.com/Security-Tools-Alliance/rengine-ng/wiki/changelog/)

![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png)  

### Screenshots

#### Dashboard

![](.github/screenshots/scan_results.gif)

![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png)

### Contributing

See the [Contributing Guide](CONTRIBUTING.md) to get started.

![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png)

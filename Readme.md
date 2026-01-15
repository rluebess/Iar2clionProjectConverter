# IAR to CLion CMake Bridge
## Project converter for Embedded Projects

### Why this project?
While I prefer JetBrains CLion for my daily work, my team continues to use **IAR EWARM**. Since a full migration was not an option, I needed a way to work in both IDEs simultaneously without breaking compatibility for my colleagues. 

I forked this project to create a bridge: it generates a `CMakeLists.txt` file from IAR project files (`.ewp`), allowing me to edit, compile, and debug in CLion while keeping the IAR project as the primary source of truth.

> [!IMPORTANT]
> **CPU Support:** This fork is specifically tailored to and tested with **STR912 series CPUs**. Other architectures have not been tested and may require manual adjustments.

---

### Project Status & Goals
The current version requires some manual environment configuration. My long-term goals for this fork are:
* **Automation:** Automate the remaining manual setup steps within CLion.
* **Synchronization:** Integrate the script into the pre-build process to ensure the CLion environment stays perfectly in sync with the IAR `.ewp` file.

### Disclaimer & Maintenance
**This tool is developed for my personal daily workflow and is provided "as-is".**

* **No Support:** I do not offer technical support or assistance with setup.
* **Scope:** I do not plan to implement features or fixes beyond my own functional requirements.
* **No Affiliation:** This is an independent project. It is **not** affiliated with, sponsored by, or endorsed by IAR Systems AB, JetBrains s.r.o., or STMicroelectronics. All trademarks are the property of their respective owners.

*Developed for personal use to bridge the gap between IAR EWARM and JetBrains CLion.*

---

## Module description

- [cmake.py](cmake.py) - Cmake and linker file generation
- [converter.py](converter.py) - Argument parsing
- [ewpproject.py](ewpproject) - Parser for IAR's ewp file format
- [uvprojx.py](uvprojx.py) - Parser for ARM's KEIL uvprojx file format

## Prerequisites

Install `python3` on your system run:
```shell
pip install Jinja2
```

## Usage

Run in output dir.

To convert project:

```
    python converter.py <project type> <path to project root> <target compiler>
```

project type: "ewp" or "uvprojx"
target compiler: "iar" or "clang"

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](semver.org) for versioning.

## Authors

- Petr Hodina - *Initial work*
- Dennisonius - *added more functions*

## License

The project is licensed under the [Apache License v2.0](https://www.apache.org/licenses/LICENSE-2.0) - see the [LICENSE.md](LICENSE.md) file for details.

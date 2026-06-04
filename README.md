# OCT Control Suite

Desktop application for controlling and synchronizing laboratory hardware components including:

* NI-DAQ devices
* NKT laser systems
* Thorlabs K-Cube controllers
* Stepper motor stages
* OCT imaging devices
* Recording and synchronization workflows

The software follows a modular architecture with separated UI, controller, driver, and core logic layers to simplify maintenance and future hardware integrations.

---

## Features

* Modular hardware abstraction
* Multi-device synchronization
* NI-DAQ analog input/output control
* NKT laser control and safety shutdown
* Thorlabs K-Cube integration
* Stepper motor control
* OCT imaging support
* Recording management
* Configuration-driven setup
* Automated testing with PyTest


## Hardware
Stepper
200 Microsteps
1/16 Microstepping with TMC2209
-> 3200 Steps/Rev

Stage
-> 1 mm/Rev

--> 3200 Steps == 1 Rev == 1 mm

---

## Project Structure

```text
.
├── app.py                      # Application bootstrap and dependency wiring
├── main.py                     # Application entry point
├── requirements.txt
├── pytest.ini
│
├── controllers/                # High-level device controllers
│   ├── kcube_controller.py
│   ├── nidaq_controller.py
│   ├── nkt_controller.py
│   ├── oct_controller.py
│   ├── record_manager.py
│   ├── stepper_controller.py
│   └── sync_controller.py
│
├── core/                       # Application core services
│   ├── app_state.py
│   └── config_manager.py
│
├── driver/                     # Hardware-specific drivers
│   ├── calibration.py
│   ├── kinesis.py
│   ├── nidaq.py
│   ├── nkt.py
│   ├── oct_imaging.py
│   ├── pi_gcs_devices.py
│   ├── pi_stage_logic.py
│   └── stepper.py
│
├── models/
│   └── stepper_status.py
│
├── ui/                         # Tkinter user interface
│   ├── footer_frame.py
│   ├── kcube_frame.py
│   ├── main_window.py
│   ├── nidaq_frame.py
│   ├── nkt_frame.py
│   ├── recording_frame.py
│   ├── stepper_frame.py
│   └── sync_frame.py
│
├── utils/
│   ├── fileIO.py
│   ├── image_loader.py
│   ├── led.py
│   ├── led_widget.py
│   ├── pluginmanager.py
│   └── version.py
│
├── resources/
│   ├── config.json
│   ├── *.png
│   ├── *.ico
│   └── *.drawio
│
├── tests/
│   ├── conftest.py
│   ├── test_check_config.py
│   ├── test_fileio.py
│   ├── test_kcube_controller.py
│   ├── test_oct_imaging.py
│   ├── test_pluginmanager.py
│   └── test_recording_frame.py
│
└── doc/
    └── GIT Best Practice README.md
```

---

## Architecture

```text
UI Layer
    │
    ▼
Controllers
    │
    ▼
Drivers
    │
    ▼
Hardware
```

### UI

Responsible for user interaction and visualization.

### Controllers

Contain application logic and coordinate communication between UI and hardware drivers.

### Drivers

Provide low-level hardware communication and vendor SDK integration.

### Core

Contains configuration management and shared application state.

---

## Installation

### Clone Repository

```bash
git clone https://github.com/<user>/<repository>.git
cd <repository>
```

### Create Virtual Environment

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configuration

Application settings are stored in:

```text
resources/config.json
```

Typical configuration sections include:

```json
{
  "devices": {},
  "nidaq": {},
  "stepper": {},
  "nkt": {},
  "kcube": {}
}
```

Adjust the configuration to match your laboratory hardware setup before launching the application.

---

## Running the Application

```bash
python main.py
```

---

## Running Tests

Execute all tests:

```bash
pytest
```

Run with verbose output:

```bash
pytest -v
```

Run a specific test:

```bash
pytest tests/test_kcube_controller.py
```

---

## Safety Features

The application includes emergency shutdown mechanisms for connected hardware.

Implemented safeguards include:

* Automatic NKT laser shutdown on unexpected application exit
* Exception-triggered emergency shutdown
* Graceful application termination handlers

---

## Development

Recommended workflow:

```bash
main
 └── dev
      ├── feature/*
      ├── bugfix/*
      └── release/*
```

Example:

```bash
git checkout dev
git checkout -b feature/new-stage-control
```

---

## Building an Executable

The project contains an AutoPyToExe configuration:

```text
AutoPYToExe.json
```

Generate a standalone executable:

```bash
auto-py-to-exe
```

Load the supplied configuration and build.

---

## License

Specify your license here.

Example:

```text
MIT License
```

---

## Author

Developed for laboratory automation, motion control, and OCT system integration.





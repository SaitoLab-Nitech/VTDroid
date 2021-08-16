# VTDroid

VTDroid is a taint analysis tool for Android app analysis. Currently, VTDroid is built for privacy leak detection. We presented VTDroid and our [test suite](https://github.com/SaitoLab-Nitech/ATATechniques) at [ARES 2021](https://www.ares-conference.eu/). When you reference this work, please cite our paper by the following:

- Hiroki Inayoshi, Shohei Kakei, Eiji Takimoto, Koichi Mouri, and Shoichi Saito. 2021. VTDroid: Value-based Tracking for Overcoming Anti-Taint-Analysis Techniques in Android Apps. In The 16th International Conference on Availability, Reliability and Security (ARES 2021), August 17–20, 2021, Vienna, Austria. ACM, New York, NY, USA, 6 pages. https://doi.org/10.1145/3465481.3465759

## Setup

### Requirements
- Python 3.6 or later
- VTDroid uses the following tools:
    - adb
    - aapt
    - apktool
    - jarsigner
    - tesseract

All paths of the tools are configured in parameters_*.json in VTDroid/smalien/parameters/.

### Key Preparation

Generate a key for VTDroid to sign apks.

Steps

1. Generate a private key with keytool

```
$ keytool -genkey -v -keystore <file_name> -alias <key_alias> -keyalg RSA -validity 25
```

2. Create a directory ```VTDroid/key/``` and create a file ```VTDroid/key/keystore_conf.txt``` with the following contents:

```
<path_to_your_key>
<keystore_password>
<key_password>
<key_alias_name>
```

## Usage

VTDroid analyzes an app by three phases: static bytecode instrumentation, app exercising, and information flow analysis.

### Static Bytecode Instrumentation

Go to VTDroid/ and run the command below. This phase requires the key explained above, so please prepare your key before running the command.

```
python3 -m smalien.main -u -a -p <path_to_parameter_file> <path_to_workspace> <path_to_apk>
```

When you get an error, please make sure that your <path_to_workspace> is an empty directory or does not exist, and try again.

### App Exercising

After the static bytecode instrumentation, go to <path_to_workspace> and run the commands below.

```
# Check your device is connected and no log file remains on your device
$ adb devices
$ adb shell rm /sdcard/SmalienLog.txt

# Install target's implanted apk
$ adb install -g <path_to_implanted_apk>

# Launch the app by tapping its icon on screen and exercise the app

# Obtain the log file generated
$ adb pull /sdcard/SmalienLog.txt
```

Failing to obtain the log file means VTDroid fails to analyze your app. Send me your app if possible, and I will find and fix the problem.

### Information Flow Analysis

Go to VTDroid/ and run the command below.

```
python3 -m smalien.main -t <path_to_parameter_file> <path_to_workspace> <path_to_apk>
```

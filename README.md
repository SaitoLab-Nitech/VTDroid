# VTDroid

VTDroid is a taint analysis tool for Android app analysis. Currently, VTDroid is built for privacy leak detection. We presented VTDroid and our [test suite](https://github.com/SaitoLab-Nitech/ATATechniques) at [ARES 2021](https://www.ares-conference.eu/). When you reference this work, please cite our paper by the following:

- Hiroki Inayoshi, Shohei Kakei, Eiji Takimoto, Koichi Mouri, and Shoichi Saito. 2021. VTDroid: Value-based Tracking for Overcoming Anti-Taint-Analysis Techniques in Android Apps. In The 16th International Conference on Availability, Reliability and Security (ARES 2021), August 17–20, 2021, Vienna, Austria. ACM, New York, NY, USA, 6 pages. https://doi.org/10.1145/3465481.3465759

## Setup

### Requirements
- Python 3.6 or later
- Python modules
    - psutil
- VTDroid uses the following tools:
    - adb
    - aapt
    - apktool
    - jarsigner
    - tesseract

All paths of the tools are configured in parameters_*.json in VTDroid/smalien/parameters/.

### Key Preparation

Generate a key for VTDroid to sign apks.

#### Steps

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

## Example

Our [test suite](https://github.com/SaitoLab-Nitech/ATATechniques)'s apks, static-analysis results, and app-exercising results are archived in VTDroid/workspace_ts_pld/. Hence, you can try VTDroid's information flow analysis without an Android device and all the above requirements except python and tesseract.

For example, run VTDroid with da_text_scaling as follows:

1. Unzip the target

```
$ cd VTDroid/workspace_ts_pld/
$ unzip da_text_scaling.zip
```

2. Go to VTDroid/ and run the command

```
$ python3 -m smalien.main -t smalien/parameters/parameters_ts_pld_ifa.json workspace_ts_pld/da_text_scaling/ workspace_ts_pld/da_text_scaling/da_text_scaling.apk
```

3. VTDroid outputs several lines, including the following lines

- A line indicating that the app loads IMEI, and the following line shows the actual value, which is our experiment device's IMEI

```
[ SOURCE_API ] 47_141_v6, ./workspace_ts_pld//20_da_text_scaling/da_text_scaling/smali/com/inayoshi/atatechniques/MainActivity.smali, IMEI1, move-result, [ TIME ] analysis: 0.0015494823455810547, app: 0.114
  [ RET ] v6, 357681080471044
```

- A line indicating that the app executes a sink
    - The line starting with "[ ATA_FLOW ]" describes that our taint propagation rule 8, 9, 7, 6, 1, 3, and 4 are used, and one direct-assignment flow is detected 

```
[ SINK ] 37_188_p1, Ljava/io/BufferedWriter; -> write(Ljava/lang/String;)V ( param: p1) in ./workspace_ts_pld//20_da_text_scaling/da_text_scaling/smali/com/inayoshi/atatechniques/Server.smali

  [ TIME ] analysis: 0.021704435348510742 app: 0.172
  [ TAINT_FOUND ] [2, {'IMEI1'}, {'37_109_v0'}]
  [ ATA_FLOW ] ['R8-9', 'R7', "DA: 19_56_v3 -> 19_73_v4 ['19_73_v4', 73, 'v4']", 'R6', 'R1', 'R3', 'R4']
  [ VALUE ] Data from client: 357681080471044
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
# Check your device is connected, and no log file remains on your device
$ adb devices
$ adb shell rm /sdcard/SmalienLog.txt

# Install target's implanted apk
$ adb install -g <path_to_implanted_apk>

# Launch the app by tapping its icon on the device's screen and exercise the app

# Obtain the log file generated
$ adb pull /sdcard/SmalienLog.txt
```

Failing to obtain the log file means VTDroid fails to analyze your app. Send me your app if possible, and I will find and fix the problem.

### Information Flow Analysis

Go to VTDroid/ and run the command below.

```
python3 -m smalien.main -t <path_to_parameter_file> <path_to_workspace> <path_to_apk>
```

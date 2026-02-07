[app]

# (str) Title of your application
title = Quran Reels Generator

# (str) Package name
package.name = quranreels

# (str) Package domain (needed for android/ios packaging)
package.domain = com.arabianaischool

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf,mp4,txt

# (list) List of inclusions using pattern matching
source.include_patterns = fonts/*,vision/*,*.ttf,*.mp4

# (list) Source files to exclude (let empty to not exclude anything)
source.exclude_exts = spec,sdl2,exe,msi

# (list) List of directory to exclude (let empty to not exclude anything)
source.exclude_dirs = tests, bin, venv, .venv, env, .env, .git, .github, dist, build

# (list) List of exclusions using pattern matching
source.exclude_patterns = license,images/*/*.jpg

# (str) Application versioning (method 1)
version = 1.0.0

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.2.1,requests,pydub,moviepy==1.0.3,pillow,numpy,urllib3,charset-normalizer,certifi,idna,imageio,imageio-ffmpeg,tqdm,proglog,decorator

# (str) Custom source folders for requirements
# Sets custom source for any requirements with recipes
# requirements.source.kivy = ../../kivy

# (list) Garden requirements
#garden_requirements =

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (list) Supported orientations
# Valid options are: landscape, portrait, portrait-reverse, landscape-reverse
orientation = portrait

# (list) List of services to declare
#services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

#
# OSX Specific
#

#
# author = © Copyright Info

# change the major version of python used by the app
osx.python_version = 3

# Kivy version to use
osx.kivy_version = 1.9.1

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (string) Presplash background color (for android toolchain)
android.presplash_color = #1c031d

# (string) Presplash background color (for new android toolchain)
#android.presplash_color = #FFFFFF

# (list) Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (list) features (adds uses-feature -tags to manifest)
#android.features = android.hardware.usb.host

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 33

# (str) Android NDK version to use
android.ndk = 25b

# (int) Android NDK API to use. This is the minimum API your app will support, it should usually match android.minapi.
android.ndk_api = 21

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Android app entry point, default is ok for Kivy-based app
#android.entrypoint = org.kivy.android.PythonActivity

# (str) Full name including package path of the Java class that implements Android Activity
# use that parameter if you want to replace the default MainActivity
#android.activity_class_name = org.kivy.android.PythonActivity

# (str) Extra xml to write directly inside the <manifest> element of AndroidManifest.xml
# use that parameter to provide a filename from where to load your custom XML code
#android.extra_manifest_xml = ./src/android/extra_manifest.xml

# (str) Extra xml to write directly inside the <manifest><application> tag of AndroidManifest.xml
# use that parameter to provide a filename from where to load your custom XML code
#android.extra_manifest_application_arguments = ./src/android/extra_manifest_application_arguments.xml

# (str) Full path to a custom JavaActivity.java file to use
#android.add_activity = ./src/android/JavaActivity.java

# (str) Extra arguments to be passed to the gradle build command
# android.gradle_options =

# (bool) If True, then skip trying to run android debug binary and go straight to gradle
# android.force_gradle_build = False

# (str) Path to a custom proguard filter file for Android builds
# android.proguard_filter =

# (str) Path to a custom gradle.properties template for Android builds
# android.gradle_properties_template =

# (str) Path to a custom AndroidManifest.xml template file for Android builds
# android.manifest_template =

# (str) Path to a custom ant.properties template file for Android builds
# android.ant_properties =

# (bool) If True, then skip trying to run android debug binary and go straight to gradle
# android.no_debug = False

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (bool) Android logcat only display log for activity org.kivy.android.PythonActivity
android.logcat_only_activity = True

# (str) Android additional build dependencies
# android.gradle_dependencies =

# (bool) Turn on debugging for Android builds
android.debuggable = False

# (int) Maximum heap size for Java VM (for gradle builds)
android.gradle_heap_size = 4G

# (bool) Convert icons to mipmap
#android.mipmap_icon = True

# (str) Android entry point for the application (default is org.kivy.android.PythonActivity)
# android.entrypoint = org.kivy.android.PythonActivity

# (str) Android app theme (default is @android:style/Theme.NoTitleBar)
# android.apptheme = "@android:style/Theme.NoTitleBar"

# (list) Pattern to whitelist for the whole project
# android.whitelist =

# (str) Path to the android arch
# android.arch = armeabi-v7a

# (list) The Android archs to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
# In past, was `android.arch` as we weren't supporting multi-archs builds
android.archs = arm64-v8a, armeabi-v7a

# (int) overrides automatic versionCode computation (used in build.gradle)
# this is not the same as app version and should only be edited if you know what you're doing
# android.numeric_version = 1

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (str) XML file for auto backup rules (Android API >= 23)
# android.backup_rules =

# (str) If you need to insert variables into your AndroidManifest.xml file,
# you can do so with the android.manifest_placeholders property.
# This property takes a map of key-value pairs. (via a string)
# Usage example : android.manifest_placeholders = [my_custom_url:http://example.org/]
# android.manifest_placeholders = [:]

# (bool) disables the compilation of py to pyc/pyo files when packaging
# android.no-compile-pyo = True

# (str) The format used to package the app for release mode (aab or apk or aar).
android.release_artifact = aab

# (str) The format used to package the app for debug mode (apk or aar).
android.debug_artifact = apk

#
# Python for android (p4a) specific
#

# (str) python-for-android URL to use for checkout
#p4a.url =

# (str) python-for-android fork to use in case if p4a.url is not specified, defaults to upstream (kivy)
#p4a.fork = kivy

# (str) python-for-android branch to use, defaults to master
#p4a.branch = master

# (str) python-for-android specific commit to use, defaults to HEAD, must be within p4a.branch
#p4a.commit = HEAD

# (str) python-for-android git clone directory (if empty, it will be automatically cloned from github)
#p4a.source_dir =

# (str) The directory in which python-for-android should look for your own build recipes
# (if empty, it will look for build recipes in python-for-android/recipes)
# p4a.local_recipes =

# (str) Filename to the hook for p4a
#p4a.hook =

# (str) Bootstrap to use for android builds (android_new is recommended)
p4a.bootstrap = sdl2

# (int) port number to specify an explicit --port= p4a argument (eg for bootstrap flask/webview)
#p4a.port =

# Control passing the --use-setup-py vs --ignore-setup-py to p4a
# In the past, providing an empty p4a.source_dir would enable --use-setup-py by default
#p4a.use_setup_py = True

# (str) extra command line arguments to pass when invoking p4a
#p4a.extra_args =


#
# iOS specific
#

# (str) Path to a custom source for the ios toolchain (default is the pre-built toolchain)
# ios.toolchain_dir = ~/build/kivy-ios

# (str) Name of the certificate to use for signing the debug version of the app (ios only)
#ios.codesign.debug = "iPhone Developer: <lastname> <firstname> (<hexstring>)"

# (str) Name of the certificate to use for signing the release version of the app (ios only)
#ios.codesign.release = %(ios.codesign.debug)s


[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab, .ipa) storage
# bin_dir = ./bin

#    -----------------------------------------------------------------------------
#    List as sections
#
#    You can define all the "list" as [section:key].
#    Each line will be considered as an option to the list.
#    Let's take [app] / source.exclude_patterns.
#    Instead of doing:
#
#[app]
#source.exclude_patterns = license,data/audio/*.wav,data/images/original/*
#
#    This can be translated into:
#
#[app:source.exclude_patterns]
#license
#data/audio/*.wav
#data/images/original/*
#


#    -----------------------------------------------------------------------------
#    Profiles
#
#    You can extend section / key with a profile
#    For example, you want to deploy a demo version of your application without
#    HD content. You could first change the title to add "(demo)" in the name
#    and extend the excluded directories to remove the HD content.
#
#[app@demo]
#title = My Application (demo)
#
#[app:source.exclude_patterns@demo]
#images/hd/*
#
#    Then, invoke the command line with the "demo" profile:
#
#buildozer --profile demo android debug

# iograft for Autodesk Maya

This repository contains scripts and nodes for running iograft within Autodesk Maya. It includes a Maya Subcore command, an iograft Plugin for Maya, and a few example iograft Maya nodes.

## Getting Started with a Maya Environment

Below are the steps required to setup a new environment in iograft for executing nodes in Maya. These steps are also available in the
iograft [Environment Quick Start Guide](https://docs.iograft.com/getting-started/guides/creating-a-new-environment):

1. Clone the iograft-maya repository.
2. Open the iograft Environment Manager and create a new environment for Maya (i.e. "maya2022").
3. Add the "nodes" directory of the iograft-maya repository to the **Plugin Path**.
4. Update the **Subcore Launch Command** to "iogmaya_subcore" (matching the subcore executor name in the bin folder of the iograft-maya repository). Note: On Windows this will automatically resolve to the "iogmaya_subcore.bat" script.
5. Add the "bin" directory of the iograft-maya respository to the **Path**.
6. Add Maya's "bin" directory to the **Path** (the directory containing the Maya executable and the mayapy executable).
7. Add the "python" directory of the iograft-maya respository to the **Python Path**.
8. Depending on the version of Maya, update the **Python Path** entry for `...\iograft\python39` by switching "python39" to the directory for the correct version of Python. (For Maya 2020: "python27"; for Maya 2022: "python37").
9. OPTIONAL: Add an **Environment Variable** for the `MAYA_PLUG_IN_PATH` so the iograft Maya plugin is available within Maya: Key: `MAYA_PLUG_IN_PATH`, Value: the path to the "plugins" directory of the iograft-maya repository.
10. Save the environment, use the Environment menu to switch to the Maya environment just created, and start creating Maya nodes.

## Maya Subcore for iograft

The Maya Subcore for iograft (`iogmaya_subcore`) defines an iograft Subcore for executing nodes in the Maya environment.

The main components of the Maya Subcore are:
- Calls `maya.standalone.initialize()` to initialize the Maya environment prior to listening for node processing requests,
- Calls `maya.standalone.uninitialize()` prior to exiting, and
- Uses the `iograft.MainThreadSubcore` class to ensure that all nodes are executed in the main thread.


## iograft Plugin for Maya

The iograft Plugin for Maya (iograftmaya.py) allows iograft to be run from inside an interactive Maya session. The plugin registers 3 MEL commands:

1. `start_iograft` -
Used to initialize a local iograft session within Maya. Starts an iograft Core using the builtin Maya Python interpreter. A UI session can be connected to this iograft Core for graph authoring and monitoring.

2. `stop_iograft` -
Used to shutdown the iograft session within Maya.

3. `iograft_ui` -
Launch the iograft UI as a subprocess and connect to the iograft Core running inside of Maya. Note: The UI runs in a completely separate process and not internally in Maya. Only the iograft Core runs inside of Maya.

*Note: The plugin also registers an iograft shelf named "iograft" which includes buttons that wrap the three commands listed above.*

All other operations for interacting with the Core object should be completed using the iograft Python API.

When `start_iograft` is executed, it registers a Core named "maya" that can be retrieved with the Python API as shown below:

```python
import iograft
core = iograft.GetCore("maya")
```

Using the Python API, we have access to useful functionality on the Core such as loading graphs, setting input values on a graph, and processing the graph.

## Launching Maya with an iograft Environment Set

To launch Maya and set the environment so iograft can run, we need to let iograft know which environment we are in. This can be done either by launching Maya using `iograft_env` or by initializing the environment in a Maya userSetup.py script:

### iograft_env

`iograft_env -e maya2020 -c maya`

The iograft_env command first initializes environment variables based on the settings from the iograft environment named "maya2020", and then launches Maya.

*Note: iograft_env does not have to be used to start Maya, but it is quick way to ensure that the environment you are running in matches one of your defined iograft environments. If you prefer, you could setup the environment manually and simply set the IOGRAFT_ENV environment variable to the name of the iograft environment you set. The important thing is that we tell iograft which environment we are currently in.*

### userSetup.py

Starting in iograft version 0.9.6, we have access to the `iograft.InitializeEnvironment(environment_name)` API call. This call initializes all of the environment variables based on the settings from an iograft environment in the current Python session. This function can be used within Maya's userSetup.py script to configure Maya to use iograft:

```python
# Ensure that the iograft python modules can be found.
# NOTE: This path can also be set in a Maya.env file.
import os
import sys
IOGRAFT_PYTHON_PATH = "C:/Program Files/iograft/python27"
if IOGRAFT_PYTHON_PATH not in sys.path:
    sys.path.append(IOGRAFT_PYTHON_PATH)

# Initialize an environment named "maya2020"
import iograft
environment_name = "maya2020"
try:
    iograft.InitializeEnvironment(environment_name)
except KeyError as e:
    print("Failed to initialize iograft environment: {}: {}".format(
                                                        environment_name, e))

# Ensure that the MAYA_PLUG_IN_PATH contains the plugins directory of the
# iograft-maya repository.
# NOTE: This can also be set in a Maya.env file.
plugin_paths = os.environ.get("MAYA_PLUG_IN_PATH", "").split(";")
IOGRAFT_MAYA_PLUGIN_PATH = "C:/Users/dtkno/Projects/iograft-public/iograft-maya/plugins"
if IOGRAFT_MAYA_PLUGIN_PATH not in plugin_paths:
    plugin_paths.append(IOGRAFT_MAYA_PLUGIN_PATH)
    os.environ["MAYA_PLUG_IN_PATH"] = ";".join(plugin_paths)
```

Initializing iograft using this method has the benefit that Maya can be launched without needing the wrapper `iograft_env` script (i.e. via an Application icon click).

Note: importing iograft in the userSetup.py requires that the iograft python modules are on the current PYTHONPATH. In addition, on Windows the PATH must contain the iograft 'bin' directory. Some possible options for setting this state is either to update the PATH and PYTHONPATH in a **Maya.env** file, within the userSetup.py script itself, or globally in the system's environment variables.


## Threading in Maya

Some of the available Maya Python commands are expected to be run in the main thread (or else there is the possibility for errors and undefined behavior). As a result, iograft's default threaded node execution is not ideal.

To get around any threading issues, there are a couple of additions we can make to the Maya scripts and nodes. The cool thing about these additions is they require NO changes to iograft's code. All of the required modifications can happen in the user's node and subcore code:

1. Nodes that execute Maya commands that may be unsafe in a threaded environment must apply the `@maya_main_thread` decorator to their `Process` function. When running iograft interactively in Maya, this decorator makes use of Maya's `executeInMainThreadWithResult` function to process the node in Maya's main thread.

2. To avoid blocking the main thread when processing graphs in an interactive Maya session, processing must be started with either the `StartGraphProcessing()` function which is non-blocking, or pass the `execute_in_main_thread` argument to `ProcessGraph(execute_in_main_thread=True)` to ensure that nodes that require the main thread can be completed successfully.

3. When processing Maya nodes in batch (i.e. when using the Maya Subcore), the `iogmaya_subcore` executes all nodes in the main thread. To do this, it makes use of the `iograft.MainThreadSubcore` class which runs the primary `iograft.Subcore.ListenForWork` listener in a secondary thread while processing nodes in the main thread.

*Note: In practice, not all nodes need to be executed in the main thread, so hypothetically it would be possible to only execute certain nodes in the main thread, but for simplicity we execute all nodes in the main thread for now.*

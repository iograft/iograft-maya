# iograft for Autodesk Maya

This repository contains scripts and nodes for running iograft within Autodesk Maya. It includes a Maya Subcore command, an iograft Plugin for Maya, and a few example iograft Maya nodes.

## Getting Started with a Maya Environment

Below are the steps required to setup a new environment in iograft for executing nodes in Maya. These steps are also available in the
iograft [Environment Quick Start Guide](https://docs.iograft.com/getting-started/guides/creating-a-new-environment):

1. Clone the iograft-maya repository.
2. Open the iograft Environment Manager and create a new environment for Maya (i.e. "maya2022").
3. Update the **Plugin Path** to include the "nodes" directory of the iograft-maya repository.
4. Update the **Subcore Launch Command** to "iogmaya_subcore" (matching the subcore executor name in the bin folder of the iograft-maya repository). Note: On Windows this will automatically resolve to the "iogmaya_subcore.bat" script.
5. Update the **Path** to include the "bin" directory of the iograft-maya repository.
6. Update the **Path** to include the directory containing the Maya executable and the mayapy executable.
7. Update the **Python Path** to include the "python" directory of the iograft-maya repository.
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

The following commands are used to interact with the state of the iograft Core.
These are loose wrappers around the Core's Python API that allow for
calling those function's on the iograft Core object running within Maya.

4. `iograft_load` -
Used to load a graph file into the iograft Core. Loose wrapper around the `iograft.Core.LoadGraph` function. Takes a single argument which is the path to the .iog file to load. Ex: `iograft_load -f /path/to/file.iog`

5. `iograft_set_input` -
Used to set the "user" input value for a node within the loaded graph. Loose wrapper around the `iograft.Core.SetNodeInputValue` function. Takes three arguments:
  - `-n/-nodename` - Name of the node to set the value on.
  - `-i/-inputname` - Name of the input to set the value on.
  - `-v/-value` - String representation of the value to set for the node input. This will be converted (if possible) to the correct underlying type.

6. `iograft_execute` -
Start the execution of the loaded graph.


## Launching Maya with an iograft Environment Set

To launch Maya and set the environment so iograft can run, we need to let iograft know which environment we are in. This can be done by launching Maya using `iograft_env`:

`iograft_env -e maya2020 -c maya`

The iograft_env command first initializes environment variables based on the settings from the iograft environment named "maya2020", and then launches Maya.

Note: iograft_env does not have to be used to start Maya, but it is quick way to ensure that the environment you are running in matches one of your defined iograft environments. If you prefer, you could setup the environment manually and simply set the IOGRAFT_ENV environment variable to the name of the iograft environment you set. The important thing is that we tell iograft which environment we are currently in.


## Threading in Maya

Some of the available Maya Python commands are expected to be run in the main thread (or else there is the possibility for errors and undefined behavior). As a result, iograft's default threaded node execution is not ideal.

To get around any threading issues, there are a couple of additions we can make to the Maya scripts and nodes. The cool thing about these additions is they require NO changes to iograft's code. All of the required modifications can happen in the user's node and subcore code:

1. Nodes that execute Maya commands that may be unsafe in a threaded environment must apply the `@maya_main_thread` decorator to their `Process` function. When running iograft interactively in Maya, this decorator makes use of Maya's `executeInMainThreadWithResult` function to process the node in Maya's main thread.

2. When processing Maya nodes in batch (i.e. when using the Maya Subcore), the `iogmaya_subcore` executes all nodes in the main thread. To do this, it makes use of the `iograft.MainThreadSubcore` class which runs the primary `iograft.Subcore.ListenForWork` listener in a secondary thread while processing nodes in the main thread.

*Note: In practice, not all nodes need to be executed in the main thread, so hypothetically it would be possible to only execute certain nodes in the main thread, but for simplicity we execute all nodes in the main thread for now.*

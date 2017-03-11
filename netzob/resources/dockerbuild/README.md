# README 

This is the official repository for the netzob project. You can learn more about it [here](https://github.com/netzob/netzob)

## Simple Examples 

Here are simple example showing how to run netzob from a container:

- Simply load netzob: `docker run --rm -it netzob/netzob`
- Load netzob with your current directory mounted at /data: `docker run --rm -it -v $(pwd):/data netzob/netzob`
- Have a command line to be able to navigate into the system, look at the code, modify it: `docker run --rm -it netzob/netzob bash`


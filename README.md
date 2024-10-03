# Monofy: Multi-Process Docker Containers

This Python script is designed to manage multiple processes within a single Docker
container, ensuring they are started, monitored, and terminated together.

This approach is useful when the processes are tightly integrated and need to operate
in unison.

### TL;DR

In your Docker file, include:

```
RUN pip install monofy

CMD ["monofy", "child-command-1", "--param-for-1", "|||", "child-command-2", "--param-for-2"]
```

### Rationale

Running multiple processes in a single Docker container is often discouraged.
However, when processes are closely connected and need to work together, this
approach can simplify deployment and maintenance.

This script provides a Python-based solution to manage such processes efficiently
within a single container, without adding unnecessary complexity. [Read more about
why this is a great idea](https://www.bugsink.com/multi-process-docker-images/)

### Features

* **Unified Process Management**: Starts and manages multiple processes as children
  of a single parent process.

* **Connected fates**: If one child process exits, terminate all others.

* **Signal Handling**: Forwards relevant signals (e.g., `SIGINT`, `SIGTERM`) to all
  child processes.

* **Unified Output**: Consolidates the output (stdout, stderr) of all child
  processes.

* **Graceful Shutdown**: Ensure the parent process waits for all children to exit
  before shutting down.

* **Variable Substition**: Substitute variables from the command line because [Docker
  can't be bothered to do so itself](https://github.com/moby/moby/issues/5509)

### Installation

To use this script, clone the repository or install via your preferred method:

```
pip install monofy
```

### Usage

You can use this script to start and manage multiple processes in a Docker container.

The commands for the processes and their own arguments should be passed as arguments 
should be passed as arguments to `monofy`, separated by the literal string `|||`.

You can also provide "pre commands", one or more commands to run before the parallel
processes are started, usually to perform setup tasks like checking the environment.
Such pre-commands should be separated by `&&`.

### Examples

Launch two commands in parallel, with connected fates (death of one kills the other):

```
monofy child-command-1 --param-for-1 '|||' child-command-2 --param-for-2
```

(Note the single quotes around the operators, which ensure they are not parsed by
your shell, but are instead passed on to `monofy`)

Launch some "pre commands" before launching two commands in parallel:

```
monofy pre-command-1 --foo=bar '&&' child-command-1 param-for-that '|||' child-command-2 -v
```

### Example Dockerfile

Here’s how you might use this script in a Dockerfile:

```
FROM [..]

RUN pip install monofy

CMD ["monofy", "check-install", "--deploy", "&&", "web-server", "0.0.0.0:8000", "|||", "background-process", "-v"]
```

It's possible to pass-in a different combination of commands to start on the invocation of `docker run`:

```
docker run -it my-image monofy check-install --deploy '&&' web-server 0.0.0.0:1234 '|||' background-process -vvvv
```

### Usage outside Docker

This package was written with (the limitations of) Docker in mind, but it can also be
used in other contexts. One thing I found useful is to use it to start multiple
development-related processes in a single line. The property that the death of one
process takes down the others is very useful in reducing confusion if only a part of
your set of tools goes down. 

### Alternatives

Use a process manager, like:

* [supervisord](https://docs.docker.com/engine/containers/multi-service_container/#use-a-process-manager). 
* [honcho](https://honcho.readthedocs.io/en/latest/)
* [Chaperone](http://chaperone.io/)
* [s6](http://skarnet.org/software/s6/overview.html)

However, these tools are often more complex and require additional configuration. They also come with the subtle
drawback that it is not possible to change the command to execute when running `docker run` (because they read config
files to determine which commands to start, rather than taking that info from the command-line).

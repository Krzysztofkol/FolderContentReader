# FolderContentReader

Working with coding large multimodal models makes it extremely easy to write and troubleshoot code. Here I present FolderContentReader - a python script that, if ran in a folder, generates a text file consisting of:

  1. tree visualisation of the folder contents, including all of its subfolders
  2. the content of files containing text

This allows one to generate a written description of the entire directory and feed it into large language model. It allows AI assistant to provide more relevant help and expand upon all of the code multistructurally.

To use it, one can navigate to the folder in command line and type:

`python folder-content-reader.py`

Alternatively, you can use a python script for generating shortened prompt template:

`python generate-prompt-template.py`

The former lists contents of all files containing texts, whereas the latter skips some formats and adds markdown formatting useful for instructing large language models.

Also, if you work with large multimodal models, I highly recommend attaching screenshot of frontend/UI where possible or applicable.

I used Claude-3.5-Sonnet on https://claude.ai/ to generate the python script and tested it on my pc.
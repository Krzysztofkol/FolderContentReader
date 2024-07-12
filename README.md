# FolderContentReader

Working with coding large multimodal models makes it extremely easy to write and troubleshoot code. Here I present FolderContentReader - a python script that, if ran in a folder, generates a text file consisting of:
  1. tree visualisation of the folder contents, including all of its subfolders
  2. the content of files containing text

This allows one to generate a written description of the entire directory and feed it into large multimodal model. It allows AI assistant to provide more relevant help and expand upon all of the code multistructurally.

To use it, one can navigate to the folder in command line and type:
`python folder-content-reader.py`

I used Claude-3.5-Sonnet on https://claude.ai/ to generate the python script and tested it on my pc.

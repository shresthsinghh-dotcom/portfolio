#!/bin/bash

# Convert philosophy markdown files to HTML
pandoc philosophy/README.md -o philosophy/README.html
pandoc philosophy/presocratics.md -o philosophy/presocratics.html
pandoc philosophy/socratic-dialogues.md -o philosophy/socratic-dialogues.html

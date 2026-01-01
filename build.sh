#!/bin/bash

# Convert philosophy markdown files to HTML
pandoc philosophy/README.md \
  --template pandoc-template.html \
  -o philosophy/README.html

pandoc philosophy/presocratics.md \
  --template pandoc-template.html \
  -o philosophy/presocratics.html

pandoc philosophy/socratic-dialogues.md \
  --template pandoc-template.html \
  -o philosophy/socratic-dialogues.html


#!/bin/bash
curl -F "file=@$1" http://localhost:5001/upload

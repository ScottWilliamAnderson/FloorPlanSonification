#!/bin/bash

# Run tests using docker-compose
docker-compose exec app uv run tests.py

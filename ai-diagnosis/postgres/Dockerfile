# Use the official PostgreSQL 16 image as the base
FROM postgres:16

# Copy the SQL initialization script to the entrypoint directory.
# Scripts in this directory are automatically executed when the container starts for the first time.
COPY ./init.sql /docker-entrypoint-initdb.d/init.sql
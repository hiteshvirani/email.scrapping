
# Email Scraper with Docker

Welcome to the Email Scraper project! This repository provides a robust solution for scraping emails from websites using Python, and it includes Docker support for easy setup and deployment.

## 📋 Requirements

- Docker installed on your system

## 🚀 Running a Single Container

To run the scraper in a single Docker container:

1. **Start the container**:
   ```bash
   docker-compose up -d
   ```

2. **Stop the container**:
   ```bash
   docker-compose down
   ```

## ⚙️ Running Multiple Containers

For scenarios where you need to run multiple containers with different configurations:

1. **Make the shell scripts executable**:
   ```bash
   chmod +x generate-compose-files.sh
   chmod +x run.sh
   ```

2. **Generate the necessary Docker Compose files**:
   ```bash
   ./generate-compose-files.sh
   ```

3. **Run the containers**:
   ```bash
   ./run.sh
   ```

> **Note**: You may need to modify the `generate-compose-files.sh` and `run.sh` files according to your requirements. This includes setting the number of containers to run and specifying paths for inputs and outputs.

## 🔧 Configuration

- **`generate-compose-files.sh`**: Customize this script to specify the number of containers and their configurations.
- **`run.sh`**: Adjust this script as needed to handle different container setups.

## 📂 Files and Directories

- **`Dockerfile`**: Defines the Docker image for the email scraper.
- **`docker-compose.yml`**: Configures the services, networks, and volumes.
- **`generate-compose-files.sh`**: Shell script to generate Docker Compose files.
- **`run.sh`**: Shell script to run multiple Docker containers.
- **`input/`**: Directory for input files.
- **`output/`**: Directory for output files.
- **`logs/`**: Directory where logs from all Docker containers will be stored.

## 📜 Logging

All logs from Docker containers will be stored in the `logs/` folder. Make sure to check these logs for detailed information on the scraping process.

## 🤝 Contributing

Feel free to submit issues or pull requests if you have suggestions for improvements or new features.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

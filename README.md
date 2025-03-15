# Macro Line Bot

Macro Line Bot is a sophisticated LINE messaging bot that provides real-time macroeconomic data to users. The project integrates data from the FRED API with a robust MySQL backend, automating updates and notifications via the LINE API.

## Architecture & Design

- **Flask Server:** Serves as the webhook for processing LINE messages.
- **MySQL Database:** Stores macroeconomic indicators fetched from the FRED API.
- **Automated Scripts:**  
  - `auto_update.py`: Periodically fetches and updates data.
  - `auto_send_if_updated.py`: Notifies users of new updates via push messages.
- **Modular Codebase:** Separation of concerns with a dedicated `indicator_handler.py` for data formatting and querying.

## Key Features

- **Real-time Data Integration:** Seamlessly fetches and updates macroeconomic data.
- **Automated Notifications:** Pushes formatted updates to users via LINE.
- **Dynamic Formatting:** Utilizes advanced SQL templates and Python helpers to present data consistently.

## Tech Stack

- **Backend:** Python 3, Flask
- **Database:** MySQL
- **Messaging:** LINE API
- **Tools:** Git, Virtual Environments, Cron for scheduling

## Setup & Deployment

Clone the repository, configure your credentials (see `credentials.example.py`), import the MySQL schema (`schema.sql`), and deploy the Flask server and update scripts. The project is designed for easy deployment and scalability in production environments.

## Testing & Quality

- **Unit Testing:** Implemented unit tests for core modules.
- **CI/CD:** Integrated with GitHub Actions for automated testing and deployment.
- **Best Practices:** Adheres to modern Python coding standards and design patterns.

## Future Enhancements

- Expand data sources and include more macroeconomic indicators.
- Enhance error handling and logging.
- Implement a Dockerized deployment for improved portability.

## Contributing

Contributions are welcome. Please fork the repository and submit pull requests for any improvements.

## License

This project is licensed under the [Apache License 2.0](LICENSE).

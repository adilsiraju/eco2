# The Ecovest: Sustainable Investing Platform
![image](https://github.com/user-attachments/assets/ffd7a980-ad4a-48a9-9d8a-f7af51c50dba)
![image](https://github.com/user-attachments/assets/3e2e57fc-e557-421b-86e1-e215ae5e595a)
![image](https://github.com/user-attachments/assets/bc506045-8141-4315-9494-34f037663047)

Ecovest is a sustainable investing platform designed to connect environmentally conscious investors with vetted sustainable projects and companies. Our mission is to make sustainable investing accessible, transparent, and impactful for everyone.

## Features

- **Sustainable Projects and Companies**: Browse and invest in a variety of sustainable initiatives and companies across renewable energy, conservation, clean water, green technology, and more.
- **Impact Tracking**: Monitor the environmental impact of your investments through detailed metrics such as carbon emissions reduced, energy saved, and water conserved.
- **User Dashboard**: Track your investment portfolio and see the real-world impact of your contributions.
- **Secure Investments**: Ensure your investments are secure and transparent, with detailed project and company profiles.

## Getting Started

### Prerequisites

- Python 3.11
- Django 5.1.7
- PostgreSQL (or SQLite for development)

### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/eco2.git
   cd eco2
   ```

2. **Set Up Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**:
   - Create a database and update the `DATABASES` setting in `ecovest/settings.py` with your database credentials.
   - Run the following commands to apply migrations:
     ```bash
     python manage.py makemigrations
     python manage.py migrate
     ```

5. **Create a Superuser**:
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the Development Server**:
   ```bash
   python manage.py runserver
   ```

7. **Access the Application**:
   Open your browser and go to `http://127.0.0.1:8000/` to see the application in action.

## Project Structure

- **core**: Contains the main views and templates for the landing page and error pages.
- **ecovest**: The main Django project directory containing settings and URL configurations.
- **initiatives**: Manages sustainable initiatives and companies, including models, views, and templates.
- **investments**: Handles investment logic, impact calculations, and related views and templates.
- **users**: Manages user authentication, profiles, and dashboard views.
- **media**: Stores uploaded images for initiatives, companies, and user profiles.
- **static**: Contains static files such as CSS and images.
- **templates**: HTML templates for rendering views.

## Contributing

We welcome contributions from the community! If you'd like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or support, please contact us at [support@eco2.com](mailto:support@eco2.com).

---

Join us in making a positive impact on the environment while generating returns on your investments. Together, we can create a sustainable future!

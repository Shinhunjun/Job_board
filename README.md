# Job Board Web Application

A full-stack job board platform built with Flask and MySQL, featuring job search, company profiles, and real-time job recommendations using scraped data.

## Features

- **Job Search & Filtering**: Search jobs by keywords, location, and category with advanced filters
- **Company Profiles**: Detailed company information including location, industry, and job listings
- **Database Integration**: MySQL database with SQLAlchemy ORM for efficient data management
- **Responsive Design**: User-friendly interface for both desktop and mobile devices

## Tech Stack

- **Backend**: Python, Flask, SQLAlchemy
- **Database**: MySQL
- **Frontend**: HTML, CSS, Jinja2 Templates
- **Data Processing**: Pandas, NumPy (for EDA and ML analysis)

## Project Structure

```
Job_board/
├── app.py                          # Main Flask application
├── CodeBase/
│   ├── Code_EDA_MachineLearning.ipynb  # Data analysis and ML notebook
│   ├── models.py                   # Database models
│   ├── utils.py                    # Utility functions
│   └── requirements.txt            # Dependencies
├── templates/
│   ├── base.html                   # Base template
│   ├── index2.html                 # Homepage
│   ├── jobsearch.html              # Job search page
│   ├── companies.html              # Companies list
│   └── company_detail.html         # Company detail page
├── static/                         # Static assets (CSS, JS)
├── data/                           # Data files
├── Dump20241207.sql               # Database dump
└── EER Disgram.png                # Entity-Relationship Diagram
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Shinhunjun/Job_board.git
   cd Job_board
   ```

2. Install dependencies:
   ```bash
   pip install -r CodeBase/requirements.txt
   ```

3. Set up MySQL database:
   ```bash
   mysql -u root -p < Dump20241207.sql
   ```

4. Configure database connection in `app.py`:
   ```python
   SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@localhost:{port}/{databasename}"
   ```

5. Run the application:
   ```bash
   python app.py
   ```

## Database Schema

The application uses a relational database with the following main tables:
- **Companies**: Company information and metadata
- **Jobs**: Job listings linked to companies
- **Locations**: Geographic information
- **Industries**: Industry categories

See `EER Disgram.png` for the complete Entity-Relationship Diagram.

## Usage

- **Homepage**: Browse featured jobs and companies
- **Job Search**: Filter jobs by keywords, title, and company
- **Company Profiles**: View detailed company information and all associated job listings

## Contributors

- Hunjun Shin
- Daniel Hasan

## License

This project is for educational purposes as part of Northeastern University coursework.

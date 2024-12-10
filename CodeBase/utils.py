import pandas as pd
from models import db, Company, Location, Industry, Job, JobSkill, Skill, JobType
from sqlalchemy.exc import IntegrityError
import logging
import re


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def load_company_data_to_db(excel_path):


    data = pd.read_excel(excel_path)

    # preprocess
    data.drop(columns=['pagination', 'web-scraper-order', 'web-scraper-start-url', 'links', 'links-href'], inplace=True)
    data['num_employee'] = data['num_employee'].apply(lambda x: re.sub(r'\s+', ' ', str(x).strip()))

    def categorize_num_employee(num_employee_text):
        
        match = re.search(r'(\d+)', num_employee_text)
        if match:
            num_employees = int(match.group(1).replace(",", "")) 
            if 1 <= num_employees <= 10:
                return "1-10 Employees"
            elif 11 <= num_employees <= 50:
                return "11-50 Employees"
            elif 51 <= num_employees <= 200:
                return "51-200 Employees"
            elif 201 <= num_employees <= 500:
                return "201-500 Employees"
            elif 501 <= num_employees <= 1000:
                return "501-1000 Employees"
            elif num_employees > 1000:
                return "1000+ Employees"
        return "Unknown"

    data['employee_count'] = data['num_employee'].apply(lambda x: categorize_num_employee(str(x)))
   
    def split_categories(categories_text):
        if pd.isna(categories_text):  
            return []
        return [category.strip() for category in re.split(r'[\n,]+', str(categories_text)) if category.strip()]

    data['company_category'] = data['company_category'].apply(split_categories)
    
    data['description'] = data['company_overview'].apply(lambda x: re.sub(r'\s+', ' ', str(x).strip()))
    
    data = data.rename(columns={
        'company_title': 'name',
        'company_logo-src': 'logo_url',
        'company_location': 'location',
        'company_website-href': 'website'
    })
    
    final_columns = ['name', 'logo_url', 'location', 'company_category', 'description', 'employee_count', 'website']
    clean_data = data[final_columns]


    def get_or_create_industry(industry_name):

        industry_info = Industry.query.filter_by(industry_name=industry_name).first()
        if industry_info:
            return industry_info
        else:
            new_industry = Industry(industry_name=industry_name)
            db.session.add(new_industry)
            try:
                db.session.commit()
                return new_industry
            except IntegrityError: 
                db.session.rollback()
                return Industry.query.filter_by(industry_name=industry_name).first()

    def clean_category(category_input):

        if not category_input:
            return []
        if isinstance(category_input, list):
            return [cat.strip() for cat in category_input if cat.strip()]
        elif isinstance(category_input, str):
            category_input = category_input.strip("[]").replace("'", "").replace('"', "").strip()
            return [cat.strip() for cat in category_input.split(",") if cat.strip()]
        else:
            return []
    try:
        df = clean_data
        df = df.where(pd.notnull(df), None)
        logging.info("Preprocessed Excel file successfully read.")
    except Exception as e:
        logging.error(f"Error reading Excel file: {e}")
        raise

    for _, row in df.iterrows():
        try:
            company = Company.query.filter_by(name=row['name']).first()
            
            if not company:                

                company = Company(
                    name=row['name'],
                    description=row['description'] if pd.notna(row['description']) else None,
                    website= row['website'] if pd.notna(row['website']) else None,
                    logo_url=row['logo_url'] if pd.notna(row['logo_url']) else None,
                )
                db.session.add(company)
                db.session.flush()  

            if pd.notna(row['location']):
                location_parts = row['location'].split(',')
                city = location_parts[0].strip() if len(location_parts) > 0 else None
                state = location_parts[1].strip() if len(location_parts) > 1 else None
                country = location_parts[2].strip() if len(location_parts) > 2 else None

                location_val = Location.query.filter_by(city=city, state=state, country=country).first()
                if not location_val:
                    location_val= Location(city="Unknown", state="Unknown", country="Unknown")
                    db.session.add(location_val)
                    db.session.flush()

                if location_val not in company.locations:
                    company.locations.append(location_val)

            if row['company_category']:
                categories = clean_category(row['company_category'])
                for category_item in categories:
                    industry = get_or_create_industry(category_item)

                    if industry not in company.industries:
                        company.industries.append(industry)

        except Exception as e:
            logging.error(f"Error processing row {row.to_dict()}: {e}")
            continue  

    try:
        db.session.commit()
        logging.info("All changes successfully committed to the database.")
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error committing changes: {e}")
        raise

def load_job_data_to_db(file_path):
    
    data = pd.read_excel(file_path)    
    
    #preprocess
    
    data['combined_info'] = data[['info1', 'info2', 'info3', 'info4']].fillna('').agg(' '.join, axis=1)

    def parse_info(info):
        parsed = {
            'work_type': None,
            'minimum_salary': 'unknown',
            'max_salary': 'unknown',
            'avg_salary': 'unknown',
            'employee_level': 'unknown'
        }

        if 'Remote' in info:
            parsed['work_type'] = 'Remote'
        elif 'Hybrid' in info:
            parsed['work_type'] = 'Hybrid'
        else:
            parsed['work_type'] = 'Onsite'

        salary_match = re.search(r'(\d+K)-(\d+K)', info)
        if salary_match:
            min_salary = int(salary_match.group(1).replace('K', '')) * 1000
            max_salary = int(salary_match.group(2).replace('K', '')) * 1000
            avg_salary = (min_salary + max_salary) // 2
            parsed['minimum_salary'] = min_salary
            parsed['max_salary'] = max_salary
            parsed['avg_salary'] = avg_salary

        levels = ['Internship','Entry level', 'Junior', 'Mid level', 'Senior level', 'Expert/Leader']
        for level in levels:
            if level in info:
                parsed['employee_level'] = level
                break

        return parsed

    parsed_info = data['combined_info'].apply(parse_info)
    data['work_type'] = parsed_info.apply(lambda x: x['work_type'])
    data['minimum_salary'] = parsed_info.apply(lambda x: x['minimum_salary'])
    data['max_salary'] = parsed_info.apply(lambda x: x['max_salary'])
    data['avg_salary'] = parsed_info.apply(lambda x: x['avg_salary'])
    data['employee_level'] = parsed_info.apply(lambda x: x['employee_level'])

    def clean_skills(skills):
        if isinstance(skills, str):
            valid_skills = re.findall(
                r'<div class="py-xs px-sm d-inline-block rounded-3 fs-sm text-nowrap border">(.*?)</div>',
                skills
            )
            return valid_skills if valid_skills else None
        return None

    data['skills'] = data['skills'].apply(clean_skills)
    data = data[data['skills'].notnull()]

    columns_to_keep = [
        'job_summary', 'company_url-href', 'job_title',
        'company_title', 'skills', 'work_type',
        'minimum_salary', 'max_salary', 'avg_salary', 'employee_level'
    ]
    data = data[columns_to_keep]

    data.rename(columns={'company_url-href': 'company_url'}, inplace=True)

    def clean_company_url(url):
        if isinstance(url, str) and url.startswith('http'):
            return url
        return 'unknown'

    data['company_url'] = data['company_url'].apply(clean_company_url)
    clean_data = data.drop_duplicates(subset=['job_title', 'company_title', 'company_url'])
    clean_data.reset_index(drop=True, inplace=True)

    def get_or_create_job_type(job_type_name):
        job_type_info = JobType.query.filter_by(type_name=job_type_name).first()
        if job_type_info:
            return job_type_info
        else:
            new_job_type = JobType(type_name=job_type_name)
            db.session.add(new_job_type)
            try:
                db.session.commit()
                return new_job_type
            except IntegrityError:
                db.session.rollback()
                return JobType.query.filter_by(type_name=job_type_name)

    def get_location_id_for_company(company_title, company_url):
        company = Company.query.filter_by(name=company_title, website=company_url).first()
        if company and company.locations:
            return company.locations[0].location_id
        return None

    def get_company_id(company_title, company_url):
        company = Company.query.filter_by(name=company_title, website=company_url).first()
        return company.company_id if company else None

    def clean_salary(value):
        try:
            return float(value)  
        except (ValueError, TypeError):
            return None   
    
    #load in to the database
    try:

        job_df = clean_data

        for _, row in job_df.iterrows():
            try:
                job_title_value = row.get('job_title', None)
                job_description_value = row.get('job_summary', None)
                company_title_value = row.get('company_title', None)
                company_url_value = row.get('company_url', None)
                work_type_value = row.get('work_type', None)
                minimum_salary_value = clean_salary(row.get('minimum_salary'))
                max_salary_value = clean_salary(row.get('max_salary'))

                if not job_title_value or not job_description_value:
                    continue

                company_id = get_company_id(company_title_value, company_url_value)
                print (company_id)
                if not company_id:
                    continue 

                location_id = get_location_id_for_company(company_title_value, company_url_value)
                if not location_id:
                    continue
  
                duplicate_job = (
                    Job.query.join(Company, Job.company_id == Company.company_id)
                    .filter(
                        Job.title == job_title_value,
                        Company.website == company_url_value
                    )
                    .first()
                )
                if duplicate_job:
                    continue  

                job_type = None
                if work_type_value:
                    job_type = get_or_create_job_type(work_type_value)

                job = Job(
                    title=job_title_value,
                    description=job_description_value,
                    company_id=company_id,
                    job_type_id=job_type.job_type_id if job_type else None,  
                    salary_min=minimum_salary_value,
                    salary_max=max_salary_value,
                    location_id=location_id
                )
                db.session.add(job)
                db.session.flush()  

                if row['skills']:
                    skills_list = eval(row['skills']) if isinstance(row['skills'], str) else row['skills']
                    for skill_item in skills_list:
                        skill = Skill.query.filter_by(skill_name=skill_item).first()
                        if not skill:
                            skill = Skill(skill_name=skill_item)
                            db.session.add(skill)
                            db.session.flush()

                        existing_job_skill = JobSkill.query.filter_by(job_id=job.job_id, skill_id=skill.skill_id).first() 
                        if not existing_job_skill:
                            job_skill = JobSkill(job_id=job.job_id, skill_id=skill.skill_id)
                            db.session.add(job_skill)

                logging.info(f"Job added: {job_title_value}")

            except Exception as inner_e:
                logging.error(f"Error processing row {row.to_dict()}: {inner_e}")
                continue 

        db.session.commit()
        logging.info("Job data successfully loaded into the database.")

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error loading job data: {e}")

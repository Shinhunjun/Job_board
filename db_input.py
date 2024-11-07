
LOAD DATA INFILE '/path/to/companies.csv'
INTO TABLE companies
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(company_id, name, size, industry);

-- jobs 테이블로 데이터 가져오기
LOAD DATA INFILE '/path/to/jobs.csv'
INTO TABLE jobs
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(job_id, title, description, company_id, location, job_type, experience_level, salary_min, salary_max, posted_date, education_level, remote);
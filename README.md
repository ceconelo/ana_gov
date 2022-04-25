
# Data scraping in the reservoir monitoring system of National Water and Sanitation Agency.

The National Water Agency (ANA) is legally liable for implementing the National Water Resources Management System (SINGREH), created to ensure the sustainable use of our rivers and lakes for the current and future generations.




## About project

This project downloads the monitoring history of the national reservoirs.

For each reservoir a .csv file is created.

The project was built with the Scrapy framework and contains two spiders that perform the tasks.

(new_files.py) -> This spider is responsible for downloading new files from the website.

(update_records) -> This spider is responsible for updating the downloaded files.



## Roadmap

- Put the project into your virtual environment

- In the settings.py file define the ABSOLUTE_PATH variable with the absolute 
  address for the datasets folder (e.g. c:\user\jose\project\ana\ana\datasets)

- Install the necessary libraries (requirements.txt)
  


## How to Use
In your virtual environment and inside the project folder (../ana).

- If you want to use a custom list define it in main.py module
```bash
  python3 .\main.py 
```

- to download the history of the reservoirs
```bash
  scrapy crawl new_files -L WARN  
```

- to update the files
```bash
  scrapy crawl update_records -L WARN
```


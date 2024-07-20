Step 1: 
  Install Python
Step 2:
  Install Below Commands
  pip install Flask
  pip install Flask-MySQLdb
  pip install pandas
  pip install requests
  pip install Pillow

Add Config Details in config.py
  class Config:
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'user'
    MYSQL_PASSWORD = 'passowrd'
    MYSQL_DB = 'sde_test'
    MYSQL_PORT = 3306

Step3:
  Create Below tables in MySQL WorkBench
  
  use sde_test;
  
  CREATE TABLE requestfilemapping (
      request_id INT PRIMARY KEY AUTO_INCREMENT,
      filename VARCHAR(255),
      current_date_time DATETIME DEFAULT CURRENT_TIMESTAMP,
      newfilename VARCHAR(255)
  );
  
  ALTER TABLE requestfilemapping AUTO_INCREMENT = 5000;
  
  use sde_test;
  
  CREATE TABLE RequestProductImages (
      RequestProductImageID INT AUTO_INCREMENT PRIMARY KEY,
      RequestID INT,
      ProductName VARCHAR(255),
      SerialNumber VARCHAR(255),
      ImageURL VARCHAR(255),
      LocalOriginalImagePath VARCHAR(255),
      LocalProcessedImagePath VARCHAR(255),
      IsProcessed BOOLEAN DEFAULT 0
  );

Step 4 (Run the Application and followed the step mentioned in the report)
  Python app.pu
  

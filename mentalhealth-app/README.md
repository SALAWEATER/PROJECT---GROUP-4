# Initial README

 To run the file, assuming you have downloaded, pulled or cloned the repository or related files, I would suggest creating a virtual environment by navigating to your desired file location through the terminal then typing:
 python -m venv <environment-name>
 after which, activate the virtual environment through 
 <environment-name>/Scripts/activate
 you should see the the name of the environment on the left-most side of your terminal.
 once done navigate to the location of the source codes then run the following in a specific order
 run the requirements.txt using the following syntax:
 pip install -r requirements.txt
 then run the source codes using:
 python <filename>.py
 in one terminal window:
 1. init_db.py
 2. app.py
 then in another terminal window:
 3. frontend.py
 should be the same in linux/macos and windows just replace the "/" in the file paths to "\" when running on a windows machine.
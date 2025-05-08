# How to use

Make sure you have [Python](https://www.python.org/) installed on your machine.

Install the required `requests` library.
```
pip install requests
```
Edit the `import.py` script and insert your access token.

Make sure you have a file with the users to import in a file called `users.csv` in the same directory as the import script and run it from the command line like this:

```
python import.py
```

### Example import file
```
UserName;FirstName;LastName;External department id;Role id 
john.doe@example.com;John;Doe;10001;900 
jane.smith@example.com;Jane;Smith;10002;901 
michael.johnson@example.com;Michael;Johnson;10003;902 
emily.white@example.com;Emily;White;10004;903 
```

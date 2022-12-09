# Social Distribution
CMPUT 404 group project https://cmput404f22t17.herokuapp.com/ 

## Demo Video
[Project Demo](https://drive.google.com/file/d/1zAntWc_vFLiCRiO99ReN3btMU7795ATg/view?usp=sharing)

## API Endpoints Documentation
[https://cmput404f22t17.herokuapp.com/docs/](https://cmput404f22t17.herokuapp.com/docs/)

## Local Deployment
### Instructions
1. `git clone` this repo
2. `cd mysite` to navigate to the project folder
3. Create a python virtual environment in the project folder and activate the environment
4. Run `pip install -r requirements.txt` to install the project dependencies
5. Run `python manage.py migrate` to apply database migration to the sql database server
6. Create superuser: Run `python manage.py createsuperuser`
7. Run `python manage.py runserver`

### Testing Instructions
1. `cd mysite` to navigate to the project folder
1. Run `python manage.py test`

## Connected Teams
- Team 6 https://socialdistribution-cmput404.herokuapp.com/
- Team 9 https://team9-socialdistribution.herokuapp.com/ 
- Team 18 https://cmput404team18-backend.herokuapp.com/


## Contributors
| Name                  | GitHub                                                  |
| --------------------- | ------------------------------------------------------- |
| Eric Weber            | [Eric Weber](https://github.com/EricWeber33)      |
| Christopher Orlick    | [Christopher Orlick ](https://github.com/corlick98)      |
| Alisha Crasta         | [Alisha Crasta](https://github.com/alisha03)    |
| Houston Le            | [Houston Le](https://github.com/houstonle)           |
| Kevin Zhu             | [Kevin Zhu ](https://github.com/OmgPockii) |

## General Usage notes
- If the app appears to not log-in just try again
- The remote registration feature was added because of misunderstanding the project requirements, using it is not recommended
## New features since presentation
- Now can edit, repost, and delete posts.
- Can now send and recieve remote likes
- Some parts of django view based frontend are now asynchronous, making the explore posts page much faster
- Link added to go view your own followers on the homepage
## License
[License Details](/LICENSE)

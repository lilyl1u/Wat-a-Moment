const express = require('express');
const mysql = require('mysql2');
const port = '3000';
const app = express();

const bodyParser = require('body-parser');
const cors = require('cors');
app.use(bodyParser.json());// to support JSON-encoded bodies
app.use(bodyParser.urlencoded({ // to support URL-encoded bodies
  extended: true
}));
app.use(express.json());// to support JSON-encoded bodies
app.use(express.urlencoded({ // to support URL-encoded bodies
  extended: true
}));
app.use(cors()); //incoming api call blocked to send data to backend

//login sessions for multiple users
const session = require('express-session');

const dotenv = require('dotenv'); //for secure sessions
dotenv.config(); //access when needed


app.use(session({
  secret: 'watamoment123',
  resave: true,
  saveUninitialized: false,
  cookie: {
    expires: 600000 //expires after 10 min of inactivity
  }
}));

//===SQL DB===
let instance = null;
const db = mysql.createPool({ //connect sql database
  host: 'riku.shoshin.uwaterloo.ca',
  user: 'a498wang',
  password: 'dbz4SLMtIM0bdgn8Q0%0',
  database: 'db101_a498wang'
  //todo: this can also be encoded using dotenv?
});
db.getConnection((err) => {
  if (err) {
    console.error("[DB] Connection error:", err.message);
  }
  console.log("[DB] mysql pool connected");
});

/*
app.use((req, _, next) => {
  console.log(`[${req.method}] ${req.url} - Body: ${JSON.stringify(req.body)}`);
  next();
});

const MySQLStore = require('express-mysql-session')(session);
const sessionStore = new MySQLStore({
  host: 'riku.shoshin.uwaterloo.ca',
  user: 'a498wang',
  password: 'dbz4SLMtIM0bdgn8Q0%0',
  database: 'db101_a498wang',
  clearExpired: true,
  checkExpirationInterval: 900000,
});

app.use(session({
  secret: process.env.SESSION_SECRET || 'default_secret',
  resave: false,
  saveUninitialized: false,
  store: sessionStore,
  cookie: {
    secure: false,
    httpOnly: true,
    maxAge: 600000,
  },
}));

console.log(`[POST] /wamUserLogin - Attempting login for user: ${username}`);
console.log(`[POST] /sync-session - Body: ${JSON.stringify(req.body)}`);
console.log(`[POST] Logout endpoint hit`);
*/



//===SQL FUNCTIONS===
//the functions below are called by routers to access the data
class DBService {
  static getDBServiceInstance() {
    return instance ? instance : new DBService(); //create new DBService if instance does not exist
  }

  //get user by username
  async getWamUser(username) { /*async means that the function is asynchronous - the following async functions will return a Promise. The await keyword is used so the asynchronous queries complete (Promise resolves or rejects) before moving on to the next step*/
    console.log(`[DBService] Fetching user: ${username}`); //new code from chat
    try {
      /*a Promise is an operation that has yet to be executed. Takes 2 arguments which are the resolve and reject functions - these functions resolve the promise with a value if fulfilled, or returns an error if rejected */
      const response = await new Promise((resolve, reject) => {
        const sql = "SELECT * FROM wamUsers WHERE username = ?;";
        db.query(sql, [username], (err, result) => { //callback function to handle resolving or rejecting the Promise
          if (err) {
            console.error(`[DBService] Error fetching user: ${err.message}`);
            reject(err);
          } else {
            console.log(`[DBService] User data retrieved: ${JSON.stringify(result)}`);
            resolve(result);
          }
        });
      });
      console.log(response);
      return response; //this returns an array of objects representing the rows in the SQL table
    }
    catch (error) { console.log(error); }
  }

    //get all users under one class code
    async getAllUsers(classCode) { /*async means that the function is asynchronous - the following async functions will return a Promise. The await keyword is used so the asynchronous queries complete (Promise resolves or rejects) before moving on to the next step*/
      console.log(`[DBService] Fetching users in: ${classCode}`); //new code from chat
      try {
        /*a Promise is an operation that has yet to be executed. Takes 2 arguments which are the resolve and reject functions - these functions resolve the promise with a value if fulfilled, or returns an error if rejected */
        const response = await new Promise((resolve, reject) => {
          const sql = "SELECT * FROM wamUsers WHERE classCode = ?;";
          db.query(sql, [classCode], (err, result) => { //callback function to handle resolving or rejecting the Promise
            if (err) {
              console.error(`[DBService] Error fetching users: ${err.message}`);
              reject(err);
            } else {
              console.log(`[DBService] User data retrieved: ${JSON.stringify(result)}`);
              resolve(result);
            }
          });
        });
        console.log(response);
        return response; //this returns an array of objects representing the rows in the SQL table
      }
      catch (error) { console.log(error); }
    }

  //create new user
  async createWamUser(username, password, classCode, firstName, lastName) { //the private photos aren't implemented here directly - instead, in the folder of all photos, each photo will be attributed to a specific user. When the same photo is shared to multiple accounts, those photos will be copies of each other that can be modified and accessed sepearately
    console.log(`[DBService] Creating user: ${username}`);
    try {
      await new Promise((resolve, reject) => {
        const sql = "INSERT INTO wamUsers (username, password, classCode, firstName, lastName) VALUES (?,?,?,?,?);";
        db.query(sql, [username, password, classCode, firstName, lastName], (err, result) => {
          if (err) reject(new Error(err.message));
          resolve(result);
        });
      });
      return {
        username: username,
        password: password,
        classCode: classCode,
        firstName: firstName,
        lastName: lastName,
      };
    }
    catch (error) { console.log(error); }
  }

  //add or update class code for a user
  async updateClassCode(username, classCode) {
    try {
      const reponse = await new Promise((resolve, reject) => {
        const sql = "UPDATE wamUsers SET classCode = ? WHERE username = ?;";
        db.query(sql, [classCode, username], (err, result) => {
          if (err) reject(new Error(err.message));
          resolve(result);
        });
      });
      return reponse;
    } catch (error) { console.log(error); }
  }

  //create/insert new photo, user can be a wamUser username or a classCode
  async insertPhoto(photoFile, photoDate, user) { //photoID field is auto-incremented (generated)
    try {
      const response = await new Promise((resolve, reject) => {
        const sql = "INSERT INTO allPhotos (photoFile, photoDate, user) VALUES (?, ?, ?);";
        db.query(sql, [photoFile, curDate(), user], (err, result) => { //todo: change curDate() to actual datetime of photo taken - passed through params
          if (err) reject(new Error(err.message));
          resolve(result);
        });
      });
      return {
        photoFile: photoFile,
        photoDate: photoDate,
        user: user,
        photoID: response.insertId //the auto-incremented generated id from the sql insert function
      };
    }
    catch (error) { console.log(error); }
  }

  //during the session, all photos taken will be saved to the session under the reserved username "CURRENT-SESSION"
  async assignPhotoToUser(photoID, user){
    try {
      const response = await new Promise((resolve, reject) => {
        const sql = "UPDATE allPhotos SET user = ? WHERE photoID = ?;";
        db.query(sql, [user, photoID], (err, result) => { 
          resolve(result);
        });
      });
      return response;
    }
    catch (error) { console.log(error); }
  }

  //check which user the photo belongs to (for verifying that it is CURRENT)
  //changed angie's code:
  async getPhoto(identifier, type = 'user') {
    try {
        const response = await new Promise((resolve, reject) => {
            const sql = type === 'user'
                ? "SELECT photoID FROM allPhotos WHERE user = ?;"
                : "SELECT photoID FROM allPhotos WHERE classCode = ?;";
            db.query(sql, [identifier], (err, result) => {
                if (err) reject(new Error(err.message));
                resolve(result);
            });
        });
        console.log(response);
        return response;
    } catch (error) {
        console.log(error);
    }
}

  /*
  async getPhotoUser(photoID) {
    try {
      const user = await new Promise((resolve, reject) => {
        const sql = "SELECT user FROM allPhotos WHERE photoID = ?;";
        db.query(sql, [photoID], (err, result) => {
          if (err) reject(new Error(err.message));
          // Assuming the result is an array and we need the `user` field from the first entry
          if (result && result.length >0) {
            resolve(result[0].user);
          } else {reject(new Error("No user found for the given photoID"));}
        });
      });
      console.log(user);
      return user;
    } catch (error) {console.log(error);}
  }
    */

  //get all private photos under one username OR get all public photos under one classCode passed through 'user'
  async getPhoto(user) {
    try {
      const response = await new Promise((resolve, reject) => {
        const sql = "SELECT * FROM allPhotos WHERE user = ?;";
        db.query(sql, [user], (err, result) => {
          if (err) reject(new Error(err.message));
          resolve(result);
        });
      });
      console.log(response);
      return (response);
    }
    catch (error) {console.log(error);}
  }

  //delete a single photo
  async deletePhoto(photoID) {
    try {
      const response = await new Promise((resolve, reject) => {
        const sql = "DELETE FROM allPhotos WHERE photoID = ?;";
        db.query(sql, [photoID], (err, result) => {
          if (err) reject(new Error(err.message));
          resolve(result);
        });
      });
      console.log(response);
      return response;
    } catch (error) {console.log(error);}
  }

  //delete a user
  async deleteUser(username) {
    try {
      const response = await new Promise((resolve, reject) => {
        const sql = "DELETE FROM wamUsers WHERE username = ?;";
        db.query(sql, [username], (err, result) => {
          if (error) reject(new Error(err.message));
          resolve(result);
        });
      });
      return response;
    } catch (error) { console.log(error); }
  }
}





//===GET ROUTERS===
//FOR RASP PI
app.get('/api/logged-in-user', (req, res) => {
  if (req.session.userID) {
      res.json({ success: true, message: 'User retrieved', userID: req.session.userID });
  } else {
      res.status(401).send('No user logged in');
  }
});


//get a single wamuser by username
app.get('/getWamUser/:username', (req, res) => {
  const { username } = req.params;
  console.log(`[GET] /getWamUser/${username}`);
  const instanceDB = DBService.getDBServiceInstance();
  const result = instanceDB.getWamUser(username); //calls function from DBService class
  result
  .then(data => {
    if (data.length > 0) {
      console.log(`[GET] User found: ${username}`);
      res.json({
        success: true,
        message: 'User data retrieved',
        data: data[0] // Access the first user object from the array (since expectng only 1)
      });
      console.log(message);
    } else {
      console.log(`[GET] User not found: ${username}`);
      res.status(404).json({
        success: false,
        message: 'User not found',
        data: null
      });
      console.log(message);
    }
  })
  .catch(err => {
    console.error(`[GET] Error retrieving user: ${err.message}`);
    res.status(500).json({
    success: false,
    message: 'Failed to retrieve user',
    data: null,
    error: err.message
  });
});
});

//changed angie's code
app.get('/getPrivatePhotos/:username', (req, res) => {
  const { username } = req.params;
  const instanceDB = DBService.getDBServiceInstance();
  const result = instanceDB.getPhoto(username, 'user');
  result
    .then(photos => {
      const updatedPhotos = photos.map(photo => {
        const photoURL = `https://drive.google.com/uc?id=${photo.photoID}`; // Construct the URL
        console.log(`Constructed URL for photoID ${photo.photoID}: ${photoURL}`); // Debug
        return {
          photoID: photo.photoID,
          photoURL: photoURL
        };
      });
      console.log('Updated Photos:', updatedPhotos); // Debug
      res.json(updatedPhotos); // Send back with URLs
    })
    console.error('Error fetching private photos:', err);
    res.status(500).json({ error: 'Failed to fetch photos' });
});


/* 
app.get('/getPrivatePhotos/:username', (req, res) => {
  const { username } = req.params;
  const instanceDB = DBService.getDBServiceInstance();
  const result = instanceDB.getPhoto(username, 'user'); //changed angie's code //calls function from DBService class
  result
    .then(photos => res.json(photos)) //directly sends array of photos
    .catch(err => console.log(err));
});
*/
app.get('/getPublicPhotos/:classCode', (req, res) => {
  const { classCode } = req.params;
  const instanceDB = DBService.getDBServiceInstance();
  const result = instanceDB.getPhoto(classCode, 'classCode'); //changed angie's code//calls function from DBService class
  result
    .then(photos => res.json(photos)) //directly sends array of photos
    .catch(err => console.log(err));
});

//TODO
//app.get for checking if a user already exists, returning true/false

//===POST ROUTER===
// Fetch all users under a class code
app.get('/getAllUsers/:classCode', (req, res) => {
  const instanceDB = DBService.getDBServiceInstance();
  const { classCode } = req.params; //changed this from angie's
  const result = instanceDB.getAllUsers(classCode); // Calls function from DBService class
  result
    .then(users => res.json(users)) // Sends the array of usernames directly
    .catch(err => {
      console.error("[Error] Fetching usernames:", err);
      res.status(500).json({ success: false, message: "Failed to fetch usernames", error: err.message });
    });
});



//===POST ROUTERS===
//LOGIN
app.post('/wamUserLogin', function (req, res) {
  //retrieve username and password from user input
  const username = req.body.username;
  const password = req.body.password;
  if (username && password) {
    db.query(`SELECT password FROM wamUsers WHERE username = ? AND password = ?`, [username, password], function (error, results) {
      if (error){
        console.error(error);
        return res.status(500).json({ error: 'Internal server error' });
        
      }
      //if account exists:
      if (results.length > 0) {
        req.session.loggedin = true;
        req.session.username = username;
        return res.json({ message: 'Login successful', redirect: '/dashboard' });
        } else {
            return res.status(401).json({ error: 'Incorrect username or password' });
      }
    })
  }
})
//LOGOUT
app.post('/logout', (req, res) => {
  if (req.session) {
    req.session.destroy((err) => {
      if (err) {
        return res.status(500).send('Logout failed.');
      }
      res.status(200).send('Logged out successfully.');
    });
  } else {
    res.status(400).send('No active session.');
  }
});
/*
app.post('/logout', (req, res) => {
  console.log("[POST] Logout endpoint hit");
  if (req.session.loggedin) {
    req.session.destroy((err) => {
      if (err) {
        console.error("[POST] Logout error:", err.message);
        res.status(500).send('An error occurred while logging out.');
      } else {
        console.log("[POST] Logout successful");
        res.status(200).send('Logged out successfully.');
      }
    });
  } else {
    console.log("[POST] Logout attempt without session");
    res.status(400).send('You are not logged in.');
  }
});
*/

app.post('/sync-session', (req, res) => {
  const { username } = req.body;
  if (!username) {
      console.log("[POST] Sync session: Missing username in request.");
      return res.status(400).send("Missing username.");
  }

  req.session.loggedin = true;
  req.session.username = username;
  console.log(`[POST] Sync session: User logged in as ${username}`);
  res.status(200).send("Session synchronized successfully.");
});
/*
app.post('/logout', (req, res) => {
  if (req.session.loggedin) {
    req.session.destroy((err) => {
      if (err) {
        console.error("[POST] Logout error:", err.message);
        res.status(500).send('An error occurred while logging out.');
      } else {
        res.status(200).send('Logged out successfully.');
      }
    });
  } else {
    console.log("[POST] Logout attempt without session");
    res.status(400).send('You are not logged in.');
    //redirect 
  }
});
*/



//create Wam User
app.post('/createWamUser', (req, res) =>{
  
  const { username, password, classCode, firstName, lastName } = req.body;
  console.log(`[POST] /createWamUser - Payload: ${JSON.stringify(req.body)}`);
  const instanceDB = DBService.getDBServiceInstance();
  const result = instanceDB.createWamUser(username, password, classCode, firstName, lastName); //front end checked if password length is >1 and if classCode = SE101
  result
    .then(data => {
      console.log(`[POST] User created successfully: ${username}`);
      res.json({success: true, message: 'Account created', data: data}) 
    })
    .catch(err => {
      console.error(`[POST] Error creating user: ${err.message}`);
      res.status(500).json({ success: false, message: 'Failed to create user', error: err.message });
    });
});

//update class code
app.post('/updateClassCode', (req, res) =>{
  const { username, classCode} = req.body;
  const instanceDB = DBService.getDBServiceInstance();
  const result = instanceDB.updateClassCode(username, classCode);
  result
    .then(data => res.json({data: data}))
    .catch(err => console.log(err));

})


/*SEE UPLOAD-PHOTO.PY
//insert photo
app.post('/insertPhoto', (req, res) =>{
  const { photoFile, photoDate, user } = req.body;
  const instanceDB = DBService.getDBServiceInstance();
  const result = instanceDB.insertPhoto(photoFile, photoDate, user);
  result
    .then(data => res.json({data: data}))
    .catch(err => console.log(err));
})*/ 


//Assign photo to user, checking that the photo is in the current session
app.post('/assignPhotoToUser/:photoID/:user', (req, res) =>{
  const { photoID, user } = req.params;
  const instanceDB = DBService.getDBServiceInstance();
  const result = instanceDB.assignPhotoToUser(photoID, user) // Call your DBService function
  result
    .then(data => res.json({success: true, data: data}))
    .catch(err => console.log(err));
})




//===DELETE ROUTERS===
//delete photos
app.delete('/deletePhoto/:photoID', (request, response) => {
  const {photoID} = request.params;
  const instanceDB = DBService.getDbServiceInstance();
  const result = instanceDB.deletePhoto(photoID);
  result
    .then(data => response.json({success: true, message: "Deleted photo", data: data}))
    .catch(err => console.log(err));
});
//delete wamUser
app.delete('/deleteUser/:username', (request, response) => {
  const {photoID} = request.params;
  const instanceDB = DBService.getDbServiceInstance();
  const result = instanceDB.deleteUser(username);
  result
    .then(data => response.json({success: true, message: "Deleted user", data: data}))
    .catch(err => console.log(err));
});


//listen on port 3000
app.listen(port, () => console.info('Listening on port ' + port));





/*
//===PAGES===
//root - this is the homepage where all users can select between 'login' and 'create account'
app.get('/', (req, res) => {
  res.sendFile(__dirname + '/public/frontend/index.html');
});
//login
app.get('/login', (req, res) => {
  res.sendFile(__dirname + '/public/frontend/login.html')
});
//create account
app.get('/create-account', (req, res) => {
  res.sendFile(__dirname + '/public/frontend/create-account.html')
});
//users pages once they've logged in
app.get('/dashboard', (req, res) => {
  if (req.session.loggedin) {res.sendFile(__dirname + '/public/frontend/dashboard.html')}
  else {res.redirect('/login'); // redirect to login if not logged in
  }
});
app.get('/view-your-photos', (req, res) => {
  if (req.session.loggedin) {res.sendFile(__dirname + '/public/frontend/viewyourphotos.html')}
  else {res.redirect('/login'); // redirect to login if not logged in
  }
});
app.get('/view-class-photos', (req, res) => {
  if (req.session.loggedin) {res.sendFile(__dirname + '/public/frontend/viewclassphotos.html')}
  else {res.redirect('/login'); // redirect to login if not logged in
  }
});
app.get('/post-photo', (req, res) => {
  if (req.session.loggedin) {res.sendFile(__dirname + '/public/frontend/post-photo.html')}
  else {res.redirect('/login'); // redirect to login if not logged in
  }
}); */

const Sequelize = require('sequelize');
const AWS = require('aws-sdk');
/*
const sequelize = new Sequelize('database', 'username', 'password');

const User = sequelize.define('user', {
  username: Sequelize.STRING,
  birthday: Sequelize.DATE
});

sequelize.sync()
  .then(() => User.create({
    username: 'janedoe',
    birthday: new Date(1980, 6, 20)
  }))
  .then(jane => {
    console.log(jane.get({
      plain: true
    }));
  });
*/

exports.lambda_handler = function(event, context) {
    console.log('Received event: ', JSON.stringify(event, null, 2));

}
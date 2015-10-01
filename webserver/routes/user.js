var request = require('request');
var host = "localhost:5000";
/*
 * POST users listing.
 */

exports.getSentence = function(req, res) {
    request.get('http://' + host + '/', function(error, response, body) {
        if (!error && response.statusCode === 200) {
           res.json(body);
        } else {
           res.json({error : "Error connecting to the server"});
    });
    res.json({error : "Error connecting to the server"});
};

// exports.postSentence = function(req, res) {
//     var data = {
//         sentence : req.sentence,
//         wasFunny : req.wasFunny
//     };
//     request.post({url: 'http://'
// };

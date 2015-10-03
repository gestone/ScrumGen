/**
 * Handles GET and POST requests for sentence generation.
 */

var request = require('request');
var host = process.env['API_HOST'];

exports.getSentence = function(req, res) {
    request
        .get('http://' + host + '/sentence', function(error, response, body) {
            if (!error && response.statusCode === 200) {
               res.json(body);
            } else {
               console.log(error);
               res.json({error : "There was an issue connecting to the server."});
            }
        })
        .on('error', function(err) {
            res.json({error : "There was an issue connecting to the server."});
        });
};

exports.postSentence = function(req, res) {
    var formData = {
        sentence : req.body.sentence,
        wasFunny : req.body.wasFunny
    };
    url = 'http://' + host + '/sentence';
    request
        .post({url: url, formData : formData}, function(error, response, body) {
            if (error) {
                res.json({error : "There was an issue posting a new sentence"});
            } else {
                res.json(body);
            }
        })
        .on('error', function(err) {
            res.json({error : "There was an issue posting a new sentence"});
        });
};

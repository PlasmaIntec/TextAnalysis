const https = require('https');
const request = require('request');
const axios = require('axios');
const util = require('util');
const config = require("./config.js");

var Twit = require('twit');
var T = new Twit(config);
var TWEET_LENGTH_LIMIT = 280;

const get = util.promisify(request.get);
const post = util.promisify(request.post);

const consumer_key = config.consumer_key; // Add your API key here
const consumer_secret = config.consumer_secret; // Add your API secret key here

const bearerTokenURL = new URL('https://api.twitter.com/oauth2/token');
const streamURL = new URL('https://api.twitter.com/labs/1/tweets/stream/sample');

var serverAvailable = true;

async function bearerToken (auth) {
  const requestConfig = {
    url: bearerTokenURL,
    auth: {
      user: consumer_key,
      pass: consumer_secret,
    },
    form: {
      grant_type: 'client_credentials',
    },
    headers: {
      'User-Agent': 'TwitterDevSampledStreamQuickStartJS',
    },
  };

  const response = await post(requestConfig);
  return JSON.parse(response.body).access_token;
}

var getFirstWord = text => {
	console.log(text)
	var words = text.replace(/[^a-zA-Z ]/g, "").split(" ");
	console.log(words)
	for (word of words) {
		if (word != "RT") {
			return word;
		}
	}
	return "ROMEO:";
}

function streamConnect(token) {
  // Listen to the stream
  const config = {
    url: 'https://api.twitter.com/labs/1/tweets/stream/sample?format=compact',
    auth: {
      bearer: token,
    },
    headers: {
      'User-Agent': 'TwitterDevSampledStreamQuickStartJS',
    },
    timeout: 20000,
  };

  const stream = request.get(config);

  stream.on('data', data => {
    try {
		if (serverAvailable) {
			serverAvailable = false;
			const json = JSON.parse(data);
			const firstWord = getFirstWord(json.data.text);
			console.log(firstWord)
			// console.log(firstWord);
			axios.get(`http://localhost:5000/${firstWord}`)
				// .then(res => console.log(`PIPE: ${res}`))
				.then(res => {
					console.log(res.data)
					T.post('statuses/update', { status: res.data.substring(0, TWEET_LENGTH_LIMIT) }, function(err, data, response) {
						if (err) {
							console.log(err.message)
						}
						console.log(response.statusCode)
					})
					return res;
				})
				.then(() => serverAvailable = true)
		}
    } catch (e) {
      // Keep alive signal received. Do nothing.
    }
  }).on('error', error => {
    if (error.code === 'ETIMEDOUT') {
      stream.emit('timeout');
    }
  });

  return stream;
}

(async () => {
  let token;

  try {
    // Exchange your credentials for a Bearer token
    token = await bearerToken({consumer_key, consumer_secret});
  } catch (e) {
    console.error(`Could not generate a Bearer token. Please check that your credentials are correct and that the Sampled Stream preview is enabled in your Labs dashboard. (${e})`);
    process.exit(-1);
  }

  const stream = streamConnect(token);
  stream.on('timeout', () => {
    // Reconnect on error
    console.warn('A connection error occurred. Reconnecting…');
    streamConnect(token);
  });
})();
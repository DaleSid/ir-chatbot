const request = require('request')

const options = {
  url: 'http://localhost:9999/send',
  json: true,
  body: {
    text: 'usa',
    topics: 'All'
  }
}

request.post(options, (err, res, body) => {
  if (err) {
    return console.log(err)
  }
  console.log(`Status: ${res.statusCode}`)
  console.log(body)
})

const Nightmare = require('nightmare')
const assert = require('assert')

describe('Public Pages', function(){
  //Recommended: 5s locally, 10s to remote server
  this.timeout('30s')

  let nightmare = null
  beforeEach(() => {
    nightmare = new Nightmare()
  })

  describe('/ (Home Page)', () => {
    it('should load without error', done => {
      //Your actual testing urls will be `http://localhost"port/path`
      nightmare.goto('http://localhost:8000/')
      .end()
      .then(function(result) {
        done()
      })
      .catch(done)
    })
  })

})

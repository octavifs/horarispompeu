// RETURN CODES
// 0: All OK
// 1: Missing arguments
// 2: Wrong email / password
// 3: Other error
// 4: Timeout

var page = require('webpage').create();
var system = require('system');
var TIMEOUT = 200000;

if (system.args.length < 4) {
  console.log('Missing arguments:\nphantomjs script.js [email] [password] [calendar_url]');
  phantom.exit(1);
}

var email = system.args[1];
var passwd = system.args[2];
var calendar = system.args[3];
var DEBUG = Boolean(system.args[4]) || false;

page.viewportSize = { width: 800, height: 800 };
page.settings.userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.11 Safari/535.19';
page.open('http://calendar.google.com/', function() {
  page.includeJs('//ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js', function() {
    page.evaluate(function(email, passwd) {
      $('#Email').val(email);
      $('#Passwd').val(passwd);
      $('#PersistentCookie').val('no');
      $('#signIn').click();
    }, email, passwd);
  });

  setTimeout(function() {
    // If the process has not ended in TIMEOUT seconds, exit
    phantom.exit(4);
  }, TIMEOUT);

  page.onLoadFinished = function(status) {
    if (DEBUG) {
      console.log('\n' + page.url + '\n');
      page.render('page.png');
    }
    // See whether the user has logged in or not
    if(/accounts\.google\.com\/ServiceLogin/.test(page.url)) {
      if (DEBUG) page.render('login.png');
      if (page.evaluate(function(email, passwd) {
        return Boolean(document.querySelector("#errormsg_0_Passwd"));
      })) {
        phantom.exit(2);
      }
    }
    // Add the calendar
    if (/www\.google\.com\/calendar\/render/.test(page.url)) {
      var secid;
      for (var i = 0; i < page.cookies.length; i++) {
        if (page.cookies[i].name == 'secid') {
          secid = page.cookies[i].value;
        }
      }
      if (DEBUG) console.log('\n' + secid + '\n');
      var postBody = {
        curl: calendar,
        cimp: true,
        cpub: false,
        secid: secid
      };
      page.includeJs('//ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js', function() {
        var result = page.evaluate(function(postBody) {
          var status = jQuery.ajax({
            url: 'https://www.google.com/calendar/addcalendarfromurl',
            type: 'POST',
            data: postBody,
            async: false,
            dataType: 'text'
          }).status;
          return (status == 200)
        }, postBody);
        if (DEBUG) page.render('calendar.png');
        if (result) {
          phantom.exit(0);
        } else {
          phantom.exit(3);
        }
      });
    }
  };
});

//
// addICSCal.js
//
// Abstract:
//       Awesome CasperJS script, capable of adding ICS calendars to any Google
//       Account programmatically.
//
// Dependencies:
//      - CasperJS 1.1 or higher
//      - PhantomJS 1.9 or higher
//
// It may work in older versions, but it hasn't been tested.
//
// Usage:
//      casperjs addICSCal.js --email=user@domain.some --password=secretpassword --calendar=icsurl
//
// Return codes:
//      0: Calendar added successfully (it may fail though, if the subscription
//         takes longer than the timeout)
//      1: Arguments missing
//      2: Incorrect email or password (could not log in)
//

var casper = require('casper').create({
    pageSettings: {
        loadImages:  false,  // This should enhance the load times a little
        loadPlugins: false
    }
});

var args = require('system').args;

// Get email from arguments
var email;
args.forEach(function(arg) {
    var email_match = arg.match(/(--email=)(.+)/i);
    if (email_match) {
        email = email_match[2];
        return true;
    }
});

// Get password from arguments
var password;
args.forEach(function(arg) {
    var password_match = arg.match(/(--password=)(.+)/);
    if (password_match) {
        password = password_match[2];
        return true;
    }
});

// Get calendar from arguments
var calendar;
args.forEach(function(arg) {
    var calendar_match = arg.match(/(--calendar=)(.+)/);
    if (calendar_match) {
        calendar = calendar_match[2];
        console.log(calendar);
        return true;
    }
});

// Check that we have both email and password.
if (!(email && password && calendar)) {
    var arguments_error = "Error: Missing email, password or calendar URL.\n" +
    "Syntax:\n" +
    "casperjs test.js --email=name@domain.some --password=secretpassword --calendar=http://icsurl";
    casper.die(arguments_error, 1);
}


// Configure the browser window (render size)
//casper.options.viewportSize = {width: 800, height: 600};

// Enter google calendar login page
casper.start('https://calendar.google.com', function() {
    this.fill('#gaia_loginform', {
        'Email': email,
        'Passwd': password,
        'PersistentCookie': 'no'
    }, true);

    // Send login form and redirect to calendar app
    this.evaluate();
});

// Check if password is correct. Otherwise, exit
casper.then(function() {
    var appurl = this.evaluate(function() {
        return document.location.href;
    });
    console.log(appurl);
    if(!appurl.match(/www.google.com\/calendar\/render/i)) {
        this.die("Wrong email or password", 2);
    }
});

// Subscribe to calendar
casper.thenEvaluate(function(calendar) {
    // Open dropdown
    __utils__.mouseEvent("mouseover","#clst_fav_menu");
    __utils__.mouseEvent("mousedown","#clst_fav_menu");
    __utils__.mouseEvent("mouseup","#clst_fav_menu");
    __utils__.mouseEvent("click","#clst_fav_menu");
    // After some time (dropdown does not automatically appear!), continue
    setTimeout(function() {
        // Select correct option (3rd one) [Add by URL]
        document.querySelector("div.goog-menuitem:nth-of-type(3)").className += " itemiwant";
        __utils__.mouseEvent("mousedown", ".itemiwant");
        __utils__.mouseEvent("mouseup", ".itemiwant");
        // Set ICS calendar address in the dialog box
        document.querySelector("input.gc-dialoginput").setAttribute("value", calendar);
        // Press OK an be awesome.
        __utils__.mouseEvent("click", "button.gc-dialogbold");
    }, 900);
}, calendar);

// Stall the execution for some time, so the setTimeout and the ICS addition can
// take place. The values are approximate and if, for whatever reason, the
// delays increase, the calendar will not be correctly added.
// It would be nice if the system could be less error prone.
casper.then(function() {
    this.wait(1500, function() {
        console.log("Done!");
    });
});

// Run the whole casper thing
casper.run();

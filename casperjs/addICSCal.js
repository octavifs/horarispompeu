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
//      3: Unknown error. May be due to calendar duplication
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

// Enter google calendar login page, fill and send form
casper.start('https://calendar.google.com', function() {
    this.fill('#gaia_loginform', {
        'Email': email,
        'Passwd': password,
        'PersistentCookie': 'no'
    }, true);
});

// Check if password is correct. Otherwise, exit
casper.then(function() {
    var appurl = this.evaluate(function() {
        return document.location.href;
    });
    if(!appurl.match(/www.google.com\/calendar\/render/i)) {
        console.log(email + " : " + password);
        this.capture("hola.png");
        this.die("Error: Wrong email or password.", 2);
    }
});

// Subscribe to calendar
casper.then(function() {
    var that = this;
    var timeout = 4000; // This is the timeout if any of the routine fails
    
    // Open dropdown
    this.evaluate(function() {
        __utils__.mouseEvent("mouseover","#clst_fav_menu");
        __utils__.mouseEvent("mousedown","#clst_fav_menu");
        __utils__.mouseEvent("mouseup","#clst_fav_menu");
        __utils__.mouseEvent("click","#clst_fav_menu");
    });

    // Wait for dropdown to open. When it finally does, add the calendar
    this.waitForSelector("div.goog-menuitem:nth-of-type(3)", function() {
        that.evaluate(function(calendar) {
            // Click dropdown button to open dialog box
            document.querySelector("div.goog-menuitem:nth-of-type(3)").className += " itemiwant";
            __utils__.mouseEvent("mousedown", ".itemiwant");
            __utils__.mouseEvent("mouseup", ".itemiwant");
            // Set ICS calendar address in the dialog box
            document.querySelector("input.gc-dialoginput").setAttribute("value", calendar);
            // Press OK an be awesome.
            __utils__.mouseEvent("click", "button.gc-dialogbold");
        }, calendar);
    }, unknownError, timeout);

    // Wait until calendar is added to the "Other Calendars" bar
    this.waitForSelectorTextChange("#calendars_fav", null, unknownError, timeout);

    function unknownError() {
        that.die("Error: Unknown error while adding calendar. Calendar already added?", 3);
    }
});

// Cleanup
casper.then(function() {
    console.log("Done!");
});

// Run the whole casper thing
casper.run();

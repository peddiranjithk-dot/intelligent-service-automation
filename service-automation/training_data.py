"""Seed training data: (request text, intent). Add more rows to improve accuracy."""
TRAINING = [
    # password_reset
    ("I forgot my password and cannot log in", "password_reset"),
    ("Please reset my password", "password_reset"),
    ("My account is locked after too many attempts", "password_reset"),
    ("Cannot sign in, password expired", "password_reset"),
    ("Need to unlock my account", "password_reset"),
    # vpn_issue
    ("VPN keeps disconnecting when working from home", "vpn_issue"),
    ("Unable to connect to the VPN", "vpn_issue"),
    ("VPN client shows authentication failed", "vpn_issue"),
    ("Remote access not working from home", "vpn_issue"),
    # software_install
    ("Please install Visual Studio Code on my laptop", "software_install"),
    ("I need Adobe Acrobat installed", "software_install"),
    ("Request to install new software license for Zoom", "software_install"),
    ("Can you install Python on my machine", "software_install"),
    # hardware_issue
    ("My laptop screen is broken", "hardware_issue"),
    ("Keyboard is not working", "hardware_issue"),
    ("Laptop battery drains very fast", "hardware_issue"),
    ("Monitor flickers and goes black", "hardware_issue"),
    ("Mouse stopped responding, need a replacement", "hardware_issue"),
    # access_request
    ("Need access to the finance shared folder", "access_request"),
    ("Please grant me permission to the CRM system", "access_request"),
    ("Request access to the production dashboard", "access_request"),
    ("New joiner needs access to email and Slack", "access_request"),
    # network_issue
    ("Wifi is very slow in the office", "network_issue"),
    ("No internet connection on my desk", "network_issue"),
    ("Network drops every few minutes", "network_issue"),
    ("Cannot reach internal websites, DNS error", "network_issue"),
    # application_error
    ("The app crashes when I click export", "application_error"),
    ("Getting a 500 error on the billing page", "application_error"),
    ("Application throws an exception on login page", "application_error"),
    ("Report generation fails with an error", "application_error"),
    # security_incident
    ("I received a suspicious phishing email", "security_incident"),
    ("Possible malware on my computer", "security_incident"),
    ("Unauthorized login attempt on my account", "security_incident"),
    ("I think my laptop was hacked", "security_incident"),
]

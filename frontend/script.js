var apiBaseUrl = "http://0.0.0.0:5000/";

function onSuccess(response) {
    let cookieHeader = response.headers.get('Set-Cookie'); // or if decided other header name
    document.cookie = cookieHeader;
}

function login() {
    const email = document.forms.loginForm["email"].value;
    const password = document.forms.loginForm["password"].value;
    const url = apiBaseUrl + "auth/login"
    const payload = {
        "email": email,
        "password": password
    }
    const param = {
        headers: {
            "Content-Type":"application/json"        
        },
        body: JSON.stringify(payload),
        method: "POST",
        credentials: 'include'
    }

    fetch(url, param)
        .then(response => response.json())
        .then(data => {
            if(data["success"] == true) {
                console.log(data["status"])
                window.localStorage.setItem('firstName', data["firstName"]);
                window.location.replace("./dashboard.html")
            }
        })
        // .then(onSuccess)
        .catch(() => {
            console.log("Error");
        });
}


function redirectIfLoggedIn() {
    url = apiBaseUrl + "auth/isLoggedIn"
    const param = {
        headers: {
            "Content-Type":"application/json"        
        },
        method: "GET",
        credentials: 'include'
    }

    fetch(url, param)
        .then(response => response.json())
        .then(data => {
            if(data["success"] == true) {
                window.location.replace("./dashboard.html")
            }
        })
        .catch(() => {
            console.log("Error");
        });
}


// function getCookie(name) {
//     if (!document.cookie) {
//         return null;
//     }

//     const xsrfCookies = document.cookie.split(';')
//         .map(c => {
//             console.log(c)
//             c.trim()
//         })
//         .filter(c => c.startsWith(name + '='));

//     if (xsrfCookies.length === 0) {
//         return null;
//     }
//     return decodeURIComponent(xsrfCookies[0].split('=')[1]);
// }

// TODO: Figure out how to send the CSRF token in request
function logout() {
    const url = apiBaseUrl + "auth/logout"
    // const csrfToken = getCookie("csrf_access_token") // TODO: Figure out why this isnt working
    const param = {
        headers: {
            "Content-Type":"application/json",
            // "X-CSRF-TOKEN": csrfToken 
        },
        method: "POST",
        credentials: 'include'
    }

    fetch(url, param)
        .then(response => response.json())
        .then(data => {
            if(data["success"] == true) {
                console.log("success")
            }   
        })
        .catch(() => {
            console.log("Error");
        });

    window.location.replace("./login.html")
}


function loadDashboard() {
    const url = apiBaseUrl + "loan"
   // const csrfToken = getCookie("csrf_access_token") // TODO: Figure out why this isnt working
    const param = {
        headers: {
            "Content-Type":"application/json",
            // "X-CSRF-TOKEN": csrfToken 
        },
        method: "GET",
        credentials: 'include'
    }

    fetch(url, param)
        .then(response => response.json())
        .then(data => {
            if(data["success"] == true) {
                setTimeOfDay()
                document.getElementsByClassName("protected")[0].style.visibility = "visible"
                nameBoxs = document.getElementsByClassName("firstName")
                for (var i = 0; i < nameBoxs.length; i++) {
                    nameBoxs[i].innerText = window.localStorage.getItem("firstName")
                }

                // Setting summary info
                overallSummary = data["overallSummary"]
                totalLoaned = -overallSummary["totalLoanedAmount"]
                currentInterestPaid = -overallSummary["totalCurrentInterestPaid"]
                projectedInterestPaid = -overallSummary["totalProjectedInterestPaid"]

                if (currentInterestPaid < 0 || (totalLoaned < 0 && currentInterestPaid == 0)) {
                    document.getElementById("earningsTitle").innerText = "Interest Paid"
                    currentInterestPaid = -currentInterestPaid
                }

                if (totalLoaned < 0) {
                    document.getElementById("loanedTitle").innerText = "Borrowed"
                    totalLoaned = -totalLoaned
                }

                if (projectedInterestPaid < 0) {
                    document.getElementById("projectedEarningsTitle").innerText = "Interest Paid"
                    projectedInterestPaid = -projectedInterestPaid
                }

                document.getElementById("loanedValue").innerText = `$${totalLoaned.toFixed(2)}`
                document.getElementById("earningsValue").innerText = `$${currentInterestPaid.toFixed(2)}`
                document.getElementById("projectedEarningsValue").innerText = `$${projectedInterestPaid.toFixed(2)}`

                // Creating card for each loan
                loanDetails = data["loanDetails"]
                for (var i = 0; i < loanDetails.length; i++) {
                    loan = loanDetails[i]
                    var card = loanCard(loan["loanName"], loan["loanValue"], loan["interestRate"] * 100, loan["loaner"], loan["withPerson"], loan["amountRemaining"])
                    console.log(card)
                    document.getElementById("loans").insertAdjacentHTML('beforeend', card)
                }

                // Setting min loan date for new loans to today
                var today = new Date();
                var dd = today.getDate();
                var mm = today.getMonth() + 1; // January is 0
                var yyyy = today.getFullYear();
                if (dd < 10) {
                    dd = '0' + dd
                } 
                if (mm < 10) {
                    mm = '0' + mm
                } 
                today = yyyy + '-' + mm + '-' + dd;
                document.getElementById("startDateField").setAttribute("min", today);


            } else {
                window.location.replace("./login.html")
                // alert("error")
            }
        })
        .catch(err => {
            console.log(err);
            window.location.replace("./login.html")
        });
    return false
}

function setTimeOfDay() {
    const today = new Date();
    const h = today.getHours();
    var TOD = "evening"
    if (h >= 5 && h < 12) {
        TOD = "morning"
    } else if (h >= 12 && h <= 17) {
        TOD = "afternoon"
    }
    document.getElementById('TOD').innerHTML = TOD;
}

function remainingDaysInMonth() {
    var date = new Date();
    var time = new Date(date.getTime());
    time.setMonth(date.getMonth() + 1);
    time.setDate(0);
    var days = time.getDate() > date.getDate() ? time.getDate() - date.getDate() : 0;
    return days
}

function loanCard(loanName, loanValue, interestRate, loaner, withPerson, amountOwed) {
    console.log(loanName)
    percentPaid = (1 - amountOwed / loanValue) * 100
    daysToNextPayment = remainingDaysInMonth()
    loanTypeTag = loaner ? `Lending to ${withPerson}` : `Borrowing from ${withPerson}`
    card = `<div class="loanOverview">
        <div class="loanLeft">
                <div class="loanTop">
                    <div class="loanName">${loanName}</div>
                    <div class="loanValue">(out of $${loanValue.toFixed(0)})</div>
                    <div class="progressBar">
                        <div class="progressBarInfill" style="height:100%; width:${percentPaid.toFixed(1)}"></div>
                        <div class="progressBarValue">${percentPaid}%</div>
                    </div>

                </div>

                <div class="loanBottom">
                    <div class="interestRateTitle">Interest Rate</div>
                    <div class="interestRateValue">${interestRate.toFixed(1)}%</div>
                </div>

        </div>

        <div class="loanRight">
            <div class="loanTop">
                <div class="tag"><span class="loanType">${loanTypeTag}</span></div>
                <div class="tag"><span class="nextPayment">Next Payment in ${daysToNextPayment} days</span></div>
            </div>

            <div class="loanBottom">
                <div class="amountOwedTitle">Amount owed</div>
                <div class="amountOwedValue">$${amountOwed.toFixed(2)}</div>
            </div>
        </div>
    </div>`
    return card
}

function toggleNewLoanModal() {
    newLoanModal = document.getElementById("newLoanModal")
    console.log(newLoanModal.style.display)
    if (newLoanModal.style.display != "block") {
        newLoanModal.style.display = "block"
    } else {
        newLoanModal.style.display = "none"
    }
}

function proposeLoan() {
    form = document.forms.loanForm
    const loaner = form["loanerBorrowerInput"].value     == "loaning" ? true : false;

    const otherUserEmail = form["userEmail"].value
    const loanName = form["loanName"].value
    const loanValue = form["loanValue"].value
    const interestRate = form["interestRate"].value
    const startDate = form["startDate"].value
    const termMonths = form["term"].value

    const url = apiBaseUrl + "loan"
    const payload = {
        "loanName": loanName,
        "loaner": loaner,
        "otherUserEmail": otherUserEmail,
        "amount": loanValue,
        "interestRate": interestRate,
        "termMonths": termMonths,
        "startDate": startDate
    }
    const param = {
        headers: {
            "Content-Type":"application/json"        
        },
        body: JSON.stringify(payload),
        method: "POST",
        credentials: 'include'
    }

    fetch(url, param)
        .then(response => response.json())
        .then(data => {
            if (data["success"]) {
                // Refresh window to show newly created loan
                window.location.replace("./dashboard.html")
            } else if (data["msg"] == "Invalid email") { // Other user does not exist
                document.getElementById("otherUserEmail").setCustomValidity("A user with this adress has not be found")
                document.getElementById("otherUserEmail").reportValidity()
            } else if (data["msg"] == "Name taken") {
                document.getElementById("loanNickname").setCustomValidity("You already have a loan with this nickname")
                document.getElementById("loanNickname").reportValidity()
            } else if (data["msg"] == "Self loan") {
                document.getElementById("otherUserEmail").setCustomValidity("You cannot create a self loan")
                document.getElementById("otherUserEmail").reportValidity()
            } else {
                alert("An internal server error may have stopped the creaton of the loan")
            }
        })
        .catch(() => {
            console.log("Error");
            alert("Error")
        });

    return false
}

// Clear previously custom set validities 
function clearManualValidations() {
    document.getElementById("loanNickname").setCustomValidity('')
    document.getElementById("otherUserEmail").setCustomValidity('')
}

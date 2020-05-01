var apiBaseUrl = "http://0.0.0.0:5000/";

function onSuccess(response) {
    let cookieHeader = response.headers.get('Set-Cookie'); // or if decided other header name
    alert(cookieHeader)
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
            console.log("gere")
        })
        .then(onSuccess)
        .catch(() => {
            // Incorrect username or password

            console.log("Error");
        });

    return false
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
     // const csrfToken = getCookie("csrf_access_token")
    document.cookie='abc=123';
    alert(!document.cookie)
    // const csrfToken = getCookie("csrf_access_token")
    const csrfToken = "123"

    alert(document.cookie)
    const param = {
        headers: {
            "Content-Type":"application/json",
            "X-CSRF-TOKEN": csrfToken 
        },
        // method: "POST",
        credentials: 'include'
    }

    fetch(url, param)
        .then(response => response.json())
        .then(data => {
            console.log("gere")
        })
        .then(onSuccess)
        .catch(() => {
            // Incorrect username or password

            console.log("Error");
        });

    return false
}


function test() {
    const url = apiBaseUrl + "test"
    const param = {
        headers: {
            "Content-Type":"application/json"        
        },
        method: "PUT",
        credentials: 'include'
    }

    fetch(url, param)
        .then(response => response.json())
        .then(data => {
            console.log("gere")
        })
        .catch(() => {
            // Incorrect username or password

            console.log("Error");
        });

    return false
}